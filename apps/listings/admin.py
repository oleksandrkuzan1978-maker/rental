"""Администрирование объявлений, вложений, адресов и городов."""

from itertools import count
from django.contrib import admin
from .models import  Property, PropertyFile, Address, City
from django.contrib import messages
from django.utils.formats import date_format
from django.utils import timezone

# Register your models here.
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """Настройки просмотра и редактирования объявлений в админке."""

    list_display = ('id', 'title', "description", 'price_per_night', 'is_active', 'created_at')
    list_editable = ('title', 'description', 'is_active')
    list_select_related = ('user', 'address')
    search_fields = ('title', 'description', "is_active", "created_at", 'price_per_night')
    ordering = ('-created_at',)


@admin.register(PropertyFile)
class PropertyFileAdmin(admin.ModelAdmin):
    """Настройки административного списка вложений."""

    list_display = ('title', 'file')
    list_select_related = ('property',)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Настройки поиска, фильтрации и редактирования адресов."""

    list_display = ("id", "property", "city", "street", "house", "plz")
    list_editable = ("street", "house", "plz")
    list_select_related = ("property", "city")
    search_fields = ("street", "house", "plz", "city__name", "property__title")
    list_filter = ("city__state",)
    ordering = ("city__name", "street", "house")


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Настройки поиска городов и фильтрации по федеральной земле."""

    list_display = ("name",)
    list_select_related = ("state",)
    search_fields = ("name", 'state__name')
    list_filter = ("state__name",)





