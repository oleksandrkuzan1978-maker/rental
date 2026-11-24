from django.db import IntegrityError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from ..models import Listing, ListingFile
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
    # чтобы перед каждым сохранением объявления выполнялись проверки из Listing.clean()
    # (обычный save() автоматически эти проверки не запускает)
    def _save_listing(self, listing_obj):
        """Проверить модель и сохранить объявление."""
        try:
            listing_obj.full_clean()
            listing_obj.save()
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.message_dict) from error
        except IntegrityError as error:
            if "unique_address" not in str(error):
                raise
            raise serializers.ValidationError({"non_field_errors":
                                                _("An ad with this address already exists.")}) from error

        return listing_obj