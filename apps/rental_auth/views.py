from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from rest_framework_simplejwt.views import  TokenObtainPairView, TokenRefreshView, TokenBlacklistView

from apps.rental_auth.serializers import (UserRegisterSerializer, UserSerializer
                                        , ChangePasswordSerializer, LoginSerializer, RefreshSerializer)
from .tokens import get_tokens_for_user, blacklist_all_tokens

# Create your views here.


LogoutView = TokenBlacklistView


class AuthThrottleMixin:
    """Общий лимит запросов для представлений аутентификации."""

    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"


class RefreshView(AuthThrottleMixin, TokenRefreshView):
    """Обновление JWT с проверкой доступности аккаунта."""

    serializer_class = RefreshSerializer


class LogoutAllView(APIView):
    """Представление для отзыва refresh-токенов текущего пользователя."""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Отозвать refresh-токены пользователя и вернуть HTTP 204."""
        blacklist_all_tokens(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginView(AuthThrottleMixin, TokenObtainPairView):
    """Выдача JWT по email и паролю."""

    serializer_class = LoginSerializer


class RegisterView(AuthThrottleMixin, generics.CreateAPIView):
    """Представление для регистрации и выдачи токенов новому пользователю."""

    serializer_class = UserRegisterSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """Зарегистрировать пользователя и вернуть его профиль и пару JWT."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({'user': UserSerializer(user).data
                            , **get_tokens_for_user(user)}
                        , status=status.HTTP_201_CREATED)


class ChangePasswordView(APIView):
    """Представление для смены пароля текущего пользователя."""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Сменить пароль, отозвать старые refresh-токены и выдать новую пару JWT."""
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        blacklist_all_tokens(user)
        return Response(get_tokens_for_user(user), status=status.HTTP_200_OK)