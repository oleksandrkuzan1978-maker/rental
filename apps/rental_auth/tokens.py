from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

def get_tokens_for_user(user):
    """Создаёт пару JWT-токенов для пользователя.

        Args:
            user: Пользователь, для которого выпускаются токены.

        Returns:
            Словарь со строковыми значениями токена доступа (`access`)
            и токена обновления (`refresh`).
        """
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }

def blacklist_all_tokens(user):
    """Добавляет все зарегистрированные токены обновления пользователя в чёрный список.

        Повторный вызов не создаёт дубликатов. Уже выданные токены доступа
        остаются действительными до истечения срока действия.

        Args:
            user: Пользователь, чьи токены обновления нужно отозвать.
        """
    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)