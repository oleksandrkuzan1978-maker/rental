"""Маршруты объявлений и справочников местоположения."""

from django.urls import path

from .views import (
    CityDistrictListView,
    CityListView,
    ListingDetailView,
    ListingCreateView,
    ListingListView,
    ListingUpdateView,
    MyListingListView,
    StateListView,
)

urlpatterns = [
    path("", ListingListView.as_view(), name="listing_list",),
    path("create/", ListingCreateView.as_view(), name="listing_create"),
    path("mine/", MyListingListView.as_view(), name="my_listing_list",),
    path("states/", StateListView.as_view(), name="state_list",),
    path("states/<str:state_code>/cities/", CityListView.as_view(), name="city_list",),
    path("cities/<int:city_id>/districts/", CityDistrictListView.as_view(), name="city_district_list",),
    path("<uuid:pk>/", ListingUpdateView.as_view(), name="listing_update",),
    path("<uuid:pk>/details/", ListingDetailView.as_view(), name="listing_detail",),
]