"""Операции создания отзывов на завершённые бронирования."""

from django.core.exceptions import PermissionDenied
from django.db import transaction
from apps.bookings.models import Booking
from .models import Review

@transaction.atomic
def create_review(*, user, booking_id, rating, comment=""):
    """Проверить, сохранить и вернуть отзыв арендатора.

    Передайте текущего пользователя user, идентификатор брони booking_id
    и оценку rating по имени. Параметр comment необязателен. Для гостя
    возникает PermissionDenied, а ошибки модели вызывают ValidationError.
    """
    if not user.is_authenticated:
        raise PermissionDenied()
    booking = Booking.objects.select_for_update().get(pk=booking_id)

    review = Review(
        user=user,
        booking=booking,
        property_id=booking.property_id,
        rating=rating,
        comment=comment
    )
    review.full_clean() # отклонит незавершённую бронь и автора, который не совпадает с её арендатором
    review.save()
    return review

# В будущем представлении вызывайте сервис после проверки входных данных.
# booking_id берите из маршрута, автора — из request.user,
# а оценку и комментарий — из проверенных данных формы или сериализатора.
# Для DRF обработайте Booking.DoesNotExist как ответ 404,
# а django.core.exceptions.ValidationError преобразуйте в ошибку валидации DRF с ответом 400.