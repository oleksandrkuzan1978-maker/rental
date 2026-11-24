"""Создание заявки с автоматическим определением результата."""

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from apps.bookings.models import Booking
from apps.listings.models import Listing

from ..utils.choices import DecisionReason, Status
from ..utils.variables import OWNER_REVIEW_TIMEOUT
from .dates import validate_dates
from .rules import listing_is_available, rejection_reason
from .state import reject_overlapping_requests

#В этом файле - сценарий подачи заявки.
# Детали расчёта календарных ограничений
# и проверки пересечений находятся в соответствующих модулях.
@transaction.atomic
def create_booking(
    *,
    user,
    listing_id,
    start_date,
    end_date,
    description="",
    adults=1,
    children=0,
    has_pets=False,
    requires_owner_approval=False,
    show_phone=True,
    show_email=True,
):
    """Создать заявку и определить результат до первого сохранения."""
    if not user.is_authenticated or not user.is_active:
        raise PermissionDenied()

    validate_dates(start_date, end_date)

    if requires_owner_approval and not description.strip():
        raise ValidationError({
            "description": "Опишите особые условия для согласования.",
        })

    try:
        # Все решения по одному объявлению выполняются по очереди.
        listing = Listing.objects.select_for_update().get(
            pk=listing_id,
        )
    except Listing.DoesNotExist:
        raise ValidationError({
            "listing": "Объявление недоступно.",
        }) from None

    if not listing_is_available(listing):
        raise ValidationError({
            "listing": "Объявление недоступно или не настроено.",
        })

    booking = Booking(
        user=user,
        listing=listing,
        start_date=start_date,
        end_date=end_date,
        total_price=(
            listing.price_per_night * (end_date - start_date).days
        ),
        description=description,
        adults=adults,
        children=children,
        has_pets=has_pets,
        requires_owner_approval=requires_owner_approval,
        show_phone=show_phone,
        show_email=show_email,
    )

    booking.full_clean()

    reason = rejection_reason(listing, booking)
    now = timezone.now()

    # Здесь определяется состояние до первого INSERT в базу.
    if reason:
        booking.status = Status.REJECTED
        booking.decision_reason = reason
        booking.decided_at = now

    elif requires_owner_approval or not listing.instant_booking_enabled:
        booking.status = Status.PENDING
        booking.review_deadline = now + OWNER_REVIEW_TIMEOUT

    else:
        booking.status = Status.CONFIRMED
        booking.decision_reason = DecisionReason.AUTO_CONFIRMED
        booking.decided_at = now

    booking.save(force_insert=True)

    if booking.status == Status.CONFIRMED:
        reject_overlapping_requests(booking, now=now)

    return booking