from rest_framework import serializers

from .models import Property, PropertyFile


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
        files = obj.files.filter(is_deleted=False)

        return PropertyFileSerializer(
            files,
            many=True,
            context=self.context
        ).data