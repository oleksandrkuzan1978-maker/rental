"""Восстановление мягко удалённых записей."""

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.bookings.models import Booking
from apps.bookings.utils.choices import Status
from apps.listings.models import Listing, ListingFile
from apps.listings.utils.choices import ListingStatus
from apps.listings.utils.variables import MAX_FILES_PER_LISTING
from apps.reviews.models import Review
from apps.users.models import User

from .access import lock_active_user, require_superuser


def _check_restore_permission(*, obj, owner_id, actor):
    """Allow owners to restore records unless deletion requires a superuser."""
    if actor.is_superuser:
        return
    if owner_id != actor.pk:
        raise PermissionDenied(_("You can only restore your own records."))
    if obj.restore_requires_superuser:
        raise PermissionDenied(_("Only a superuser can restore this record."))


def _check_file(attachment):
    """Проверить наличие восстанавливаемого файла в хранилище."""
    if (
        not attachment.file.name
        or not attachment.file.storage.exists(attachment.file.name)
    ):
        raise ValidationError(
            _("The file is missing from storage.")
        )


@transaction.atomic
def restore_object(*, obj, actor, warnings=None):
    """Восстановить запись с проверкой прав и связанных объектов.

    Аккаунт восстанавливает суперпользователь, остальные записи —
    их владелец или суперпользователь с учётом запрета восстановления.
    Вернуть актуальный объект из базы данных.
    """
    actor = lock_active_user(user=actor)

    fields = ["deleted_at", "updated_at"]
    now = timezone.now()

    if isinstance(obj, User):
        require_superuser(actor)

        current = User.all_objects.select_for_update().get(pk=obj.pk)

        if current.deleted_at is None:
            return current

        current.is_active = True
        fields.append("is_active")

    elif isinstance(obj, Listing):
        current = Listing.all_objects.select_for_update().get(pk=obj.pk)

        _check_restore_permission(
            obj=current, owner_id=current.user_id, actor=actor,
        )

        if current.deleted_at is None:
            return current

        # Выбираем вложения, удалённые вместе с объявлением.
        attachments_query = (
            ListingFile.deleted_objects.select_for_update()
            .filter(listing=current)
            .filter(deleted_at=current.deleted_at)
            .order_by("pk")
        )

        if not actor.is_superuser:
            attachments_query = attachments_query.filter(
                restore_requires_superuser=False,
            )

        attachments = list(attachments_query)
        available_ids = []
        missing_files = []

        for attachment in attachments:
            if (
                    attachment.file.name
                    and attachment.file.storage.exists(attachment.file.name)
            ):
                available_ids.append(attachment.pk)
            else:
                missing_files.append({
                    "id": str(attachment.pk),
                    "title": attachment.title,
                })

        if (
                ListingFile.objects.filter(listing=current).count()
                + len(available_ids)
                > MAX_FILES_PER_LISTING
        ):
            raise ValidationError(
                _("The attachment limit has been reached.")
            )

        ListingFile.deleted_objects.filter(
            listing=current,
            pk__in=available_ids,
        ).update(
            deleted_at=None,
            restore_requires_superuser=False,
            updated_at=now,
        )

        if warnings is not None:
            warnings.extend(missing_files)

        current.status = ListingStatus.PAUSED
        fields.append("status")

    elif isinstance(obj, ListingFile):
        reference = ListingFile.all_objects.only("listing_id").get(
            pk=obj.pk,
        )

        listing = Listing.all_objects.select_for_update().get(
            pk=reference.listing_id,
        )
        current = ListingFile.all_objects.select_for_update().get(
            pk=obj.pk,
            listing_id=listing.pk,
        )

        _check_restore_permission(
            obj=current, owner_id=listing.user_id, actor=actor,
        )

        if current.deleted_at is None:
            return current

        if listing.deleted_at is not None:
            raise ValidationError(
                _("Restore the listing before restoring its files.")
            )

        if ListingFile.objects.filter(listing=listing).count() >= MAX_FILES_PER_LISTING:
            raise ValidationError(
                _("The attachment limit has been reached.")
            )

        _check_file(current)

    elif isinstance(obj, Booking):
        # Локальный импорт предотвращает циклическую зависимость.
        from apps.bookings.services.state import lock_booking

        _listing, current = lock_booking(obj.pk)

        _check_restore_permission(
            obj=current, owner_id=current.user_id, actor=actor,
        )

        if current.deleted_at is None:
            return current

        if current.status not in (
            Status.REJECTED,
            Status.CANCELLED,
            Status.COMPLETED,
        ):
            raise ValidationError(
                _("This booking cannot be restored to history.")
            )

    elif isinstance(obj, Review):
        reference = Review.all_objects.only("booking_id").get(
            pk=obj.pk,
        )

        booking = Booking.all_objects.select_for_update().get(
            pk=reference.booking_id,
        )
        current = Review.all_objects.select_for_update().get(
            pk=obj.pk,
            booking_id=booking.pk,
        )

        _check_restore_permission(
            obj=current, owner_id=booking.user_id, actor=actor,
        )

        if current.deleted_at is None:
            return current

        if booking.deleted_at is not None:
            raise ValidationError(
                _("Restore the booking before restoring its review.")
            )

        if booking.status != Status.COMPLETED:
            raise ValidationError(
                _("Reviews can only be restored for completed bookings.")
            )

    else:
        raise TypeError(
            _("Restoration is not supported for this model.")
        )

    current.deleted_at = None
    current.restore_requires_superuser = False
    fields.append("restore_requires_superuser")
    current.save(update_fields=fields)

    return current