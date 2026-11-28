"""Редактирование отклонённых заявок."""
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from ..utils.choices import Status
from ..utils.variables import (
    EDITABLE_BOOKING_FIELDS,
    MAX_BOOKING_EDITS,
)
from .state import lock_booking
from .workflow import save_booking_result
from apps.base.services.access import lock_active_user

@transaction.atomic
def update_booking(*, user, booking_id, changes):

    user = lock_active_user(user=user)

    listing, booking = lock_booking(booking_id)

    if booking.user_id != user.pk:
        raise PermissionDenied()

    if booking.deleted_at is not None:
        raise ValidationError(_("Deleted booking cannot be modified"))

    if booking.status == Status.COMPLETED:
        raise ValidationError(
            _("Completed bookings cannot be modified.")
        )

    if booking.status not in (Status.PENDING, Status.REJECTED):
        raise ValidationError(
            _("Only pending or rejected booking requests can be modified.")
        )

    if booking.status == Status.PENDING and (
        booking.review_deadline is None
        or booking.review_deadline <= timezone.now()
    ):
        raise ValidationError(
            _(
                "The review period has expired. "
                "The request can no longer be modified."
            )
        )


    if set(changes) - set(EDITABLE_BOOKING_FIELDS):
        raise ValidationError(
            _("Invalid fields were provided for updating the booking request.")
        )

    changed = any(
        getattr(booking, field) != value
        for field, value in changes.items()
    )

    if not changed:
        return booking

    if booking.edit_count >= MAX_BOOKING_EDITS:
        raise ValidationError(
            _("The booking edit limit has been reached.")
        )

    for field, value in changes.items():
        setattr(booking, field, value)

    booking.edit_count += 1

    return save_booking_result(listing, booking)
