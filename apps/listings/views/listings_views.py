from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from ..models import Listing
from ..serializers import ListingSerializer
from ..utils.choices import ListingStatus

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


