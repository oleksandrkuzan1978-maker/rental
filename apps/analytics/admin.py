"""Администрирование истории просмотров и поисковых запросов."""

# from itertools import count
from django.contrib import admin
from .models import PropertyView, SearchHistory
# from django.contrib import messages
# from django.utils.formats import date_format
# from django.utils import timezone

# Register your models here.

@admin.register(PropertyView)
class PropertyViewAdmin(admin.ModelAdmin):
    """Настройки поиска и фильтрации просмотров в админке."""

    list_display = ('id', 'created_at')
    list_select_related = ('user', 'property')
    search_fields = ('user__email', "property__id")
    list_filter = ("user__email", 'property_id')
    ordering = ('-created_at',)


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    """Настройки просмотра истории поиска в админке."""

    list_display = ('id', 'query', 'created_at')
    list_select_related = ('user',)
    search_fields = ('user__email', "query")
    list_filter = ('user__email',)
    ordering = ('-created_at',)


