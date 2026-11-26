"""Операции создания отзывов на завершённые бронирования."""
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.base.deletion import lock_active_user
from apps.bookings.models import Booking
from apps.bookings.utils.choices import Status

from .models import Review


def is_booking_tenant(*, user, booking):
    """Проверить, что вошедший в систему пользователь является арендатором брони."""
    return user.is_authenticated and booking.user_id == user.pk

@transaction.atomic
def create_review(*, user, booking_id, rating, comment=""):
    """Создать отзыв пользователя на собственную завершённую бронь."""
    user = lock_active_user(user=user)

    booking = Booking.objects.select_for_update().get(
        pk=booking_id,
    )

    if not is_booking_tenant(user=user, booking=booking):
        raise PermissionDenied(
            _("Можно оставить отзыв только о своей брони.")
        )

    if booking.deleted_at is not None:
        raise ValidationError(
            _("Нельзя оставить отзыв для удалённой брони.")
        )

    if booking.status != Status.COMPLETED:
        raise ValidationError(
            _("Отзыв можно оставить только для завершённой брони.")
        )

    review = Review(
        booking=booking,
        rating=rating,
        comment=comment,
    )

    review.full_clean()
    review.save()

    return review

# В будущем представлении вызывайте сервис после проверки входных данных.
# booking_id берите из маршрута, автора — из request.user,
# а оценку и комментарий — из проверенных данных формы или сериализатора.
# Для DRF обработайте Booking.DoesNotExist как ответ 404,
# а django.core.exceptions.ValidationError преобразуйте в ошибку валидации DRF с ответом 400.

@transaction.atomic
def update_review(*, user, review_id, rating, comment=""):
    """Изменить собственный неудалённый отзыв на завершённую бронь.

    Заблокировать аккаунт, затем бронь и отзыв. Запретить изменение
    чужого отзыва и записей, связанных с удалённой бронью.
    """
    user = lock_active_user(user=user)

    # Пока только узнаём, к какой брони относится отзыв.
    reference = Review.objects.only("booking_id").get(
        pk=review_id,
    )

    # Сначала блокируем бронь, затем связанный с ней отзыв.
    booking = Booking.objects.select_for_update().get(
        pk=reference.booking_id,
    )
    review = Review.objects.select_for_update().get(
        pk=review_id,
        booking_id=booking.pk,
    )

    if booking.user_id != user.pk:
        raise PermissionDenied(_("Можно изменять только свой отзыв."))

    if review.deleted_at is not None:
        raise ValidationError(_("Удалённый отзыв нельзя редактировать."))

    if booking.deleted_at is not None:
        raise ValidationError(
            _("Нельзя изменить отзыв для удалённой брони.")
        )

    if booking.status != Status.COMPLETED:
        raise ValidationError(
            _("Отзыв можно изменять только для завершённой брони.")
        )

    review.booking = booking
    review.rating = rating
    review.comment = comment

    review.full_clean()
    review.save(update_fields=[
        "rating",
        "comment",
        "updated_at",
    ])

    return review