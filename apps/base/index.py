"""Текстовая главная страница проекта."""
from django.http import HttpResponse

def index(request):
    """Вернуть текст главной страницы проекта."""
    return HttpResponse("Главная страница")