from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.bookings.models import Booking
from apps.reviews.models import Review
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.serializers import as_serializer_error

from .services import create_review

class ReviewListSerializer(serializers.ModelSerializer):
    """Заготовка сериализатора для списка отзывов."""

    pass


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Принять данные и создать отзыв через сервис."""

    class Meta:
        """Поля создания отзыва."""

        model = Review
        fields = ("id", "booking", "rating", "comment")
        read_only_fields = ("id",)

    def create(self, validated_data):
        """Создать отзыв на собственную завершённую бронь."""
        booking = validated_data["booking"]

        try:
            return create_review(
                user=self.context["request"].user,
                booking_id=booking.pk,
                rating=validated_data["rating"],
                comment=validated_data.get("comment", ""),
            )

        except Booking.DoesNotExist:
            raise serializers.ValidationError({
                "booking": _("The booking no longer exists."),
            }) from None

        except DjangoValidationError as error:
            raise serializers.ValidationError(
                as_serializer_error(error)
            ) from error


class ReviewUpdateSerializer(serializers.ModelSerializer):

    """Принять новую оценку и текст существующего отзыва."""

    class Meta:
        """Разрешить обновление оценки и текста отзыва."""

        model = Review
        fields = ['rating', 'comment']
    # Если переопределить метод get_queryset во вьюшке как показано ниже или создать пермишн, то этот валидейт можно убрать
    # def validate(self, attrs):
    #     user = self.context['request'].user
    #
    #     if self.instance.booking.user_id != user.id:
    #         raise serializers.ValidationError(
    #             _('You can only edit your own reviews.')
    #         )
    #
    #     return attrs


# class ReviewViewSet(ModelViewSet):
#
#     queryset = Review.objects.select_related(
#         'booking', 'booking__user'
#     ).all()
#
#     def get_queryset(self):
#         if self.action in ['update', 'partial_update', 'destroy']:
#             return Review.objects.filter(
#                 booking__user=self.request.user
#             ).select_related('booking')
#
#         return super().get_queryset()
#
#     def get_serializer_class(self):
#         if self.action == 'create':
#             return ReviewCreateSerializer
#
#         if self.action in ['update', 'partial_update']:
#             return ReviewUpdateSerializer
#
#         return ReviewListSerializer



