"""Регистрация и мягкое удаление пользовательских аккаунтов."""

from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.utils import timezone
from apps.users.models import User

def soft_delete_user(*, user_id):
    """Деактивировать аккаунт user_id и записать дату мягкого удаления.

    Вернуть True, если запись обновлена. Если аккаунт отсутствует
    или уже мягко удалён, вернуть False.
    """
    now = timezone.now()
    updated = (User.objects.filter(pk=user_id
                                  , deleted_at__isnull=True).update(deleted_at=now
                                                                    , is_active=False
                                                                    , updated_at=now))
    return updated == 1


@transaction.atomic
def register_user(*, email, name, password):
    """Создать пользователя и добавить его в группу Tenant.

    Передайте email, name и password по имени. Вернуть новый аккаунт.
    Если группа Tenant отсутствует, вызвать Group.DoesNotExist.
    """
    tenant = Group.objects.get(name=_('Tenant'))

    user = User.objects.create_user(
        email=email,
        name=name,
        password=password,
    )
    user.groups.add(tenant)
    return user