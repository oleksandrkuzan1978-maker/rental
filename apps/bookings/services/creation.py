"""Создание заявки с автоматическим определением результата."""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.bookings.models import Booking
from apps.listings.models import Listing
from apps.base.services.deletion import lock_active_user
from .workflow import save_booking_result


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

    user = lock_active_user(user=user)

    try:
        listing = Listing.objects.select_for_update().get(
            pk=listing_id,
        )
    except Listing.DoesNotExist:
        raise ValidationError({
            "listing": _("The listing is unavailable."),
        }) from None

    booking = Booking(
        user=user,
        listing=listing,
        start_date=start_date,
        end_date=end_date,
        description=description,
        adults=adults,
        children=children,
        has_pets=has_pets,
        requires_owner_approval=requires_owner_approval,
        show_phone=show_phone,
        show_email=show_email,
    )

    return save_booking_result(listing, booking)