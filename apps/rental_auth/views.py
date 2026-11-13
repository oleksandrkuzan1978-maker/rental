from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from rest_framework_simplejwt.views import  TokenObtainPairView, TokenRefreshView, TokenBlacklistView

from apps.rental_auth.serializers import UserRegisterSerializer, UserSerializer
from .tokens import get_tokens_for_user


# Create your views here.


LogoutView = TokenBlacklistView


class AuthThrottleMixin:
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "auth"


class RefreshView(AuthThrottleMixin, TokenRefreshView):
    pass



class LoginView(AuthThrottleMixin, TokenObtainPairView):
    pass


class RegisterView(AuthThrottleMixin, generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({'user': UserSerializer(user).data
                            , **get_tokens_for_user(user)}
                        , status=status.HTTP_201_CREATED)