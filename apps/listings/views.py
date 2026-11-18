from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Property
from .serializers import PropertySerializer

# Create your views here.

class PropertyCreateView(CreateAPIView):
    """Создание объявления текущего пользователя."""
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]
   # переопределение perform_create нужно, чтобы сервер
    # назначил владельцем объявления текущего пользователя
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# через это представление выполняется и PUT и PATCH
class PropertyUpdateView(UpdateAPIView):
    """Редактирование собственного объявления."""
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]
    # Переопределенный get_queryset определяет,
    # среди каких объявлений представление может искать объект для редактирования.
    # (только среди неудаленных объявлений пользователя, сделавшего запрос.)
    def get_queryset(self):
        return Property.objects.filter(
            user=self.request.user
            , deleted_at__isnull=True
        )
