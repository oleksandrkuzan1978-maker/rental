import phonenumbers

from django.db import IntegrityError, transaction
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


User = get_user_model()

class ProfileUserSerializer(serializers.ModelSerializer):
    """Просмотр профиля и изменение имени и телефона."""

    phone=serializers.CharField(required=False, allow_blank=True, max_length=100)
    phone_country=serializers.ChoiceField(choices=sorted(phonenumbers.SUPPORTED_REGIONS),
                                          required=False, write_only=True,)

    class Meta:
        model = User
        fields = ["id", "name", "email",
            "phone", "phone_country", "created_at", "updated_at",]
        read_only_fields = ["id", "email", "created_at", "updated_at",]

    def validate(self, attrs):
        attrs = super().validate(attrs)

        country = attrs.pop("phone_country", None)
        phone = attrs.get("phone")

        # Телефон не изменяется или пользователь удаляет его.
        if phone is None or phone == "":
            return attrs
        if not phone.startswith("+") and country is None:
            raise serializers.ValidationError({
                "phone_country": _(
                    "Select a country for the phone number, excluding the international code."
                ),
            })
        try:
            number = phonenumbers.parse(phone, country)
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError({
                "phone": _("Could not recognize the number. Please check the number and the country.")
            }) from None

        if not phonenumbers.is_valid_number(number):
            raise serializers.ValidationError({
                "phone": _("Phone number is not valid. Please check the phone number."),
            })
        attrs["phone"] = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164,)

        return attrs

class ChangeEmailSerializer(serializers.Serializer):
    """Смена email текущего пользователя."""

    email = serializers.EmailField(max_length=150)
    current_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate_current_password(self, value):
        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError(
                _("Incorrect current password.")
            )

        return value

    def validate_email(self, value):
        email = value.strip().lower()
        user = self.context["request"].user

        if User.objects.filter(
            email__iexact=email,
        ).exclude(pk=user.pk).exists():
            raise serializers.ValidationError(
                _("This email is already in use.")
            )

        return email

    def update(self, instance, validated_data):
        email = validated_data["email"]

        try:
            with transaction.atomic():
                instance.email = email
                instance.save(update_fields=["email", "updated_at"])
        except IntegrityError as error:
            # Адрес мог занять другой запрос после проверки.
            email_taken = User.objects.filter(
                email__iexact=email,
            ).exclude(pk=instance.pk).exists()

            if email_taken:
                raise serializers.ValidationError({
                    "email": _("This email is already in use."),
                }) from error

            raise

        return instance
