
from rest_framework.pagination import CursorPagination


class DefaultCursorPaginationClass(CursorPagination):
    ordering = ('-updated_at', '-created_at', )
    cursor_query_param = 'uid'
    page_size = 40


class SearchCursorPaginationClass(DefaultCursorPaginationClass):
    page_size = 32
