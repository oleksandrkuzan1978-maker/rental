"""Настройки бронирования."""
from datetime import timedelta

OWNER_REVIEW_TIMEOUT = timedelta(hours=2)
NOTIFICATION_RETRY_DELAY = timedelta(minutes=5) #Задержка повторной попытки уведомления.
MAINTENANCE_BATCH_SIZE = 100 # Размер пакета технического обслуживания

MAX_ADVANCE_BOOKING_MONTHS = 9 # ограничивает дату заезда относительно сегодня
MAX_STAY_MONTHS = 3 # ограничивает дату выезда относительно заезда.
