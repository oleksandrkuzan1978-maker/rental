from .models import PropertyView, SearchHistory


def count_property_views(*, property_id=None):
    """Посчитать все просмотры или просмотры одного объявления."""
    views = PropertyView.objects.all()

    if property_id is not None:
        views = views.filter(property_id=property_id)

    return views.count()


def count_search_history(*, user_id=None, query=None):
    """Посчитать поисковые запросы с необязательными фильтрами."""
    history = SearchHistory.objects.all()

    if user_id is not None:
        history = history.filter(user_id=user_id)

    if query is not None:
        history = history.filter(query=query)

    return history.count()