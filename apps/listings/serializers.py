from rest_framework import serializers

from .models import Property, PropertyFile, State, City


class PropertyFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyFile
        fields = ['id', 'file']


class PropertySerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = ['id', 'title', 'files']

    def get_files(self, obj):
        files = obj.files.all()

        return PropertyFileSerializer(
            files,
            many=True,
            context=self.context
        ).data


class StateSerializer(serializers.ModelSerializer):

    class Meta:
        model = State
        fields = ("code", "name")


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ("id", "ags", "name", "state")