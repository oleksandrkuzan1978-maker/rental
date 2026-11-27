from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.users.serializers import ProfileUserSerializer, ChangeEmailSerializer

# Create your views here.

class CurrentUserView(RetrieveUpdateAPIView):
    """Получение профиля текущего пользователя."""
    serializer_class = ProfileUserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return self.request.user

class ChangeEmailView(GenericAPIView):
    """Смена email авторизованного пользователя."""

    serializer_class = ChangeEmailSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.save()

        return Response({
            "message": "Email is changed.",
            "email": user.email,
        })