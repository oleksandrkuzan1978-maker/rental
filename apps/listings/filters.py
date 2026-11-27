"""Фильтрация объявлений по местоположению и параметрам жилья."""

from django import forms
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters

from .models import Listing

# проверка параметров фильтрации через форму проще чем через сериализатор
class ListingFilterForm(forms.Form):
    """Проверить согласованность границ поисковых диапазонов."""

    def clean(self):
        """Запретить минимальное значение больше максимального."""
        cleaned_data = super().clean()

        for lower, upper in (
            ("price_min", "price_max"),
            ("rooms_min", "rooms_max"),
        ):
            minimum = cleaned_data.get(lower)
            maximum = cleaned_data.get(upper)

            if (
                minimum is not None
                and maximum is not None
                and minimum > maximum
            ):
                self.add_error(
                    upper,
                    _("The maximum must be greater than or equal to the minimum."),
                )

        return cleaned_data


class ListingFilter(filters.FilterSet):
    """Фильтры публичного списка объявлений."""

    state = filters.CharFilter(
        field_name="city__state_id",
    )

    price_min = filters.NumberFilter(
        field_name="price_per_night",
        lookup_expr="gte",
        min_value=0,
        decimal_places=2,
    )
    price_max = filters.NumberFilter(
        field_name="price_per_night",
        lookup_expr="lte",
        min_value=0,
        decimal_places=2,
    )

    rooms_min = filters.NumberFilter(
        field_name="rooms",
        lookup_expr="gte",
        min_value=0,
        decimal_places=1,
    )
    rooms_max = filters.NumberFilter(
        field_name="rooms",
        lookup_expr="lte",
        min_value=0,
        decimal_places=1,
    )

    class Meta:
        """Модель, стандартные фильтры и проверка диапазонов."""

        model = Listing
        form = ListingFilterForm
        fields = (
            "city",
            "city_district",
            "property_type",
        )