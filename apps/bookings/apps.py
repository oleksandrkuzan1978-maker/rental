"""Конфигурация приложения бронирований."""
from django.apps import AppConfig


class BookingsConfig(AppConfig):
    """Настройки приложения бронирований."""

    name = 'apps.bookings'

    def ready(self):
        """Подключить обработчики сигналов."""
        from . import signals
