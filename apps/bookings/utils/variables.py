"""Настройки бронирования."""
from datetime import timedelta

OWNER_REVIEW_TIMEOUT = timedelta(hours=2) # # Владелец должен ответить на ожидающую заявку за два часа.
MAINTENANCE_BATCH_SIZE = 100 # Максимальное количество записей за один запуск фоновой команды.

MAX_ADVANCE_BOOKING_MONTHS = 9 # ограничивает дату заезда относительно сегодня
MAX_STAY_MONTHS = 3 # ограничивает дату выезда относительно заезда.

CANCELLATION_NOTICE = timedelta(days=2) # Граничный срок отмены брони

MAX_BOOKING_EDITS = 10 # Максимально допустимое количество изменений в броне.

# Перечень полей модели Booking, значения которых могут быть изменены при редактировании заявки на бронь
# Одним редактированием считается одно сохранение с фактическими изменениями данных заявки.
EDITABLE_BOOKING_FIELDS = (
    "adults",
    "children",
    "has_pets",
    "description",
    "requires_owner_approval",
    "show_phone",
    "show_email",
)