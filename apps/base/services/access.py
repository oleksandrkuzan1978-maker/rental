"""Общие проверки прав и блокировка активного пользователя."""

from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

from apps.users.models import User


def require_superuser(actor):
    """Проверить актуальные права на физическое удаление."""
    if (
        actor is None
        or not actor.is_authenticated
        or not User.all_objects.filter(
            pk=actor.pk,
            is_active=True,
            is_superuser=True,
            deleted_at__isnull=True,
        ).exists()
    ):
        raise PermissionDenied(
            _("Only a superuser can permanently delete records.")
        )


def lock_active_user(*, user):
    """Заблокировать аккаунт внутри транзакции и проверить его доступ."""
    if user is None or not user.is_authenticated:
        raise PermissionDenied(_("You must be logged in."))

    try:
        return User.all_objects.select_for_update().get(
            pk=user.pk,
            is_active=True,
            deleted_at__isnull=True,
        )
    except User.DoesNotExist:
        raise PermissionDenied(_("The account is unavailable.")) from None


