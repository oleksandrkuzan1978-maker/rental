"""API создания, просмотра и рассмотрения заявок на бронирование."""
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from django.http import Http404

from rest_framework import serializers
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    RetrieveAPIView, UpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Booking
from .serializers import (
    BookingDecisionSerializer,
    BookingSerializer,
    BookingUpdateSerializer,
)
from .services import decide_booking

class BookingCreateView(CreateAPIView):
    """Создание заявку текущего пользователя на бронирование."""
    serializer_class = BookingSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        """Назначить арендатором авторизованного пользователя."""
        serializer.save(user=self.request.user)


class BookingDetailView(RetrieveAPIView):
    """Показать заявку её арендатору или владельцу объявления."""
    serializer_class = BookingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Доступ к заявке на бронь разрешён, если пользователь
        является арендатором заявки либо владельцем объявления"""
        return (Booking.objects.active().select_related('user', "listing__user")
                .filter(Q(user=self.request.user)
                        | Q(listing__user=self.request.user)))


class BookingDecisionView(GenericAPIView):
    """Принять решение владельца по ожидающей заявке."""
    serializer_class = BookingDecisionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Разрешить доступ к заявкам на собственные объявления."""
        return Booking.objects.filter(
            listing__user=self.request.user,
        )

    def patch(self, request, *args, **kwargs):
        """Подтвердить или отклонить заявку через сервис."""
        # get_object ищет заявку только в разрешённой выборке.
        booking = self.get_object()
        # Проверяем наличие и корректность поля approve.
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            booking = decide_booking(
                user=request.user,
                booking_id=booking.pk,
                approve=serializer.validated_data["approve"],
            )
        except Booking.DoesNotExist:
            # Заявка могла исчезнуть между чтением и вызовом сервиса.
            raise Http404 from None
        except DjangoValidationError as error:
            # Превращаем ошибку сервиса в ответ HTTP 400.
            detail = (
                error.message_dict
                if hasattr(error, "message_dict")
                else {"non_field_errors": error.messages}
            )
            raise serializers.ValidationError(detail) from error

        # Возвращаем фактический результат принятия решения.
        return Response(
            BookingSerializer(
                booking,
                context=self.get_serializer_context(),
            ).data
        )

class BookingUpdateView(UpdateAPIView):
    serializer_class = BookingUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Booking.objects.active().filter(user=self.request.user)












