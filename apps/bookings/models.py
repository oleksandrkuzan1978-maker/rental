"""Модель бронирования и допустимые статусы заявки."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxLengthValidator, MinValueValidator, MaxValueValidator

from apps.base.models import TimeStampModel, UUIDModel
from django.conf import settings

from apps.listings.models import Listing
from apps.bookings.utils.choices import Status, DecisionReason
from apps.bookings.utils.variables import MAX_BOOKING_EDITS

# Create your models here.


class Booking(UUIDModel, TimeStampModel):
    """Заявка арендатора на проживание с датами, стоимостью и статусом."""

    Status = Status

    user = models.ForeignKey(settings.AUTH_USER_MODEL
                             , on_delete=models.PROTECT
                             , related_name='bookings'
                             , verbose_name=_('User'))
    listing = models.ForeignKey(Listing
                                , on_delete=models.PROTECT
                                , related_name='bookings'
                                , verbose_name=_('Listing'))
    start_date = models.DateField(verbose_name=_('Start Date'))
    end_date = models.DateField(verbose_name=_('End Date'))
    total_price = models.DecimalField(max_digits=10, decimal_places=2
                                      , verbose_name=_('Total Price'))
    status = models.CharField(max_length=15, choices=Status, default=Status.PENDING, verbose_name=_('Status'))
    description = models.TextField(blank=True, validators=[MaxLengthValidator(5000)], verbose_name=_("Description"))

    adults = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name=_("Adults"),)
    children = models.PositiveSmallIntegerField(default=0, verbose_name=_("Children"))
    has_pets = models.BooleanField(default=False, verbose_name=_("Pets"))

    show_phone = models.BooleanField(default=True)  # Флаги показа контактов в моделях
    show_email = models.BooleanField(default=True)
    # requires_owner_approval - есть ли у арендатора особые условия, требующие согласования.
    requires_owner_approval = models.BooleanField(default=False
                                                  , verbose_name=_("Special conditions require owner approval"))
    # decision_reason — почему заявка была подтверждена или отклонена.
    decision_reason = models.CharField(max_length=50,
                                       choices=DecisionReason,
                                       blank=True,
                                       default='',
                                       verbose_name=_("Decision Reason"),)
    # decided_at — когда было принято решение о подтверждении или отклонении.
    decided_at = models.DateTimeField(null=True, blank=True
                                      , verbose_name=_("Decision time"))
    # review_deadline — до какого момента владелец должен ответить.
    review_deadline = models.DateTimeField(null=True, blank=True
                                           , verbose_name=_("Owner response deadline"))
    edit_count = models.PositiveSmallIntegerField(
        default=0,
        editable=False,
        validators=[MaxValueValidator(MAX_BOOKING_EDITS)],
        verbose_name=_("Number of edits"),
    )


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
            , models.CheckConstraint(condition=models.Q(adults__gte=1)
                                     , name="booking_has_adult",)
            , models.CheckConstraint(condition=models.Q(decision_reason__in=["", *DecisionReason.values])
                                     , name="booking_has_decision_reason",)
            , models.CheckConstraint(condition=models.Q(edit_count__lte=MAX_BOOKING_EDITS)
                                     , name="booking_edit_count_max",),]
        indexes = [
            models.Index(
                fields=["listing", "status", "start_date"],
                name="booking_prop_status_start_idx",
            ),
            models.Index(
                fields=["user", "-created_at"], # помогает находить бронирования конкретного пользователя
                name="booking_user_created_idx", # и упорядочивать их по времени создания.
            ),
            models.Index(
                fields=["status", "review_deadline"], # индекс для поиска просроченных заявок
                name="booking_review_due_idx"
            ),
        ]

    @property
    def guests_count(self):
        """Общее количество проживающих."""
        return self.adults + self.children

    def __str__(self):
        return f"Booking: {self.pk}, {self.status}"
