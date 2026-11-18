from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

EMAIL_TAKEN = _("Email already exists")

def email_exists(email):
    """Проверить, занят ли email, без учёта регистра."""
    return User.objects.filter(email__iexact=email).exists()

class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя по имени, email и паролю."""

    password = serializers.CharField(write_only=True)
    class Meta:
        """Модель и поля формы регистрации."""

        model = User
        fields  = ['id', 'name', 'email', 'password']
        read_only_fields = ('id',)

    def validate_email(self, email):
        """Привести email к нижнему регистру и проверить, что он свободен."""
        email = email.lower()
        if User.objects.filter(email__iexact=email).first():
            raise serializers.ValidationError(EMAIL_TAKEN)
        return email

    def validate(self, attrs):
        """Проверить пароль по правилам Django с учётом данных пользователя."""
        attrs_without_password = attrs.copy()
        attrs_without_password.pop('password')

        user = User(**attrs_without_password)
        password = attrs['password']

        try:
            validate_password(password, user)
        except DjangoValidationError as error:
            raise serializers.ValidationError({'password': list(error.messages)})

        return attrs

    def create(self, validated_data):
        """Создать пользователя и сообщить об ошибке, если email уже занят."""
        try:
            with transaction.atomic():
                return User.objects.create_user(**validated_data)
        except IntegrityError as e:
            # Другой запрос мог занять email после проверки.
            if email_exists(validated_data["email"]):
                raise serializers.ValidationError({'email': EMAIL_TAKEN}) from e
            raise
    # def create(self, validated_data):
    #     return User.objects.create_user(**validated_data)


class LoginSerializer(TokenObtainPairSerializer):
    """Сериализатор логирования пользователя."""
    def validate(self, attrs):
        attrs["email"] = attrs["email"].strip().lower()
        return super().validate(attrs)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя."""

    class Meta:
        """Модель и поля профиля пользователя в API."""

        model = User
        fields = ['id', 'name', 'email', 'phone', 'created_at', 'updated_at']
        read_only_fields = ('id',) #'name', 'email'


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор смены пароля для текущего пользователя."""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, new_password):
        """Проверить новый пароль по правилам Django и вернуть его."""
        validate_password(new_password, self.context['request'].user)
        return new_password

    def validate_old_password(self, old_password):
        """Проверить старый пароль по сохранённому паролю пользователя."""
        user = self.context['request'].user
        if not user.check_password(old_password):
            raise serializers.ValidationError(_('The password is incorrect'))
        return old_password

    def validate(self, attrs):
        """Проверить, что новый пароль отличается от старого."""
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        if old_password and new_password and new_password == old_password:
            raise serializers.ValidationError(_('Passwords the same'))
        return attrs

    def save(self, **kwargs):
        """Сохранить хеш нового пароля и вернуть текущего пользователя."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user




