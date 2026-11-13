"""Модель бронирования и допустимые статусы заявки."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.base.models import TimeStampModel, UUIDModel
from django.conf import settings

from apps.listings.models import Property

# Create your models here.
class Booking(UUIDModel, TimeStampModel):
    """Заявка арендатора на проживание с датами, стоимостью и статусом."""

    class Status(models.TextChoices):
        """Допустимые статусы заявки на бронирование."""

        PENDING = 'pending', _('Pending')
        CONFIRMED = 'confirmed', _('Confirmed')
        REJECTED = 'rejected', _('Rejected')
        CANCELLED = 'cancelled', _('Cancelled')
        COMPLETED = 'completed', _('Completed')

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
    description = models.TextField(blank=True, verbose_name=_("Description"))

    class Meta:
        """Порядок выдачи, ограничение дат и индекс для поиска бронирований."""

        db_table = 'bookings'
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
        ordering = ['-created_at']
        constraints = [models.CheckConstraint(condition=models.Q(end_date__gt=models.F('start_date'))
                                              , name='booking_end_after_start' )]
        indexes = [models.Index(fields=["property", "status", 'start_date']
                                , name="booking_prop_status_start_idx")]
        """Эта запись создаёт один составной индекс по трём полям в указанном порядке: property, status, start_date. 
        booking_prop_status_start_idx — имя этого индекса в базе данных.
Представьте список броней, сгруппированный сначала по объявлению, затем по статусу, 
а внутри каждой группы отсортированный по дате заезда. При проверке пересечения MySQL 
может использовать индекс, чтобы:
1. Найти брони нужного объявления по property_id.
2. Взять из них группу со статусом confirmed.
3. Просмотреть в этой группе даты заезда раньше booking.end_date."""
