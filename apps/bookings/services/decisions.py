"""Решение владельца и автоматический отказ по истечении срока."""

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ..utils.choices import DecisionReason, Status
from .rules import rejection_reason
from .state import (
    lock_booking,
    reject_overlapping_requests,
    set_decision,
)
from apps.base.services.access import lock_active_user

# Здесь собраны операции над уже созданной заявкой.
# Обработка дедлайна использует те же блокировки
# и способ сохранения решения, что и действие владельца.
@transaction.atomic
def decide_booking(
    *,
    user,
    booking_id,
    approve,
    listing_id=None,
):
    """Применить решение владельца с проверкой срока и доступности."""

    user = lock_active_user(user=user)

    listing, booking = lock_booking(booking_id, listing_id)

    if listing.user_id != user.pk:
        raise PermissionDenied()

    if booking.deleted_at is not None:
        raise ValidationError(_("A deleted request cannot be considered."))

    expected_status = (
        Status.CONFIRMED if approve else Status.REJECTED
    )

    # Повторное нажатие той же кнопки возвращает существующий результат.
    if booking.status == expected_status:
        return booking

    if booking.status != Status.PENDING:
        raise ValidationError(
            _("The request has already been processed. Please update its status.")
        )

    now = timezone.now()

    if (
        booking.review_deadline is None
        or booking.review_deadline <= now
    ):
        return set_decision(
            booking,
            status=Status.REJECTED,
            reason=DecisionReason.REVIEW_TIMEOUT,
            now=now,
        )

    if not approve:
        return set_decision(
            booking,
            status=Status.REJECTED,
            reason=DecisionReason.OWNER_REJECTED,
            now=now,
        )

    # Правила объявления могли измениться за время ожидания.
    reason = rejection_reason(listing, booking)

    if booking.start_date < timezone.localdate():
        reason = DecisionReason.REVIEW_TIMEOUT

    if reason:
        return set_decision(
            booking,
            status=Status.REJECTED,
            reason=reason,
            now=now,
        )

    set_decision(
        booking,
        status=Status.CONFIRMED,
        reason=DecisionReason.OWNER_CONFIRMED,
        now=now,
    )

    reject_overlapping_requests(booking, now=now)
    return booking


def confirm_booking(*, user, listing_id, booking_id):
    """Подтвердить бронь от имени явно переданного владельца."""
    return decide_booking(
        user=user,
        listing_id=listing_id,
        booking_id=booking_id,
        approve=True,
    )


@transaction.atomic
def expire_booking(*, booking_id):
    """Отклонить просроченную заявку после проверки под блокировкой."""
    _, booking = lock_booking(booking_id)
    now = timezone.now()

    if (
        booking.status == Status.PENDING
        and booking.review_deadline is not None
        and booking.review_deadline <= now
    ):
        set_decision(
            booking,
            status=Status.REJECTED,
            reason=DecisionReason.REVIEW_TIMEOUT,
            now=now,
        )

    return booking

@transaction.atomic
def complete_booking(*, booking_id, user=None):
    """Завершить бронь автоматически по сроку или вручную владельцем.

    При переданном user проверить владельца и разрешить досрочное
    завершение. Без user завершать только после времени выезда.
    """
    if user is not None:
        user = lock_active_user(user=user)

    listing, booking = lock_booking(booking_id)

    if user is not None and listing.user_id != user.pk:
        raise PermissionDenied(
            _("Only the listing owner can complete this booking.")
        )

    # Повторное завершение не меняет дату принятого решения.
    if booking.status == Status.COMPLETED:
        return booking

    if booking.status != Status.CONFIRMED:
        if user is not None:
            raise ValidationError(
                _("Only confirmed bookings can be completed.")
            )

        return booking

    now = timezone.now()

    if user is None:
        local_now = timezone.localtime(
            now,
            timezone.get_default_timezone(),
        )

        if (
            booking.end_date,
            listing.check_out_time,
        ) > (
            local_now.date(),
            local_now.time(),
        ):
            return booking

    booking.status = Status.COMPLETED
    booking.decided_at = now

    booking.save(update_fields=[
        "status",
        "decided_at",
        "updated_at",
    ])

    return booking