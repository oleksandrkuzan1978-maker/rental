"""Проверка дат бронирования."""
from datetime import date, timedelta

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone

from ..utils.variables import (
    MAX_ADVANCE_BOOKING_MONTHS,
    MAX_STAY_MONTHS,
)

def _add_months(day, months):
    """Прибавить календарные месяцы с учётом последнего дня месяца."""
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


def validate_dates(start_date, end_date):
    """Проверить даты новой заявки по ограничениям проекта."""
    today = timezone.localdate()

    if start_date < today:
        raise ValidationError(_("The arrival date cannot be in the past."))

    if start_date > _add_months(today, MAX_ADVANCE_BOOKING_MONTHS):
        raise ValidationError(_("Move-in is possible no later than %(months)s months from now."
                                ) % {"months": MAX_ADVANCE_BOOKING_MONTHS})

    if end_date <= start_date:
        raise ValidationError(_("The departure date must be later than the arrival date."))

    if end_date > _add_months(start_date, MAX_STAY_MONTHS):
        raise ValidationError(_(
            "The duration of the stay cannot exceed "
            "%(months)s months.") % {"months": MAX_STAY_MONTHS})
