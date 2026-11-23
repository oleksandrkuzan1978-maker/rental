from django.urls import path

from .views import ListingCreateView, ListingUpdateView

urlpatterns = [
    path('', ListingCreateView.as_view(), name='listing_create'),
    path('<uuid:pk>/', ListingUpdateView.as_view(), name='listing_update'),
]