"""Модель бронирования и допустимые статусы заявки."""
import builtins
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxLengthValidator, MinValueValidator

from apps.base.models import TimeStampModel, UUIDModel
from django.conf import settings

from apps.listings.models import Property

# Create your models here.


class Status(models.TextChoices):
    """Допустимые статусы заявки на бронирование."""

    PENDING = 'pending', _('Pending')
    CONFIRMED = 'confirmed', _('Confirmed')
    REJECTED = 'rejected', _('Rejected')
    CANCELLED = 'cancelled', _('Cancelled')
    COMPLETED = 'completed', _('Completed')


class Booking(UUIDModel, TimeStampModel):
    """Заявка арендатора на проживание с датами, стоимостью и статусом."""

    Status = Status

    user = models.ForeignKey(settings.AUTH_USER_MODEL
                             , on_delete=models.PROTECT
                             , related_name='bookings'
                             , verbose_name=_('User'))
    property = models.ForeignKey(Property
                                 , on_delete=models.PROTECT
                                 , related_name='bookings'
                                 , verbose_name=_('Property'))
    start_date = models.DateField(verbose_name=_('Start Date'))
    end_date = models.DateField(verbose_name=_('End Date'))
    total_price = models.DecimalField(max_digits=10, decimal_places=2
                                      , verbose_name=_('Total Price'))
    status = models.CharField(max_length=15, choices=Status, default='pending', verbose_name=_('Status'))
    description = models.TextField(blank=True, validators=[MaxLengthValidator(5000)], verbose_name=_("Description"))

    adults = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name=_("Adults"),)
    children = models.PositiveSmallIntegerField(default=0, verbose_name=_("Children"))
    has_pets = models.BooleanField(default=False, verbose_name=_("Pets"))

    show_phone = models.BooleanField(default=True)  # Флаги показа контактов в моделях
    show_email = models.BooleanField(default=True)

    class Meta:
        """Порядок выдачи, ограничение дат и индекс для поиска бронирований."""

        db_table = 'bookings'
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
        ordering = ['-created_at']
        constraints = [models.CheckConstraint(condition=models.Q(end_date__gt=models.F('start_date'))
                                              , name='booking_end_after_start' )
            , models.CheckConstraint(condition=models.Q(status__in=Status.values)
                                     , name='booking_status_in')
                                      ]
        indexes = [models.Index(
            fields=["property", "status", 'start_date']
            , name="booking_prop_status_start_idx")
                    , models.Index(
            fields=['user', '-created_at'],  # помогает находить бронирования конкретного пользователя
            name='booking_user_created_idx', # и упорядочивать их по времени создания.
            )]
        # ограничение: кол-во людей не должно быть = 0
        models.CheckConstraint(
            condition=(
                    models.Q(adults__gt=0)
                    | models.Q(children__gt=0)
            ),
            name="booking_has_guests",
        ),

    @builtins.property
    def guests_count(self):
        """Общее количество проживающих."""
        return self.adults + self.children