"""Модели событий просмотра объявлений и поиска жилья."""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from apps.listings.models import Listing
from apps.base.managers import DeleteQuerySet
from apps.base.models import UUIDModel, ProtectedDeleteModel
# Create your models here.

class ListingView(UUIDModel, ProtectedDeleteModel):
    """Одно открытие страницы объявления."""

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE
                                , related_name="views", verbose_name=_('Listing'))
    created_at = models.DateTimeField(auto_now_add=True)

    objects = DeleteQuerySet.as_manager()

    class Meta:
        """Настройки таблицы и индекса по объявлению и времени просмотра."""

        db_table = 'listing_views'
        indexes = [models.Index(fields=['listing', 'created_at'], name='listing_views_time_idx')]
        ordering = ['-created_at']
        verbose_name = _('Listing View')
        verbose_name_plural = _('Listing Views')

        ## Внутри обработчика после получения доступного посетителю объявления.
            # if request.method == "GET":
            #     ListingView.objects.create(listing=listing)

        # Как посчитать просмотры за период?
        # views_count = ListingView.objects.filter(
        #     listing=listing,
        #     created_at__gte=period_start,
        #     created_at__lt=period_end,
        # ).count()


class SearchHistory(UUIDModel, ProtectedDeleteModel):
    """Один поисковый запрос посетителя."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL
                             , on_delete=models.SET_NULL
                             , null=True, blank=True
                             , related_name="search_history", verbose_name=_('User'))
    query = models.CharField(max_length=255, verbose_name=_('Query'))
    created_at = models.DateTimeField(auto_now_add=True)

    objects = DeleteQuerySet.as_manager()

    class Meta:
        """Настройки таблицы и сортировки запросов по времени."""

        db_table = 'search_history'
        ordering = ['-created_at']
        verbose_name = _('Search history entry')
        verbose_name_plural = _('Search history')

        # Когда сохранять запрос
        # В обработчике поиска записывать фразу после проверки ввода, при отправке нового поиска.
        # В форме или сериализаторе ограничить длину 255 символами и убрать пробелы по краям.
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
        # Для примера результат будет Wohnung Berlin — 2, Haus Dortmund — 1.