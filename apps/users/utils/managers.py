"""Менеджер создания пользователей и администраторов с входом по email."""

from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

from apps.base.managers import SoftDeleteQuerySet


class AllUserManager(BaseUserManager.from_queryset(SoftDeleteQuerySet)):
    """Создание пользователей с нормализацией email и хешированием пароля."""
    # в коде регистрации пользователя использовать этот метод: User.objects.create_user(email=..., password=...)
    def create_user(self, email, password, **extra_fields): # **extra_fields передаёт дополнительные поля:
                                                                 # имя, фамилию, username и другие.
        """Создать и вернуть пользователя с хешированным паролем.

        Требуются email, password и name в extra_fields. При отсутствии
        любого из этих значений вызвать ValueError.
        """
        if not email:
            raise ValueError(_('Users must have an email address'))
        if not password:
            raise ValueError(_("Users must have a password"))

        field = "name"
        if not extra_fields.get(field):
            raise ValueError(_(f'Field {field} is required'))

        email = self.normalize_email(email).lower() # Приводим доменную часть email к нижнему регистру:
        user = self.model(email=email, **extra_fields) # Создаёт объект модели User в памяти.
        user.set_password(password) # set_password() превращает пароль в защищённый хеш.
        user.save(using=self._db) # Сохраняем пользователя в базе, выбранной менеджером.

        return user

    def create_superuser(self, email, password, **extra_fields):
        """Создать и вернуть активного суперпользователя с доступом в админку.

        Параметры передаются в create_user. Если is_staff, is_superuser
        или is_active явно отключены, вызвать ValueError.
        """

        for field in ("is_staff", "is_superuser", "is_active"):
            value = extra_fields.setdefault(field, True)
            if value is not True:
                raise ValueError(f"Superuser must have {field}=True.")

        # extra_fields.setdefault('is_staff', True)
        # extra_fields.setdefault('is_superuser', True)
        # extra_fields.setdefault('is_active', True)

        # if extra_fields.get('is_staff') is not True:
        #     raise ValueError('Superuser must have is_staff=True.')
        # if extra_fields.get('is_superuser') is not True:
        #     raise ValueError('Superuser must have is_superuser=True.')
        # if extra_fields.get('is_active') is not True:
        #     raise ValueError('Superuser must have is_active=True.')

        return self.create_user(email, password, **extra_fields)

class UserManager(AllUserManager):
    """Создание пользователей и выборка неудалённых аккаунтов."""

    def get_queryset(self):
        """Исключить мягко удалённые аккаунты."""
        return super().get_queryset().filter(
            deleted_at__isnull=True,
        )


