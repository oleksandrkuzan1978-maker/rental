from rest_framework import serializers

class ContactModelSerializer(serializers.ModelSerializer):
    """Контакты пользователя с учётом настроек их показа."""
    contact_phone = serializers.SerializerMethodField()
    contact_email = serializers.SerializerMethodField()

    def get_contact_phone(self, obj):
        if obj.show_phone:
            return obj.user.phone
        return ""

    def get_contact_email(self, obj):
        if obj.show_email:
            return obj.user.email
        return ""