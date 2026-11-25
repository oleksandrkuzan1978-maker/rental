"""Абстрактные модели для UUID и временных меток."""

from django.db import models
import uuid

class UUIDModel(models.Model):
    """Абстрактная модель с автоматически создаваемым UUID."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        """Настройки абстрактной модели идентификатора."""

        abstract = True


class TimeStampModel(models.Model):
    """Абстрактная модель с датами создания и последнего обновления."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Настройки абстрактной модели двух временных меток."""

        abstract = True
