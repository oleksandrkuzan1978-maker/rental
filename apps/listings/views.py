from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Listing, City
from .serializers import ListingSerializer, CityDistrictSerializer

# Create your views here.

class ListingCreateView(CreateAPIView):
    """Создание объявления текущего пользователя."""
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticated]
   # переопределение perform_create нужно, чтобы сервер
    # назначил владельцем объявления текущего пользователя
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# через это представление выполняется и PUT и PATCH
class ListingUpdateView(UpdateAPIView):
    """Редактирование собственного объявления."""
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticated]
    # Переопределенный get_queryset определяет,
    # среди каких объявлений представление может искать объект для редактирования.
    # (только среди неудаленных объявлений пользователя, сделавшего запрос.)
    def get_queryset(self):
        return Listing.objects.filter(
            user=self.request.user
            , deleted_at__isnull=True
        )


class CityDistrictListView(ListAPIView):
    """Вернуть районы указанного города."""

    serializer_class = CityDistrictSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """Выбрать районы города, указанного в URL."""
        city = get_object_or_404(
            City,
            pk=self.kwargs["city_id"],
        )

        return city.districts.order_by("name", "pk")