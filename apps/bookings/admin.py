"""Настройки административного списка бронирований."""

from itertools import count
from django.contrib import admin
from .models import  Booking
from django.contrib import messages
from django.utils.formats import date_format
from django.utils import timezone

# Register your models here.

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Показывает даты, стоимость и статус бронирования в админке."""

    list_display = ('id', 'start_date', 'end_date', 'total_price', 'status')
    readonly_fields = ('id', 'start_date', 'end_date', 'total_price', 'status', 'property', 'user',)
    list_select_related = ('user', 'property')
    search_fields = ('user__email', "property__title", "created_at")
    list_filter = ("start_date", 'end_date')
    ordering = ('-created_at',)
