from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Listing, ListingFile, State, City
from apps.base.serializers import ContactModelSerializer


class ListingFileSerializer(serializers.ModelSerializer):
    """Сериализатор файлов, прикреплённых к объявлению."""

    class Meta:
        """Модель и поля файла в API."""

        model = ListingFile
        fields = ['id', 'file']


class ListingSerializer(ContactModelSerializer):
    """Сериализатор объявлений со списком прикреплённых файлов."""
    files = ListingFileSerializer(many=True, read_only=True)

    class Meta:
        """Модель и поля объявления в API."""

        model = Listing
        fields = ["id", "user", "title", "description", "property_type",
                  "price_per_night", "rooms", "city", "city_district", "street",
                "house", "apartment", "plz", "status", "files",
                  "show_phone", "show_email",
                  "contact_phone", "contact_email",
                  "max_guests", "pets_allowed", "instant_booking_enabled",
                  ]
        read_only_fields = ["id", "user"]

    def create(self, validated_data):
        listing_obj = Listing(**validated_data)
        return self._save_listing(listing_obj)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        return self._save_listing(instance)
    # переопределение create и update нужно для вызова full_clean,
    # чтобы перед каждым сохранением объявления выполнялись проверки из Property.clean()
    # (обычный save() автоматически эти проверки не запускает)
    def _save_listing(self, listing_obj):
        """Проверить модель и сохранить объявление."""
        try:
            listing_obj.full_clean()
        except DjangoValidationError as error:
            # Если нужно выводить каждую ошибку возле соответствующего поля формы,
            # тогда сообщения выводим в таком виде
            detail=(error.message_dict
                    if hasattr(error, 'message_dict')
                    else {"non_field_errors": error.messages})
            raise serializers.ValidationError(detail) from error

        listing_obj.save()
        return listing_obj


class StateSerializer(serializers.ModelSerializer):
    """Сериализатор федеральных земель."""

    class Meta:
        """Модель и поля федеральной земли в API."""

        model = State
        fields = ("code", "name")


class CitySerializer(serializers.ModelSerializer):
    """Сериализатор городов с указанием федеральной земли."""

    class Meta:
        """Модель и поля города в API."""

        model = City
        fields = ("id", "ags", "name", "state")