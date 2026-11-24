from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from ..models import City
from ..serializers import CityDistrictSerializer

# Create your views here.

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