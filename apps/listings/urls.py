from django.urls import path

from .views import PropertyCreateView, PropertyUpdateView

urlpatterns = [
    path('', PropertyCreateView.as_view(), name='property_create'),
    path('<uuid:pk>/', PropertyUpdateView.as_view(), name='property_update'),
]