"""Модель отзыва и проверки его связи с бронированием."""
from django.core.validators import MinValueValidator, MaxValueValidator, MaxLengthValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.base.models import TimeStampModel, UUIDModel, SoftDeleteModel

from apps.bookings.models import Booking
# Create your models here.


class Review(UUIDModel, TimeStampModel, SoftDeleteModel):
    """Отзыв арендатора с оценкой и необязательным комментарием."""

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE
                                   , related_name='reviews'
                                   , verbose_name=_('Booking'))
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)]
                                              , verbose_name=_('Rating'))
    comment = models.TextField(blank=True, validators=[MaxLengthValidator(5000)]
                               , verbose_name=_('Comment'))

    class Meta(SoftDeleteModel.Meta):
        """Настройки таблицы, сортировки и ограничения оценки от 1 до 5."""

        db_table = 'reviews'
        constraints = [models.CheckConstraint(condition=Q(rating__gte=1, rating__lte=5)
                                              , name='reviews_rating_1_and_5')]
        ordering = ['-rating']
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')

    # Возможно, стоит убрать этот clean отсюда. Создание отзывов будет идти только через API (вьюшки)
    # def clean(self):
    #     """Проверить возможность создания отзыва."""
    #     super().clean()
    #     try:
    #         booking = self.booking
    #     except Booking.DoesNotExist:
    #         return
    #
    #     if booking.status != Booking.Status.COMPLETED:
    #         raise ValidationError(_('Only completed bookings can be reviewed.'))
    #     if booking.end_date >= timezone.localdate():
    #         raise ValidationError(_('A review can only be submitted after the booking ends.'))
