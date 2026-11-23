from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.base.serializers import ContactModelSerializer
from .models import Booking
from .utils.services import create_booking


class BookingSerializer(ContactModelSerializer):
    """Создание и представление бронирования."""
    guests_count = serializers.IntegerField(read_only=True)

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
        ]
        read_only_fields = ["id", "user", "total_price", "status",] # поля включаются в ответ,
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

class BookingUpdateSerializer(ContactModelSerializer):
    """Редактирование описания и настроек контактов бронирования."""
    class Meta:
        model = Booking
        fields = [
            "id", "user", "listing", "start_date",
        ]