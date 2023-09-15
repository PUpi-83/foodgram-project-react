from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Пагинация по лимиту на странице."""

    page_size_query_param = "limit"
