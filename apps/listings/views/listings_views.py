from django.db.models import Prefetch

from rest_framework.generics import (
    ListCreateAPIView,
    UpdateAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated

from ..filters import ListingFilter
from ..models import Listing, ListingFile
from ..serializers import ListingSerializer, ListingListSerializer
from ..utils.choices import ListingStatus

# Create your views here.

class ListingListCreateView(ListCreateAPIView):
    """Публичный список объявлений и создание своего объявления."""

    filterset_class = ListingFilter

    search_fields = ("title", "description")
    ordering_fields = ("price_per_night", "created_at", "id")
    ordering = ("-created_at", "id")

    def get_permissions(self):
        """Разрешить просмотр всем, создание — вошедшим пользователям."""
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [AllowAny()]

        return [IsAuthenticated()]

    def get_serializer_class(self):
        """Выбрать краткое представление для списка и форму для создания."""
        if self.request.method == "POST":
            return ListingSerializer

        return ListingListSerializer

    def get_queryset(self):
        """Получить публичные объявления с подготовленными связями."""
        return (
            Listing.objects.active()
            .filter(
                status=ListingStatus.PUBLISHED,
                user__is_active=True,
                user__deleted_at__isnull=True,
            )
            .select_related("city", "city_district")
            .prefetch_related(
                Prefetch(
                    "files",
                    queryset=ListingFile.objects.active().order_by(
                        "created_at",
                        "pk",
                    ),
                )
            )
        )

    def perform_create(self, serializer):
        """Назначить владельцем объявления текущего пользователя."""
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

class ListingDetailView(RetrieveAPIView):
    """Показать посетителю опубликованное неудалённое объявление."""

    serializer_class = ListingSerializer
    permission_classes = [AllowAny]

    queryset = (
        Listing.objects.active()
        .filter(
            status=ListingStatus.PUBLISHED,
            user__is_active=True,
            user__deleted_at__isnull=True,
        )
        .select_related("user")
    )


