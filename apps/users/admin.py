"""Формы и административные настройки пользовательских аккаунтов."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm

from .models import User
from apps.base.admin import SuperuserDeleteAdminMixin


class UserAddForm(BaseUserCreationForm):
    """Форма создания пользователя с email и хешированием пароля."""

    class Meta:
        """Модель и поля формы создания пользователя."""

        model = User
        fields = ("email", "name", "phone")


class UserEditForm(UserChangeForm):
    """Форма редактирования профиля и прав пользователя."""

    class Meta(UserChangeForm.Meta):
        """Пользовательская модель для стандартной формы редактирования."""

        model = User


# Register your models here.
@admin.register(User)
class UserAdmin(SuperuserDeleteAdminMixin, BaseUserAdmin):
    """Админка аккаунтов с входом по email и формами смены пароля."""

    add_form = UserAddForm
    form = UserEditForm

    list_display = ("email", "name", 'phone', "is_active", "is_staff", "is_superuser", "created_at", "last_login")
    search_fields = ("email", "name", 'phone')
    list_filter = ("is_active", "is_staff", "is_superuser")
    ordering = ("-created_at",)
    readonly_fields = ("last_login", "created_at", "updated_at", "deleted_at")

    # Форма редактирования существующего аккаунта
    fieldsets = (
        (None, {
            "fields": ("email", "password"),
        }),
        ("Профиль", {
            "fields": ("name", "phone"),
        }),
        ("Доступ", {
            "fields": ("is_active", "is_staff"),
        }),
        ("Даты", {
            "fields": (
                "last_login",
                "created_at",
                "updated_at",
                "deleted_at",
            ),
        }),
    )

    # Форма создания нового аккаунта
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "name",
                "phone",
                "password1",
                "password2",
            ),
        }),
    )


    def has_add_permission(self, request):
        """Разрешить создание аккаунтов суперпользователям."""
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """Разрешить изменение аккаунтов суперпользователям."""
        return request.user.is_superuser



