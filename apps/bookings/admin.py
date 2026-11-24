"""Настройки административного списка бронирований."""

from django.contrib import admin
from .models import  Booking

# Register your models here.

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Показывает даты, стоимость и статус бронирования в админке."""

    list_display = ('id', 'user', 'listing', 'start_date', 'end_date',
                    'total_price', 'status',
                    "adults", "children", "has_pets",
                    "requires_owner_approval", "decision_reason", "decided_at", "review_deadline",)
    readonly_fields = ('id', 'user', 'listing', 'start_date',
                       "status", 'end_date', 'total_price', 'description',
                       "adults", "children", "has_pets",
                       "requires_owner_approval", "decision_reason", "decided_at", "review_deadline",
                       )
    list_select_related = ('user', 'listing')
    search_fields = ('user__email', "listing__title")
    list_filter = ("start_date", 'end_date', 'status')
    ordering = ('-created_at',)
    # Метод has_add_permission Django вызывает, чтобы узнать,
    # разрешено ли добавление объектов через стандартную админку.
    def has_add_permission(self, request):
        """Запретить стандартное создание брони через админку."""
        return False
