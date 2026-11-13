"""Модель пользователя с входом по email и дополнительными данными профиля."""
from sys import is_stack_trampoline_active

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import PermissionsMixin
from .managers import UserManager
from apps.base.models import TimeStampModel, UUIDModel


class User(AbstractBaseUser, PermissionsMixin, TimeStampModel, UUIDModel):
    """Аккаунт с входом по email, контактными данными и правами Django."""

    #username = models.CharField(_("username"), max_length=50, unique=True
                                #, error_messages={'unique': _("This username already exists.")})
    first_name = models.CharField(_("first name"), max_length=40)
    #last_name = models.CharField(_("last name"), max_length=40, null=True, blank=True)
    email = models.EmailField(_("email address"), max_length=150, unique=True)
    phone = models.CharField(max_length=75, null=True, blank=True)
    is_active = models.BooleanField(default=True) # Определяет, считается ли учётная запись пользователя активной.
    is_staff = models.BooleanField(default=False) # доступ к административной панели Django
    #is_superuser = models.BooleanField(default=False) # Определяет, обладает ли пользователь всеми разрешениями Django.
    #date_joined = models.DateTimeField(auto_now_add=True)
    #last_login = models.DateTimeField(null=True, blank=True)
    #updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True) # Для мягкого удаления
    #deleted = models.BooleanField(default=False)
    #position = models.CharField(max_length=15, choices=UserPositions, default=UserPositions.PROGRAMMER)
    #project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="users", null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"] # "username", "last_name"

    objects = UserManager()

    class Meta:
        """Порядок выдачи аккаунтов и ограничение мягкого удаления."""

        db_table = _("users")
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-created_at"]
        #Условие означает, что у записи либо нет даты удаления, либо аккаунт деактивирован.
        # Неактивный аккаунт без даты удаления тоже допустим.
        constraints = [models.CheckConstraint(condition=(models.Q(deleted_at__isnull=True)
                                                         | models.Q(is_active=False))
                                              , name="user_deleted_requires_inactive")]

    # def has_role(self, role):
    #     return self.groups.filter(name=role).exists()

    def __str__(self):
        """Вернуть имя пользователя."""
        return f"{self.first_name}" # {self.last_name}

