"""Настройки административного списка отзывов арендаторов."""

# from itertools import count
from django.contrib import admin
from .models import  Review
from apps.base.admin import SuperuserDeleteAdminMixin
# from django.contrib import messages
# from django.utils.formats import date_format
# from django.utils import timezone

# Register your models here.

@admin.register(Review)
class ReviewAdmin(SuperuserDeleteAdminMixin, admin.ModelAdmin):
    """Настройки просмотра и поиска отзывов в админке."""

    list_display = ('id', 'rating', 'comment')
    list_select_related = ("booking__user", "booking__listing")
    search_fields = ('booking__user__email', "booking__listing__title", "rating")
    list_filter = ("rating", "booking__status",)
    ordering = ('-rating',)

    def has_add_permission(self, request):
        """Запретить создание отзывов через административную панель."""
        return False

# Нижеследующие методы убрать, так как зачем нам создавать или менять отзывы через админку.
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         """Настроить выбор бронирования, ограничив его бронями текущего пользователя с заданным статусом."""
#         if db_field.name == "booking":
#             kwargs["queryset"] = Booking.objects.filter(user_id=request.user.pk
#                                                         , status=Booking.Status.COMPLETED)
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)
#
#     def has_change_permission(self, request, obj: Review | None = None) -> bool:
#         """Проверить право Django на изменение отзыва и принадлежность его брони пользователю."""
#         if not super().has_change_permission(request, obj):
#             return False
#
#         if obj is None:
#             return True
#
#         return is_booking_tenant(user=request.user, booking=obj.booking)
#
#     def get_readonly_fields(self, request, obj=None):
#         """Вернуть поля только для чтения, включая бронь существующего отзыва."""
#         readonly_fields = super().get_readonly_fields(request, obj)
#         if obj is not None:
#             return *readonly_fields, "booking"
#         return readonly_fields
