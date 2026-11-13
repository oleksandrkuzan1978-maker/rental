"""Маршруты главной страницы и административного сайта проекта."""

from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path, include
from apps.base.index import index

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),

    path('api/v1/auth/', include('apps.rental_auth.urls')),
]
