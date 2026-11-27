"""Публичные справочники земель, городов и районов."""

from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter

from ..models import City, State
from ..serializers import (
    CityDistrictSerializer,
    CitySerializer,
    StateSerializer,
)


class StateListView(ListAPIView):
    """Вернуть федеральные земли для выбора местоположения."""

    serializer_class = StateSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = []

    queryset = State.objects.order_by("name", "pk")


class CityListView(ListAPIView):
    """Вернуть города выбранной федеральной земли."""

    serializer_class = CitySerializer
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        """Проверить существование земли и выбрать её города."""
        state = get_object_or_404(
            State,
            pk=self.kwargs["state_code"],
        )
        return state.cities.order_by("name", "pk")


class CityDistrictListView(ListAPIView):
    """Вернуть районы выбранного города."""

    serializer_class = CityDistrictSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = []

    def get_queryset(self):
        """Проверить существование города и выбрать его районы."""
        city = get_object_or_404(
            City,
            pk=self.kwargs["city_id"],
        )
        return city.districts.order_by("name", "pk")