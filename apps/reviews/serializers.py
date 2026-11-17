from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.bookings.models import Booking
from apps.reviews.models import Review


class ReviewListSerializer(serializers.ModelSerializer):
    pass


class ReviewCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ['id', 'booking', 'rating', 'comment']
        read_only_fields = ['id']

    def validate(self, attrs):
        booking = attrs['booking']
        user = self.context['request'].user

        if booking.user_id != user.id:
            raise serializers.ValidationError({
                'booking': _('You can only review your own bookings.')
            })

        if booking.status != Booking.Status.COMPLETED:
            raise serializers.ValidationError({
                'booking': _('Only completed bookings can be reviewed.')
            })

        if booking.end_date >= timezone.localdate():
            raise serializers.ValidationError({
                'booking': _('A review can only be submitted after the booking ends.')
            })

        return attrs


class ReviewUpdateSerializer(serializers.ModelSerializer):

    class Meta:
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



