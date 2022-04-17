from rest_framework import pagination


class NewestIdLastCursorPagination(pagination.CursorPagination):
    ordering = "id"


class NewestIdFirstCursorPagination(pagination.CursorPagination):
    ordering = "-id"
