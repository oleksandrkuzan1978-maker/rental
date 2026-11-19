"""Настройки административного списка бронирований."""

from django.contrib import admin
from .models import  Booking

# Register your models here.

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Показывает даты, стоимость и статус бронирования в админке."""

    list_display = ('id', 'user', 'property', 'start_date', 'end_date',
                    'total_price', 'status',
                    "adults", "children", "has_pets")
    readonly_fields = ('id', 'user', 'property', 'start_date', "status", 'end_date', 'total_price', 'description',)
    list_select_related = ('user', 'property')
    search_fields = ('user__email', "property__title")
    list_filter = ("start_date", 'end_date', 'status')
    ordering = ('-created_at',)
