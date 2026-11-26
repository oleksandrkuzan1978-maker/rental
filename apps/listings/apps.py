from django.apps import AppConfig


class ListingsConfig(AppConfig):
    """Конфигурация приложения объявлений."""

    name = "apps.listings"

    def ready(self):
        """Подключить обработчики удаления вложений."""
        from . import signals
