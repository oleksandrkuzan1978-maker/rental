from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Property, PropertyFile, State, City


class PropertyFileSerializer(serializers.ModelSerializer):
    """Сериализатор файлов, прикреплённых к объявлению."""

    class Meta:
        """Модель и поля файла в API."""

        model = PropertyFile
        fields = ['id', 'file']


class PropertySerializer(serializers.ModelSerializer):
    """Сериализатор объявлений со списком прикреплённых файлов."""

    files = PropertyFileSerializer(many=True, read_only=True)

    class Meta:
        """Модель и поля объявления в API."""

        model = Property
        fields = ["id", "user", "title", "description", "property_type",
                  "price_per_night", "rooms", "city", "city_district", "street",
                "house", "plz", "status", "files",]
        read_only_fields = ["id", "user"]

    def create(self, validated_data):
        property_obj = Property(**validated_data)
        return self._save_property(property_obj)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        return self._save_property(instance)
    # переопределение create и update нужно для вызова full_clean,
    # чтобы перед каждым сохранением объявления выполнялись проверки из Property.clean()
    # (обычный save() автоматически эти проверки не запускает)
    def _save_property(self, property_obj):
        """Проверить модель и сохранить объявление."""
        try:
            property_obj.full_clean()
        except DjangoValidationError as error:
            # Если нужно выводить каждую ошибку возле соответствующего поля формы,
            # тогда сообщения выводим в таком виде
            detail=(error.message_dict
                    if hasattr(error, 'message_dict')
                    else {"non_field_errors": error.messages})
            raise serializers.ValidationError(detail) from error

        property_obj.save()
        return property_obj


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