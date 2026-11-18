from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from apps.rental_auth.serializers import UserSerializer

# Create your views here.

class CurrentUserView(RetrieveAPIView):
    """Получение профиля текущего пользователя."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user