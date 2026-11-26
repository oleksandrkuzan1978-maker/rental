"""Общие операции удаления и выборки записей."""

from django.db import models, transaction


class DeleteQuerySet(models.QuerySet):
    """Физическое удаление записей с проверкой прав."""

    def full_delete(self, *, actor):
        """Физически удалить выборку от имени суперпользователя."""
        from .services.deletion import require_superuser

        require_superuser(actor)
        return super().delete() # удаляет выборку QuerySet

    def delete(self, *, actor=None):
        """По умолчанию разрешать физическое удаление только суперюзеру."""
        return self.full_delete(actor=actor)


class SoftDeleteQuerySet(DeleteQuerySet):
    """Выборки моделей, поддерживающих мягкое удаление."""

    def active(self):
        """Вернуть записи без даты удаления."""
        return self.filter(deleted_at__isnull=True)

    def deleted(self):
        """Вернуть мягко удалённые записи."""
        return self.filter(deleted_at__isnull=False)

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

    def hard_delete(self, *, actor):
        """Физически удалить только ранее мягко удалённые записи."""
        return self.deleted().full_delete(actor=actor)


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    """Менеджер с явным выбором активных и удалённых записей."""

# class TaskManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(categories__deleted_at__isnull=False).distinct()

