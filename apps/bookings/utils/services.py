"""Создание и подтверждение заявок на бронирование."""
from django.utils import timezone
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from apps.listings.models import  Listing, ListingStatus
from apps.bookings.models import Booking
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from .variables import (
    MAX_ADVANCE_BOOKING_MONTHS,
    MAX_STAY_MONTHS,
)

def  confirm_booking(*, listing_id, booking_id):
    """Подтвердить ожидающую заявку и вернуть её.

    Ключевые параметры listing_id и booking_id указывают на объявление
    и заявку. Проверка пересечений и смена статуса выполняются в транзакции.
    Уже подтверждённая заявка возвращается сразу. Пересечение или другой
    статус вызывают ValidationError. Отсутствующая запись вызывает DoesNotExist.
    """
    with transaction.atomic():
        # Общая блокировка заставляет подтверждения одного объекта идти по очереди.
        Listing.objects.select_for_update().get(pk=listing_id)

        # Блокируем заявку на время проверки статуса и дат.
        booking = Booking.objects.select_for_update().get(pk=booking_id, listing=listing_id)
        if booking.status == Booking.Status.CONFIRMED:
            return booking
        if booking.status != Booking.Status.PENDING:
            raise ValidationError(_("Only one pending booking can be confirmed.")
                                  , code="booking_not_pending")

        # Блокирующее чтение проверяет актуальные подтверждённые брони.
        has_overlap = Booking.objects.select_for_update().filter(
            listing_id=listing_id,
            status__in=[
                Booking.Status.PENDING,
                Booking.Status.CONFIRMED,
            ],
            start_date__lt=booking.end_date,
            end_date__gt=booking.start_date,
        ).exclude(
            pk=booking.pk,
        ).exists()

        if has_overlap:
            raise ValidationError(_("A confirmed booking already exists for these dates.")
                                  , code="booking_overlap")
        booking.status = Booking.Status.CONFIRMED
        booking.save(update_fields=['status', "updated_at"])
        return booking


def _add_months(day, months):
    """Прибавить календарные месяцы с учётом длины месяца."""
    year, month_index = divmod(
        day.year * 12 + day.month - 1 + months,
        12,
    )
    month = month_index + 1

    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)

    last_day = (next_month - timedelta(days=1)).day

    return day.replace(
        year=year,
        month=month,
        day=min(day.day, last_day),
    )


@transaction.atomic # На MySQL/InnoDB транзакция удержит блокировку объявления до сохранения брони,
# поэтому параллельное отключение объявления не сможет вклиниться между проверкой и записью.
def create_booking(*, user, listing_id, start_date, end_date, description="",
                   adults=1, children=0, has_pets=False,
                   show_phone=True, show_email=True):
    """Создать ожидающую заявку и вернуть её с рассчитанной стоимостью.

    Передайте арендатора user, идентификатор объявления listing_id,
    дату заезда start_date и дату выезда end_date по имени. День выезда
    исключается из числа оплачиваемых ночей. Недоступное объявление
    или недопустимые данные вызывают ValidationError.
    """
    today = timezone.localdate()

    latest_start_date = _add_months(
        today,
        MAX_ADVANCE_BOOKING_MONTHS,
    )
    latest_end_date = _add_months(
        start_date,
        MAX_STAY_MONTHS,
    )

    if start_date < today:
        raise ValidationError(_("The arrival date cannot be in the past."))
    if start_date > latest_start_date:
        raise ValidationError({"start_date": _(
            "Move-in is possible no later than %(months)s months from now."
        ) % {"months": MAX_ADVANCE_BOOKING_MONTHS}, })
    if end_date <= start_date:
        raise ValidationError(_("The departure date must be later than the arrival date."))
    if end_date > latest_end_date:
        raise ValidationError({
        "end_date": _(
            "The duration of the stay cannot exceed "
            "%(months)s months."
        ) % {"months": MAX_STAY_MONTHS},
    })

    # День выезда не входит в число оплачиваемых ночей.
    nights = (end_date - start_date).days

    try:
        listing = Listing.objects.select_for_update().get(pk=listing_id
                                                          , status=ListingStatus.PUBLISHED
                                                          , deleted_at__isnull=True
                                                          , price_per_night__isnull=False)
    # Запрет новых заявок на неактивное объявление
    except Listing.DoesNotExist:
        raise ValidationError(_("This listing is not available for booking.")
                              , code="listing_unavailable" ) from None

    # проверка наличия броней на пересечение по датам
    has_overlap = Booking.objects.select_for_update().filter(
        listing=listing,
        status__in=[
            Booking.Status.PENDING,
            Booking.Status.CONFIRMED,
        ],
        start_date__lt=end_date,
        end_date__gt=start_date,
    ).exists()

    if has_overlap:
        raise ValidationError(
            _("The listing is already booked for the selected dates. "
                "Please choose different dates."),
            code="booking_overlap",
        )

    booking = Booking(
        user=user,
        listing=listing,
        start_date=start_date,
        end_date=end_date,
        total_price=listing.price_per_night * nights,
        description=description,
        adults=adults,
        children=children,
        has_pets=has_pets,
        show_phone=show_phone,
        show_email=show_email,
    )
    # full_clean выполняет проверки модели.
    booking.full_clean()
    booking.save(force_insert=True) # force_insert=True явно фиксирует нужное поведение.
    # Если запись с таким первичным ключом уже существует, база вернёт ошибку
    return booking
