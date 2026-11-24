"""Маршруты API бронирований."""
from django.urls import path

from .views import BookingCreateView,  BookingDecisionView, BookingDetailView

urlpatterns = [
    path('', BookingCreateView.as_view(), name='booking_create'),
    path('<uuid:pk>/', BookingDetailView.as_view(), name='booking_detail'),
    path("<uuid:pk>/decision/", BookingDecisionView.as_view(), name='booking_decision'),
]