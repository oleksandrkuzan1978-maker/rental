"""Пагинация списков в REST API проекта rental."""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class RentalPageNumberPagination(PageNumberPagination):
    """Пагинация по номерам страниц с настраиваемым размером страницы."""

    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20

    def get_paginated_response(self, data):
        """Вернуть данные страницы, её номер, размеры и ссылки."""
        return Response({
            'count': self.page.paginator.count,
            'results': data,
            'page': self.page.number,
            'page_size': self.page.paginator.per_page,
            'total_pages': self.page.paginator.num_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
        })

