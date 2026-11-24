"""Сериализаторы справочников местоположения."""

from rest_framework import serializers

from ..models import City, CityDistrict, State


class StateSerializer(serializers.ModelSerializer):
    """Представить федеральную землю."""

    class Meta:
        """Поля справочника земель."""

        model = State
        fields = ("code", "name")


class CitySerializer(serializers.ModelSerializer):
    """Представить город и его федеральную землю."""

    class Meta:
        """Поля справочника городов."""

        model = City
        fields = ("id", "ags", "name", "state")


class CityDistrictSerializer(serializers.ModelSerializer):
    """Представить район города для выбора адреса."""

    class Meta:
        """Поля справочника районов."""

        model = CityDistrict
        fields = ("id", "city", "code", "name")
        read_only_fields = ("id", "city", "code", "name")

