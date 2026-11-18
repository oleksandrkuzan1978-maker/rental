from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from .serializers import BookingSerializer

class BookingCreateView(CreateAPIView):
    """Создание бронирования текущего пользователя."""
    serializer_class = BookingSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

