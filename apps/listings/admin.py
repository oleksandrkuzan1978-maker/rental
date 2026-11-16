"""Администрирование объявлений, вложений, адресов и городов."""
from django.contrib import admin
from .models import  Property, PropertyFile, City


# Register your models here.
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """Настройки просмотра и редактирования объявлений в админке."""

    list_display = ('id', 'title', "description", 'price_per_night'
                        , 'property_type', 'is_active', 'created_at'
                        , "city", "street", "house", "plz")
    list_editable = ('title', 'description', 'is_active'
                         , "street", "house", "plz")
    list_select_related = ('user', "city")
    search_fields = ('title', 'description'
                         , "street", "house", "plz", "city__name")
    list_filter = ("city__state", "price_per_night", 'title', 'property_type', 'created_at')
    autocomplete_fields = ("city",)
    ordering = ('-created_at',)


@admin.register(PropertyFile)
class PropertyFileAdmin(admin.ModelAdmin):
    """Настройки административного списка вложений."""

    list_display = ('title', 'file')
    list_select_related = ('property',)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Настройки поиска городов и фильтрации по федеральной земле."""

    list_display = ("name",)
    list_select_related = ("state",)
    search_fields = ("name", 'state__name')
    list_filter = ("state__name",)
