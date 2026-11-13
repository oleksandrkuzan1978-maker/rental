"""Настройки административного списка отзывов арендаторов."""

# from itertools import count
from django.contrib import admin
from .models import  Review
# from django.contrib import messages
# from django.utils.formats import date_format
# from django.utils import timezone

# Register your models here.

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Настройки просмотра и поиска отзывов в админке."""

    list_display = ('id', 'rating', 'comment')
    list_select_related = ('user', 'property', 'booking')
    search_fields = ('user__email', "property__title", "rating")
    list_filter = ("user__email",)
    ordering = ('-rating',)

# Register your models here.
