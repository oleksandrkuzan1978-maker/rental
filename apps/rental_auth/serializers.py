from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model

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
            raise serializers.ValidationError("Email already exists")
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

