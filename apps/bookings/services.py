"""Создание и подтверждение заявок на бронирование."""

from django.core.exceptions import ValidationError
from apps.listings.models import  Property
from .models import Booking
from django.db import transaction
from django.utils.translation import gettext_lazy as _


def  confirm_booking(*, property_id, booking_id):
    """Подтвердить ожидающую заявку и вернуть её.

    Ключевые параметры property_id и booking_id указывают на объявление
    и заявку. Проверка пересечений и смена статуса выполняются в транзакции.
    Уже подтверждённая заявка возвращается сразу. Пересечение или другой
    статус вызывают ValidationError. Отсутствующая запись вызывает DoesNotExist.
    """
    with transaction.atomic():
        # Общая блокировка заставляет подтверждения одного объекта идти по очереди.
        Property.objects.select_for_update().get(pk=property_id)

        # Блокируем заявку на время проверки статуса и дат.
        booking = Booking.objects.select_for_update().get(pk=booking_id, property=property_id)
        if booking.status == Booking.Status.CONFIRMED:
            return booking
        if booking.status != Booking.Status.PENDING:
            raise ValidationError(_("Only one pending booking can be confirmed.")
                                  , code="booking_not_pending")

        # Блокирующее чтение проверяет актуальные подтверждённые брони.
        has_overlap = Booking.objects.select_for_update().filter(
            property_id=property_id,
            status=Booking.Status.CONFIRMED,
            # Строгие границы разрешают заезд в день выезда предыдущего гостя.
            start_date__lt=booking.end_date,
            end_date__gt=booking.start_date,
        ).exists()

        if has_overlap:
            raise ValidationError(_("A confirmed booking already exists for these dates.")
                                  , code="booking_overlap")
        booking.status = Booking.Status.CONFIRMED
        booking.save(update_fields=['status', "updated_at"])
        return booking

@transaction.atomic # На MySQL/InnoDB транзакция удержит блокировку объявления до сохранения брони,
# поэтому параллельное отключение объявления не сможет вклиниться между проверкой и записью.
def create_booking(*, user, property_id, start_date, end_date):
    """Создать ожидающую заявку и вернуть её с рассчитанной стоимостью.

    Передайте арендатора user, идентификатор объявления property_id,
    дату заезда start_date и дату выезда end_date по имени. День выезда
    исключается из числа оплачиваемых ночей. Недоступное объявление
    или недопустимые данные вызывают ValidationError.
    """
    # День выезда не входит в число оплачиваемых ночей.
    nights = (end_date - start_date).days

    # if nights <= 0:
    #     raise ValidationError({
    #         "end_date": "Дата выезда должна быть позже даты заезда.",
    #     })

    try:
        listing = Property.objects.select_for_update().get(pk=property_id, is_active=True)
    # Запрет новых заявок на неактивное объявление
    except Property.DoesNotExist:
        raise ValidationError(_("This listing is not available for booking.")
                              , code="listing_unavailable" ) from None


    booking = Booking(
        user=user,
        property=listing,
        start_date=start_date,
        end_date=end_date,
        total_price=listing.price_per_night * nights,
    )
    # Проверяем порядок дат и допустимую точность суммы перед вставкой.
    booking.full_clean()
    booking.save(force_insert=True)
    return booking
