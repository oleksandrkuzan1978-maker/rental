"""Общие правила удаления через административную панель."""


class SuperuserDeleteAdminMixin:
    """Разрешить физическое удаление только суперпользователю."""

    def has_delete_permission(self, request, obj=None):
        """Проверить право на удаление объекта."""
        return (
            request.user.is_active
            and request.user.is_superuser
        )

    def delete_model(self, request, obj):
        """Физически удалить один объект."""
        obj.full_delete(actor=request.user)

    def delete_queryset(self, request, queryset):
        """Физически удалить выбранные объекты."""
        queryset.full_delete(actor=request.user)
