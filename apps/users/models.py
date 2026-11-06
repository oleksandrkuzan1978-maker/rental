"""Модель пользователя с входом по email и дополнительными данными профиля."""

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import PermissionsMixin
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Пользователь с входом по email, контактными данными, должностью и проектом."""
    username = models.CharField(_("username"), max_length=50, unique=True
                                , error_messages={'unique': _("This username already exists.")})
    first_name = models.CharField(_("first name"), max_length=40)
    last_name = models.CharField(_("last name"), max_length=40)
    email = models.EmailField(_("email address"), max_length=150, unique=True)
    phone = models.CharField(max_length=75, null=True, blank=True)
    is_active = models.BooleanField(default=True) # Определяет, считается ли учётная запись пользователя активной.
    is_staff = models.BooleanField(default=False) # доступ к административной панели Django
    is_superuser = models.BooleanField(default=False) # Определяет, обладает ли пользователь всеми разрешениями Django.
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True) # Это поле хранит дату последнего изменения записи пользователя.
    deleted_at = models.DateTimeField(null=True, blank=True) # Для мягкого удаления
    #deleted = models.BooleanField(default=False)
    #position = models.CharField(max_length=15, choices=UserPositions, default=UserPositions.PROGRAMMER)
    #project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="users", null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        """Вернуть имя и фамилию пользователя."""
        return f"{self.first_name} {self.last_name}"

