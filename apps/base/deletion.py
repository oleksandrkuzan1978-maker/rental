"""Проверки прав и бизнес-правил удаления объектов проекта."""

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.bookings.models import Booking
from apps.bookings.utils.choices import DecisionReason, Status
from apps.listings.models import Listing
from apps.listings.utils.choices import ListingStatus
from apps.reviews.models import Review
from apps.users.models import User


def require_superuser(actor):
    """Проверить актуальные права на физическое удаление."""
    if (
        actor is None
        or not actor.is_authenticated
        or not User.objects.filter(
            pk=actor.pk,
            is_active=True,
            is_superuser=True,
            deleted_at__isnull=True,
        ).exists()
    ):
        raise PermissionDenied(
            _("Only a superuser can permanently delete records.")
        )


def lock_active_user(*, user):
    """Заблокировать аккаунт внутри транзакции и проверить его доступ."""
    if user is None or not user.is_authenticated:
        raise PermissionDenied(_("You must be logged in."))

    try:
        return User.objects.select_for_update().get(
            pk=user.pk,
            is_active=True,
            deleted_at__isnull=True,
        )
    except User.DoesNotExist:
        raise PermissionDenied(_("The account is unavailable.")) from None


def _mark_deleted(obj, *, now):
    """Записать дату удаления после выполнения бизнес-проверок."""
    if obj.deleted_at is not None:
        return

    obj.deleted_at = now
    fields = ["deleted_at", "updated_at"]

    if isinstance(obj, User):
        obj.is_active = False
        fields.append("is_active")

    elif isinstance(obj, Listing):
        obj.status = ListingStatus.PAUSED
        fields.append("status")

    obj.save(update_fields=fields)


def _cancel_booking(booking, *, reason, now):
    """Отменить ожидающую заявку перед удалением."""
    if booking.status != Status.PENDING:
        return

    booking.status = Status.CANCELLED
    booking.decision_reason = reason
    booking.decided_at = now
    booking.review_deadline = None

    booking.save(update_fields=[
        "status",
        "decision_reason",
        "decided_at",
        "review_deadline",
        "updated_at",
    ])

def _delete_account(user, *, now):
    """Удалить аккаунт и собственные записи при отсутствии CONFIRMED."""
    owned_ids = set(
        Listing.objects.filter(user_id=user.pk)
        .values_list("pk", flat=True)
    )

    tenant_listing_ids = set(
        Booking.objects.filter(user_id=user.pk)
        .values_list("listing_id", flat=True)
    )

    # Сначала блокируем объявления в едином порядке.
    listings = list(
        Listing.objects.select_for_update()
        .filter(pk__in=owned_ids | tenant_listing_ids)
        .order_by("pk")
    )

    # Затем блокируем собственные брони и брони своих объявлений.
    bookings = list(
        Booking.objects.select_for_update()
        .filter(
            Q(user_id=user.pk)
            | Q(listing_id__in=owned_ids)
        )
        .order_by("pk")
    )

    if any(booking.status == Status.CONFIRMED for booking in bookings):
        raise ValidationError(
            _(
                "You cannot delete your account: you or your "
                "listings have confirmed bookings."
            )
        )

    for booking in bookings:
        _cancel_booking(
            booking,
            reason=DecisionReason.ACCOUNT_DELETED,
            now=now,
        )

        # Чужие заявки сохраняем в истории их арендаторов.
        if booking.user_id == user.pk:
            _mark_deleted(booking, now=now)

    reviews = (
        Review.objects.select_for_update()
        .filter(booking__user_id=user.pk)
        .order_by("pk")
    )

    for review in reviews:
        _mark_deleted(review, now=now)

    for listing in listings:
        if listing.user_id == user.pk:
            _mark_deleted(listing, now=now)

    _mark_deleted(user, now=now)


@transaction.atomic
def soft_delete_object(*, obj, actor):
    """Удалить собственный объект с проверкой прав и обязательств."""
    actor = lock_active_user(user=actor)

    if isinstance(obj, User):
        if obj.pk != actor.pk:
            raise PermissionDenied(_("You can only delete your own account."))

        _delete_account(actor, now=timezone.now())

    elif isinstance(obj, Listing):
        listing = Listing.objects.select_for_update().get(pk=obj.pk)

        if listing.user_id != actor.pk:
            raise PermissionDenied(_("This listing belongs to another user."))

        if listing.deleted_at is not None:
            return 0, {}

        if Booking.objects.filter(
            listing_id=listing.pk,
            status=Status.CONFIRMED,
        ).exists():
            raise ValidationError(
                _("You cannot delete a listing with confirmed bookings.")
            )

        now = timezone.now()

        waiting = (
            Booking.objects.select_for_update()
            .filter(listing_id=listing.pk, status=Status.PENDING)
            .order_by("pk")
        )

        for booking in waiting:
            _cancel_booking(
                booking,
                reason=DecisionReason.LISTING_UNAVAILABLE,
                now=now,
            )

        _mark_deleted(listing, now=now)

    elif isinstance(obj, Booking):
        # Локальный импорт предотвращает циклический импорт сервисов.
        from apps.bookings.services.state import lock_booking

        _listing, booking = lock_booking(obj.pk)

        if booking.user_id != actor.pk:
            raise PermissionDenied(_("This booking belongs to another user."))

        if booking.deleted_at is not None:
            return 0, {}

        allowed = {
            Status.PENDING,
            Status.REJECTED,
            Status.CANCELLED,
            Status.COMPLETED,
        }

        if booking.status not in allowed:
            raise ValidationError(
                _("You cannot soft-delete a confirmed booking.")
            )

        now = timezone.now()

        _cancel_booking(
            booking,
            reason=DecisionReason.USER_CANCELLED,
            now=now,
        )
        _mark_deleted(booking, now=now)

    elif isinstance(obj, Review):
        review = Review.objects.select_for_update().get(pk=obj.pk)

        if review.booking.user_id != actor.pk:
            raise PermissionDenied(_("This review belongs to another user."))

        if review.deleted_at is not None:
            return 0, {}

        _mark_deleted(review, now=timezone.now())

    else:
        raise TypeError(_("Soft deletion is not supported for this model."))

    # Возвращаем число удалённых корневых объектов.
    return 1, {obj._meta.label: 1}
