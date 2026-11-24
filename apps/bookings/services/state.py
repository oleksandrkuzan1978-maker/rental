"""Блокировки и сохранение результатов решений по заявкам."""
from apps.bookings.models import Booking
from apps.listings.models import Listing

from ..utils.choices import DecisionReason, Status


def set_decision(booking, *, status, reason, now):
    """Сохранить решение и вызвать сигнал уведомления."""
    # set_decision() одинаково сохраняет результат и время.
    booking.status = status
    booking.decision_reason = reason
    booking.decided_at = now

    booking.save(update_fields=['status', 'decision_reason', 'decided_at', 'updated_at'])

    return booking


def reject_overlapping_requests(booking, *, now):
    """Отклонить ожидающие заявки на даты подтверждённой брони."""
    # reject_overlapping_requests() освобождает систему
    # от конфликтующих ожидающих заявок после подтверждения.
    waiting = (Booking.objects.select_for_update()
               .filter(listing_id=booking.listing_id,
                        status=Status.PENDING,
                        start_date__lt=booking.end_date,
                        end_date__gt=booking.start_date,)
               .exclude(pk=booking.pk).order_by("pk"))

    for other in waiting:
        reason = DecisionReason.DATES_UNAVAILABLE

        if (
                other.review_deadline is not None
                and other.review_deadline <= now
        ):
            reason = DecisionReason.REVIEW_TIMEOUT

        set_decision(
            other,
            status=Status.REJECTED,
            reason=reason,
            now=now,
        )


def lock_booking(booking_id, listing_id=None):
    """Заблокировать объявление, затем бронь в едином порядке."""
    # lock_booking() обеспечивает единый порядок блокировок.
    reference = Booking.objects.only("listing_id").get(pk=booking_id)

    if (listing_id is not None
            and reference.listing_id != listing_id):
        raise Booking.DoesNotExist()

    listing = Listing.objects.select_for_update().get(pk=reference.listing_id)

    booking = Booking.objects.select_for_update().get(pk=booking_id, listing_id=listing.pk,)

    return listing, booking




