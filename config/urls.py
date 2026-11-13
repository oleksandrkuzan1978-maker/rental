"""Маршруты главной страницы и административного сайта проекта."""

from django.contrib import admin
from django.urls import path
from apps.base.index import index

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
]
