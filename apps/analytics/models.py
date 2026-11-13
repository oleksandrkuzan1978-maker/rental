"""Модели событий просмотра объявлений и поиска жилья."""

from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.base.models import TimeStampModel, UUIDModel, TimeStampMod
from django.conf import settings

from apps.listings.models import Property
# Create your models here.

class PropertyView(TimeStampMod, UUIDModel):
    """Одно открытие страницы объявления."""

    property = models.ForeignKey(Property, on_delete=models.CASCADE
                                 , related_name="views", verbose_name=_('Property'))
    # user может быть NULL, если просмотр объявления доступен незарегистрированным посетителям.
    user = models.ForeignKey(settings.AUTH_USER_MODEL
                             , null=True, blank=True
                             , on_delete=models.SET_NULL
                             , related_name="views", verbose_name=_('User'))

    class Meta:
        """Настройки таблицы и индекса по объявлению и времени просмотра."""

        db_table = 'property_views'
        indexes = [models.Index(fields=['property', 'created_at'], name='property_views_time_idx')]
        ordering = ['-created_at']
        verbose_name = _('Property View')
        verbose_name_plural = _('Property Views')

        ## Внутри обработчика после получения доступного посетителю объявления.
            # if request.method == "GET":
            #     PropertyView.objects.create(
            #         property=listing,
            #         user=request.user if request.user.is_authenticated else None,
            #     )


        # Как посчитать просмотры за период?
        # views_count = PropertyView.objects.filter(
        #     property=listing,
        #     created_at__gte=period_start,
        #     created_at__lt=period_end,
        # ).count()


class SearchHistory(TimeStampMod, UUIDModel):
    """Один поисковый запрос посетителя."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL
                             , on_delete=models.SET_NULL
                             , null=True, blank=True
                             , related_name="search_history", verbose_name=_('User'))
    query = models.CharField(max_length=255, verbose_name=_('Query'))

    class Meta:
        """Настройки таблицы и сортировки запросов по времени."""

        db_table = 'search_history'
        ordering = ['-created_at']
        verbose_name = _('Search history entry')
        verbose_name_plural = _('Search history')

        # Когда сохранять запрос
        # В обработчике поиска записывайте фразу после проверки ввода, при отправке нового поиска.
        # В форме или сериализаторе ограничьте длину 255 символами и уберите пробелы по краям.
        # Пустой ввод можно использовать для показа всех объявлений, не создавая запись в истории.

        # В обработчике отправки нового поиска, после валидации формы.
        # query = form.cleaned_data["query"]
        #
        # if query:
        #     SearchHistory.objects.create(
        #         query=query,
        #         user=request.user if request.user.is_authenticated else None,
        #     )

        # Как получить популярные запросы за период
        # from django.db.models import Count
        #
        # popular_queries = (
        #     SearchHistory.objects
        #     .filter(created_at__gte=period_start, created_at__lt=period_end)
        #     .values("query")
        #     .annotate(search_count=Count("pk"))
        #     .order_by("-search_count", "query")[:10]
        # )

        # .values("query") группирует записи по фразе, а Count("pk") считает все строки в каждой группе.
        # Для вашего примера результат будет Wohnung Berlin — 2, Haus Dortmund — 1.