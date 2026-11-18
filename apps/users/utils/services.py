"""Регистрация и мягкое удаление пользовательских аккаунтов."""
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

