"""Общая проверка и сохранение результата подачи заявки."""
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone

from ..utils.choices import DecisionReason, Status
from ..utils.variables import OWNER_REVIEW_TIMEOUT
from .dates import validate_dates
from .rules import listing_is_available, rejection_reason
from .state import reject_overlapping_requests


def save_booking_result(listing, booking):
    """Вызвать внутри транзакции после блокировки объявления."""
    validate_dates(booking.start_date, booking.end_date)

    if (
        booking.requires_owner_approval
        and not booking.description.strip()
    ):
        raise ValidationError({
            "description": _("Describe the special conditions that require approval."),
        })

    if not listing_is_available(listing):
        raise ValidationError({
            "listing": _("The listing is unavailable or has not been configured."),
        })

    booking.total_price = (
        listing.price_per_night
        * (booking.end_date - booking.start_date).days
    )

    booking.full_clean()

    reason = rejection_reason(listing, booking)
    now = timezone.now()

    # сохранение прежнего дедлайна
    previous_deadline = (
        booking.review_deadline
        if booking.status == Status.PENDING
        else None
    )
    booking.decision_reason = reason
    booking.decided_at = None
    booking.review_deadline = None

    if reason:
        booking.status = Status.REJECTED
        booking.decided_at = now

    elif (
        booking.requires_owner_approval
        or not listing.instant_booking_enabled
    ):
        booking.status = Status.PENDING
        booking.review_deadline = (
            previous_deadline or now + OWNER_REVIEW_TIMEOUT
        )

    else:
        booking.status = Status.CONFIRMED
        booking.decision_reason = DecisionReason.AUTO_CONFIRMED
        booking.decided_at = now

    booking.save()

    if booking.status == Status.CONFIRMED:
        reject_overlapping_requests(booking, now=now)

    return booking
