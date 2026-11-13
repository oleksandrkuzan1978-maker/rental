from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields  = ['id', 'first_name', 'email', 'password']
        read_only_fields = ('id',)

    def validate_email(self, email):
        email = email.lower()
        if User.objects.filter(email__iexact=email).first():
            raise serializers.ValidationError(_("Email already exists"))
        return email

    def validate(self, attrs):
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
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'email', 'phone', 'created_at', 'updated_at']
        read_only_fields = ('id',) #'first_name', 'email'


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, new_password):
        validate_password(new_password, self.context['request'].user)
        return new_password

    def validate_old_password(self, old_password):
        user = self.context['request'].user
        if not user.check_password(old_password):
            raise serializers.ValidationError(_('The password is incorrect'))
        return old_password

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        if old_password and new_password and new_password == old_password:
            raise serializers.ValidationError(_('Passwords the same'))
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user




