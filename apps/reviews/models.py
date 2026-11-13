"""Модель отзыва и проверки его связи с бронированием."""

from django.core.validators import MinValueValidator, MaxValueValidator, ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.base.models import TimeStampModel, UUIDModel
from django.conf import settings

from apps.bookings.models import Booking
from apps.listings.models import Property
# Create your models here.


class Review(UUIDModel, TimeStampModel): # Подумать: может поменять на TimeStampMod
    """Отзыв арендатора с оценкой и необязательным комментарием."""

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE
                                   , related_name='reviews', verbose_name=_('Booking'))
    property = models.ForeignKey(Property, on_delete=models.CASCADE
                                 , related_name='reviews', verbose_name=_('Property'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                             , related_name='reviews', verbose_name=_('User'))
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)]
                                              , verbose_name=_('Rating'))
    comment = models.TextField(blank=True, verbose_name=_('Comment'))

    class Meta:
        """Настройки таблицы, сортировки и ограничения оценки от 1 до 5."""

        db_table = 'reviews'
        constraints = [models.CheckConstraint(condition=Q(rating__gte=1, rating__lte=5)
                                              , name='reviews_rating_1_and_5')]
        ordering = ['-rating']
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')

    def clean(self):
        """Проверить завершение брони и соответствие автора и объявления.

        При нарушении правил вызвать ValidationError с найденными ошибками.
        """
        super().clean()
        try:
            booking = self.booking
        except Booking.DoesNotExist:
            # Наличие бронирования проверяет само поле booking.
            return
        errors = []
        if booking.status != Booking.Status.COMPLETED:
            errors.append(_('Only completed bookings can be reviewed.'))
        if self.property_id != booking.property_id:
            errors.append(_('The property must match the booking.'))
        if self.user_id != booking.user_id:
            errors.append(_('The author must be the renter on the booking.'))
        if errors:
            raise ValidationError(errors)



        # При создании отзыва берите автора из request.user,
        # а объявление из бронирования. Из формы достаточно принять оценку и комментарий.
        # В обработчике или сервисе сохранение будет выглядеть так:
        # review = Review(
        #     booking=booking,
        #     property_id=booking.property_id,
        #     user=request.user,
        #     rating=rating,
        #     comment=comment,
        # )
        # review.full_clean() # Обязательно!
        # review.save()
