from .models import ListingView, SearchHistory


def count_listing_views(*, listing_id=None):
    """Посчитать все просмотры или просмотры одного объявления."""
    views = ListingView.objects.all()

    if listing_id is not None:
        views = views.filter(listing_id=listing_id)

    return views.count()


def count_search_history(*, user_id=None, query=None):
    """Посчитать поисковые запросы с необязательными фильтрами."""
    history = SearchHistory.objects.all()

    if user_id is not None:
        history = history.filter(user_id=user_id)

    if query is not None:
        history = history.filter(query=query)

    return history.count()