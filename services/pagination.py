from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from math import ceil


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data, message=None):
        total = self.page.paginator.count
        page_size = self.get_page_size(self.request)
        total_pages = ceil(total / page_size)

        return Response(
            {
                "is_success": True,
                "message": message,
                "pagination": {
                    "current_page": self.page.number,
                    "page_size": page_size,
                    "total_items": total,
                    "total_pages": total_pages,
                    "has_next": self.page.has_next(),
                    "has_previous": self.page.has_previous(),
                },
                "data": data,
            }
        )
