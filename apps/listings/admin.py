"""Администрирование объявлений, вложений, адресов и городов."""
from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect

from .models import  Listing, ListingFile, City
from .utils.services import save_listing_file
from apps.base.admin import SuperuserDeleteAdminMixin

# Register your models here.
@admin.register(Listing)
class ListingAdmin(SuperuserDeleteAdminMixin, admin.ModelAdmin):
    """Настройки просмотра и редактирования объявлений в админке."""

    list_display = ('id', 'title', "description", "user", 'price_per_night'
                        , 'property_type', 'status', 'created_at'
                        , "city", "city_district", "street", "house", "apartment", "plz")
    list_select_related = ('user', "city", "city_district")
    search_fields = ('title', 'description'
                         , "street", "house", "plz", "city__name")
    list_filter = ("city__state", "price_per_night", 'status', 'property_type', 'created_at')
    autocomplete_fields = ("city",)
    ordering = ('-created_at',)


@admin.register(ListingFile)
class ListingFileAdmin(SuperuserDeleteAdminMixin, admin.ModelAdmin):
    """Управление вложениями с проверкой лимита файлов объявления."""

    list_display = ("id", "title", "listing", "file")
    list_select_related = ("listing",)
    search_fields = ("title", "listing__title")
    ordering = ("title", "-created_at")

    def get_readonly_fields(self, request, obj=None):
        """Запретить ручное изменение даты удаления и связи вложения."""
        if obj is not None:
            return ("listing", "deleted_at")

        return ("deleted_at",)

    def save_model(self, request, obj, form, change):
        """Сохранить вложение через общий сервис."""
        save_listing_file(attachment=obj)

    def changeform_view(
        self,
        request,
        object_id=None,
        form_url="",
        extra_context=None,
    ):
        """Показать сообщение, если сервис отклонил сохранение."""
        try:
            return super().changeform_view(
                request,
                object_id=object_id,
                form_url=form_url,
                extra_context=extra_context,
            )
        except ValidationError as error:
            self.message_user(
                request,
                " ".join(error.messages),
                level=messages.ERROR,
            )
            return redirect(request.path)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Настройки поиска городов и фильтрации по федеральной земле."""

    list_display = ("id", "name", 'ags', 'state')
    list_select_related = ("state",)
    search_fields = ("name", 'state__name')
    list_filter = ("state",)
