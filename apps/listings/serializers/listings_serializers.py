from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from ..models import Listing, ListingFile
from apps.base.serializers import ContactModelSerializer
from apps.base.services.deletion import lock_active_user
from apps.users.models import User


class ListingFileSerializer(serializers.ModelSerializer):
    """Сериализатор файлов, прикреплённых к объявлению."""

    class Meta:
        """Модель и поля файла в API."""

        model = ListingFile
        fields = ['id', 'file']


class ListingListSerializer(serializers.ModelSerializer):
    """Краткая карточка опубликованного объявления."""

    city_name = serializers.CharField(
        source="city.name",
        read_only=True,
        default=None,
    )
    district_name = serializers.CharField(
        source="city_district.name",
        read_only=True,
        default=None,
    )
    files = ListingFileSerializer(many=True, read_only=True)

    class Meta:
        """Поля карточки, предназначенные для чтения."""

        model = Listing
        fields = ("id", "title", "city", "city_name",
                  "city_district", "district_name", "property_type", "price_per_night",
                  "rooms", "max_guests", "instant_booking_enabled", "files",
        )
        read_only_fields = fields


class ListingSerializer(ContactModelSerializer):
    """Сериализатор объявлений со списком прикреплённых файлов."""
    files = serializers.SerializerMethodField()

    def get_files(self, obj):
        """Вернуть неудалённые вложения неудалённого объявления."""
        if obj.deleted_at is not None:
            return []

        return ListingFileSerializer(
            obj.files.active(),
            many=True,
            context=self.context,
        ).data

    class Meta:
        """Модель и поля объявления в API."""

        model = Listing
        fields = ["id", "user", "title", "description", "property_type",
                  "price_per_night", "rooms", "city", "city_district", "street",
                "house", "apartment", "plz", "status", "files",
                  "show_phone", "show_email",
                  "contact_phone", "contact_email",
                  "max_guests", "pets_allowed", "instant_booking_enabled",
                  "check_in_time", "check_out_time",
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

    @transaction.atomic
    def _save_listing(self, listing_obj):
        """Проверить владельца и состояние объявления перед сохранением."""
        owner = User.objects.get(pk=listing_obj.user_id)

        lock_active_user(user=owner)
        # listing_obj._state.adding — служебный признак Django:
        # - True — объект считается новым и ещё не сохранённым;
        # - False — объект получен из базы или уже был сохранён.
        if not listing_obj._state.adding: # «Если мы редактируем существующее объявление».??? Может, убрать
            # заново получаем объявление из базы. За прошедшее время другой запрос мог мягко удалить объявление.
            current = Listing.objects.select_for_update().get(
                pk=listing_obj.pk,
            )

            if current.deleted_at is not None:
                raise serializers.ValidationError(
                    _("Удалённое объявление нельзя редактировать.")
                )

        try:
            listing_obj.full_clean()
            listing_obj.save()

        except DjangoValidationError as error:
            raise serializers.ValidationError(
                error.message_dict
            ) from error

        except IntegrityError as error:
            if "unique_address" not in str(error):
                raise

            raise serializers.ValidationError({
                "non_field_errors": _(
                    "An ad with this address already exists."
                ),
            }) from error

        return listing_obj