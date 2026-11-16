from rest_framework import serializers

from .models import Property, PropertyFile, State, City


class PropertyFileSerializer(serializers.ModelSerializer):
    """Сериализатор файлов, прикреплённых к объявлению."""

    class Meta:
        """Модель и поля файла в API."""

        model = PropertyFile
        fields = ['id', 'file']


class PropertySerializer(serializers.ModelSerializer):
    """Сериализатор объявлений со списком прикреплённых файлов."""

    files = serializers.SerializerMethodField()

    class Meta:
        """Модель и поля объявления в API."""

        model = Property
        fields = ['id', 'title', 'files']

    def get_files(self, obj):
        """Вернуть сериализованные данные всех прикреплённых к объявлению файлов."""
        files = obj.files.all()

        return PropertyFileSerializer(
            files,
            many=True,
            context=self.context
        ).data


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