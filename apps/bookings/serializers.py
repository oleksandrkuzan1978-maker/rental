from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.serializers import as_serializer_error

from apps.base.serializers import ContactModelSerializer
from .models import Booking
from .services import create_booking, update_booking
from .utils.variables import EDITABLE_BOOKING_FIELDS


class BookingSerializer(ContactModelSerializer):
    """Создание и представление бронирования."""
    guests_count = serializers.IntegerField(read_only=True)
    # Поле decision_reason_display дает пользователю понятное название причины решения.
    decision_reason_display = serializers.CharField(
        source="get_decision_reason_display",
        read_only=True,
    )

    # Статус бронирования остаётся только для чтения
    # — подтверждение, отмена и завершение заявки требуют собственных правил доступа.
    class Meta:
        model = Booking
        fields = [
            "id", "user", "listing", "start_date",
            "end_date", "description", "total_price", "status",
            "adults",
            "children",
            "guests_count",
            "has_pets",
            "show_phone", "show_email",
            "contact_phone", "contact_email",
            "requires_owner_approval", "decision_reason",
            "decision_reason_display", "decided_at", "review_deadline",
            "edit_count"
        ]
        read_only_fields = ["id", "user", "total_price", "status", "edit_count",
                            "decision_reason", "decided_at", "review_deadline",] # поля включаются в ответ,
                                                                # Но переданные клиентом значения
                                                                # игнорируются при проверке входящих данных.
                                                                # Их назначает сервер.
    def create(self, validated_data):
        listing_obj = validated_data.pop("listing")
        try:
            return create_booking(listing_id=listing_obj.pk,
                                  **validated_data)
        except DjangoValidationError as error:
            detail = (
                error.message_dict
                if hasattr(error, "message_dict")
                else {"non_field_errors": error.messages}
            )
            raise serializers.ValidationError(detail) from error


class BookingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = EDITABLE_BOOKING_FIELDS

    def update(self, instance, validated_data):
        try:
            return update_booking(
                user=self.context["request"].user,
                booking_id=instance.pk,
                changes=validated_data,
            )
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                as_serializer_error(error)
            ) from error

    def to_representation(self, instance):
        return BookingSerializer(
            instance,
            context=self.context,
        ).data


class BookingDecisionSerializer(serializers.Serializer):
    """Решение владельца по ожидающей заявке."""

    approve = serializers.BooleanField()