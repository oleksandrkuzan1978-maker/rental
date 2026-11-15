"""Модель пользователя с входом по email и дополнительными данными профиля."""
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import PermissionsMixin
from .managers import UserManager
from apps.base.models import TimeStampModel, UUIDModel


class User(AbstractBaseUser, PermissionsMixin, TimeStampModel, UUIDModel):
    """Аккаунт с входом по email, контактными данными и правами Django."""
    name = models.CharField(_("name"), max_length=40)
    email = models.EmailField(_("email address"), max_length=150, unique=True)
    phone = models.CharField(max_length=75, null=True, blank=True)
    is_active = models.BooleanField(default=True) # Определяет, считается ли учётная запись пользователя активной.
    is_staff = models.BooleanField(default=False) # доступ к административной панели Django
    #is_superuser = models.BooleanField(default=False) # Определяет, обладает ли пользователь всеми разрешениями Django.
    #last_login = models.DateTimeField(null=True, blank=True)
    #updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True) # Для мягкого удаления

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"] # "username", "last_name"

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
        return f"{self.name}"

