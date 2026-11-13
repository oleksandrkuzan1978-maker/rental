"""Формы и административные настройки пользовательских аккаунтов."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm

from .models import User


class UserAddForm(BaseUserCreationForm):
    """Форма создания пользователя с email и хешированием пароля."""

    class Meta:
        """Модель и поля формы создания пользователя."""

        model = User
        fields = ("email", "first_name", "phone")


class UserEditForm(UserChangeForm):
    """Форма редактирования профиля и прав пользователя."""

    class Meta(UserChangeForm.Meta):
        """Пользовательская модель для стандартной формы редактирования."""

        model = User


# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка аккаунтов с входом по email и формами смены пароля."""

    add_form = UserAddForm
    form = UserEditForm

    list_display = ("email", "first_name", "is_active", "is_staff", "is_superuser", "created_at")
    search_fields = ("email", "first_name")
    list_filter = ("is_active", "is_staff", "is_superuser")
    ordering = ("-created_at",)
    readonly_fields = ("last_login", "created_at", "updated_at", "deleted_at")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Профиль", {"fields": ("first_name", "phone")}),
        ("Доступ", {"fields": (
            "is_active", "is_staff", "is_superuser", "groups", "user_permissions",
        )}),
        ("Даты", {"fields": ("last_login", "created_at", "updated_at", "deleted_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "phone", "password1", "password2"),
        }),
    )

    def has_add_permission(self, request):
        """Разрешить создание аккаунтов суперпользователям."""
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """Разрешить изменение аккаунтов суперпользователям."""
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """Запретить физическое удаление аккаунтов через админку."""
        return False


