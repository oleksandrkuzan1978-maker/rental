"""Администрирование истории просмотров и поисковых запросов."""

# from itertools import count
from django.contrib import admin
from .models import ListingView, SearchHistory
# from django.contrib import messages
# from django.utils.formats import date_format
# from django.utils import timezone

# Register your models here.

@admin.register(ListingView)
class ListingViewAdmin(admin.ModelAdmin):
    """Настройки поиска и фильтрации просмотров в админке."""

    list_display = ('id', 'listing', 'created_at')
    list_select_related = ('listing',)
    search_fields = ("listing__id",)
    list_filter = ('listing',)
    ordering = ('-created_at',)


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    """Настройки просмотра истории поиска в админке."""

    list_display = ('id', 'user', 'query', 'created_at')
    list_select_related = ('user',)
    search_fields = ('user__email', "query")
    list_filter = ('user',)
    ordering = ('-created_at',)


