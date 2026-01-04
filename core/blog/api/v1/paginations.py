from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

# Page-number pagination with custom metadata fields.
class LargeResultsSetPagination(PageNumberPagination):
    page_size = 4
    def get_paginated_response(self, data):
        # Return links, counts, and results in a consistent envelope.
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'total_objects': self.page.paginator.count,
            'number_of_pages' : self.page.paginator.num_pages,
            'results': data ,
        })
