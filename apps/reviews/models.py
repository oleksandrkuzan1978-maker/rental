"""Модель отзыва и проверки его связи с бронированием."""

from django.core.validators import MinValueValidator, MaxValueValidator, ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.base.models import TimeStampModel, UUIDModel

from apps.bookings.models import Booking
# Create your models here.


class Review(UUIDModel, TimeStampModel): # Подумать: может поменять на TimeStampMod
    """Отзыв арендатора с оценкой и необязательным комментарием."""

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE
                                   , related_name='reviews', verbose_name=_('Booking'))
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
        """Проверить, что бронирование завершено."""
        super().clean()
        try:
            booking = self.booking
        except Booking.DoesNotExist:
            return

        if booking.status != Booking.Status.COMPLETED:
            raise ValidationError(_('Only completed bookings can be reviewed.'))
