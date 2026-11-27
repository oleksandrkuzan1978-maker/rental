"""Создание, редактирование и просмотр собственных объявлений."""

from django.db.models import Prefetch
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated

from ..filters import ListingFilter
from ..models import Listing, ListingFile
from ..serializers import ListingListSerializer, ListingSerializer


class ListingCreateView(CreateAPIView):
    """Создать объявление от имени текущего пользователя."""

    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Назначить текущего пользователя владельцем объявления."""
        serializer.save(user=self.request.user)


class MyListingListView(ListAPIView):
    """Вернуть собственные неудалённые объявления всех статусов."""

    serializer_class = ListingListSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ListingFilter

    search_fields = ("title", "description")
    ordering_fields = ("price_per_night", "created_at", "id")
    ordering = ("-created_at", "id")

    def get_queryset(self):
        """Выбрать объявления текущего пользователя со связанными данными."""
        return (
            Listing.objects
            .filter(user=self.request.user)
            .select_related("city", "city_district")
            .prefetch_related(
                Prefetch(
                    "files",
                    queryset=ListingFile.objects.order_by("created_at", "pk"),
                )
            )
        )


class ListingUpdateView(UpdateAPIView):
    """Разрешить владельцу редактировать своё неудалённое объявление."""

    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Ограничить доступ объявлениями текущего пользователя."""
        return (
            Listing.objects
            .filter(user=self.request.user)
            .select_related("user")
        )