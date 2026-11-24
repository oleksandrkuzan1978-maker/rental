from django.urls import path

from .views import ListingCreateView, ListingUpdateView, CityDistrictListView

urlpatterns = [
    path('', ListingCreateView.as_view(), name='listing_create'),
    path('<uuid:pk>/', ListingUpdateView.as_view(), name='listing_update'),
    path("cities/<int:city_id>/districts/", CityDistrictListView.as_view(), name="city_district_list"),
]