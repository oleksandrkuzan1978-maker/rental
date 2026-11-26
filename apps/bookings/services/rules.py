"""Проверка доступности объявления и условий проживания."""

from apps.bookings.models import Booking
from apps.listings.utils.choices import ListingStatus

from ..utils.choices import DecisionReason, Status
from apps.users.models import User

def listing_is_available(listing):
    """Проверить объявление и активность его владельца."""
    return (
        listing.status == ListingStatus.PUBLISHED
        and listing.deleted_at is None
        and listing.price_per_night is not None
        and listing.max_guests is not None
        and User.objects.filter(
            pk=listing.user_id,
            is_active=True,
            deleted_at__isnull=True,
        ).exists()
    )


def rejection_reason(listing, booking):
    """Найти причину отказа под блокировкой объявления."""
    # rejection_reason() возвращает код причины либо пустую строку, если препятствий нет.
    if not listing_is_available(listing):
        return DecisionReason.LISTING_UNAVAILABLE

    if booking.guests_count > listing.max_guests:
        return DecisionReason.CAPACITY_EXCEEDED

    if booking.has_pets and not listing.pets_allowed:
        return DecisionReason.PETS_NOT_ALLOWED

    # Только подтверждённая бронь занимает даты.
    occupied = Booking.objects.select_for_update().filter(
        listing_id=listing.pk,
        status=Status.CONFIRMED,
        start_date__lt=booking.end_date,
        end_date__gt=booking.start_date,
    ).exclude(pk=booking.pk).exists()

    if occupied:
        return DecisionReason.DATES_UNAVAILABLE
    return ""





