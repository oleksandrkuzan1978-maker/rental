"""Абстрактные модели """
from django.db import models
import uuid

from .managers import SoftDeleteManager

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


class ProtectedDeleteModel(models.Model):
    """Разрешить физическое удаление только суперпользователю."""

    class Meta:
        abstract = True

    def full_delete(self, using=None, keep_parents=False, *, actor=None):
        """Физически удалить объект после проверки прав."""
        from .deletion import require_superuser

        require_superuser(actor)

        return super().delete(  # Удаляет экземпляр модели (запись)
            using=using,
            keep_parents=keep_parents,
        )

    def delete(self, using=None, keep_parents=False, *, actor=None):
        """Для моделей без мягкого удаления выполнить полное удаление."""
        return self.full_delete(
            using=using,
            keep_parents=keep_parents,
            actor=actor,
        )


class SoftDeleteModel(ProtectedDeleteModel):
    """Объект с мягким удалением через общие бизнес-проверки."""

    objects = SoftDeleteManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, *, actor=None):
        """Мягко удалить объект от имени переданного пользователя."""
        from .deletion import soft_delete_object

        if using not in (None, "default"):
            raise ValueError("Удаление рассчитано на базу default.")

        return soft_delete_object(obj=self, actor=actor)

    def soft_delete(self, *, actor):
        """Явное название операции мягкого удаления."""
        return self.delete(actor=actor)