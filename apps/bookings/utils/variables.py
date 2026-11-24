"""Настройки бронирования."""
from datetime import timedelta

OWNER_REVIEW_TIMEOUT = timedelta(hours=2) # # Владелец должен ответить на ожидающую заявку за два часа.
MAINTENANCE_BATCH_SIZE = 100 # Максимальное количество записей за один запуск фоновой команды.

MAX_ADVANCE_BOOKING_MONTHS = 9 # ограничивает дату заезда относительно сегодня
MAX_STAY_MONTHS = 3 # ограничивает дату выезда относительно заезда.

# CHECK_IN_TIME = time(hour=14, minute=0)  # час начала срока бронирования
# CHECK_OUT_TIME = time(hour=11, minute=0) # час окончания срока бронирования
