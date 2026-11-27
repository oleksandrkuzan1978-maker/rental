from django.urls import path

from .views import ListingListCreateView, ListingUpdateView, ListingDetailView, CityDistrictListView

urlpatterns = [
    path('', ListingListCreateView.as_view(), name='listing_create'),
    path('<uuid:pk>/', ListingUpdateView.as_view(), name='listing_update'),
    path("cities/<int:city_id>/districts/", CityDistrictListView.as_view(), name="city_district_list"),
    path("<uuid:pk>/details/", ListingDetailView.as_view(), name="listing_detail"),
]