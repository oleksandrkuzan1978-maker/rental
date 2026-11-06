"""Менеджер создания пользователей и администраторов с входом по email."""

from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    """Создание пользователей с нормализацией email и хешированием пароля."""
    def create_user(self, email, password=None, **extra_fields): # **extra_fields передаёт дополнительные поля:
                                                                 # имя, фамилию, username и другие.
        """Проверить обязательные поля, хешировать пароль и сохранить пользователя."""
        if not email:
            raise ValueError('Users must have an email address')

        for field in ("username", "first_name", "last_name"):
            if not extra_fields.get(field):
                raise ValueError(f'Field {field} is required')

        email = self.normalize_email(email) # Приводим доменную часть email к нижнему регистру:
        user = self.model(email=email, **extra_fields) # Создаёт объект модели User в памяти.
        user.set_password(password) # set_password() превращает пароль в защищённый хеш.
        user.save(using=self._db) # Сохраняем пользователя в базе, выбранной менеджером.

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """create_superuser() включает права администратора и использует тот же способ создания."""

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_active') is not True:
            raise ValueError('Superuser must have is_active=True.')

        return self.create_user(email, password, **extra_fields)


