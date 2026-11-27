"""Публичный поиск и просмотр объявлений."""

from django.db.models import Prefetch
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from ..filters import ListingFilter
from ..models import Listing, ListingFile
from ..serializers import ListingListSerializer, ListingSerializer
from ..utils.choices import ListingStatus


class ListingListView(ListAPIView):
    """Вернуть опубликованные объявления активных владельцев."""

    serializer_class = ListingListSerializer
    permission_classes = [AllowAny]
    filterset_class = ListingFilter

    search_fields = ("title", "description")
    ordering_fields = ("price_per_night", "created_at", "id")
    ordering = ("-created_at", "id")

    queryset = (
        Listing.objects
        .filter(
            status=ListingStatus.PUBLISHED,
            user__is_active=True,
            user__deleted_at__isnull=True,
        )
        .defer("description")
        .select_related("city", "city_district")
        .prefetch_related(
            Prefetch(
                "files",
                queryset=ListingFile.objects.order_by("created_at", "pk"),
            )
        )
    )


class ListingDetailView(RetrieveAPIView):
    """Вернуть подробную информацию о публичном объявлении."""

    serializer_class = ListingSerializer
    permission_classes = [AllowAny]

    queryset = (
        Listing.objects
        .filter(
            status=ListingStatus.PUBLISHED,
            user__is_active=True,
            user__deleted_at__isnull=True,
        )
        .select_related("user")
    )