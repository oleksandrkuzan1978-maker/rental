"""Общие операции удаления и выборки записей."""

from django.db import models, transaction


class DeleteQuerySet(models.QuerySet):
    """Физическое удаление записей с проверкой прав."""

    def full_delete(self, *, actor):
        """Физически удалить выборку от имени суперпользователя."""
        from .services.access import require_superuser

        require_superuser(actor)
        return super().delete() # удаляет выборку QuerySet

    def delete(self, *, actor=None):
        """По умолчанию разрешать физическое удаление только суперюзеру."""
        return self.full_delete(actor=actor)


class SoftDeleteQuerySet(DeleteQuerySet):
    """Выборки моделей, поддерживающих мягкое удаление."""

    @transaction.atomic
    def soft_delete(self, *, actor):
        """Удалить записи через общие проверки бизнес-правил."""
        total = 0
        details = {}

        for obj in self.order_by("pk"):
            count, labels = obj.delete(actor=actor)
            total += count

            for label, value in labels.items():
                details[label] = details.get(label, 0) + value

        return total, details

    def delete(self, *, actor=None):
        """Обычное удаление выборки считать мягким."""
        return self.soft_delete(actor=actor)


class AllObjectsManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    """Все записи, включая мягко удалённые."""


class ActiveObjectsManager(AllObjectsManager):
    """Только неудалённые записи."""

    def get_queryset(self):
        """Исключить записи с заполненной датой удаления."""
        return super().get_queryset().filter(
            deleted_at__isnull=True,
        )


class DeletedObjectsManager(AllObjectsManager):
    """Только мягко удалённые записи."""

    def get_queryset(self):
        """Выбрать записи с заполненной датой удаления."""
        return super().get_queryset().filter(
            deleted_at__isnull=False,
        )

