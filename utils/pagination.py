"""
CoRide Platform - Pagination Module
====================================
Custom pagination classes for Django REST Framework.
Provides consistent paginated response format across all endpoints.

Usage:
    from utils.pagination import StandardResultsPagination, RideSearchPagination
    
    # In views
    class RideViewSet(viewsets.ModelViewSet):
        pagination_class = StandardResultsPagination
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict

# ============================================
# STANDARD PAGINATION
# ============================================

class StandardResultsPagination(PageNumberPagination):
    """
    Standard pagination for most API endpoints.
    
    Configuration:
    - Default page size: 20 items
    - Max page size: 100 items
    - Client can customize page size via ?page_size=X
    
    Response Format:
        {
            "success": true,
            "count": 150,
            "total_pages": 8,
            "current_page": 1,
            "page_size": 20,
            "next": "http://api.example.com/rides/?page=2",
            "previous": null,
            "results": [...]
        }
    
    Use Cases:
    - User lists
    - Ride lists
    - Booking lists
    - General purpose pagination
    
    Example:
        class UserViewSet(viewsets.ModelViewSet):
            pagination_class = StandardResultsPagination
    """
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """
        Return paginated response with custom format.
        
        Args:
            data: Serialized data for current page
            
        Returns:
            Response object with pagination metadata
        """
        return Response(OrderedDict([
            ('success', True),
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
    
    def get_paginated_response_schema(self, schema):
        """
        Return schema for drf-spectacular API documentation.
        
        Args:
            schema: Schema for the results data
            
        Returns:
            Schema dictionary for paginated response
        """
        return {
            'type': 'object',
            'properties': {
                'success': {
                    'type': 'boolean',
                    'example': True,
                },
                'count': {
                    'type': 'integer',
                    'example': 150,
                    'description': 'Total number of items',
                },
                'total_pages': {
                    'type': 'integer',
                    'example': 8,
                    'description': 'Total number of pages',
                },
                'current_page': {
                    'type': 'integer',
                    'example': 1,
                    'description': 'Current page number',
                },
                'page_size': {
                    'type': 'integer',
                    'example': 20,
                    'description': 'Number of items per page',
                },
                'next': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': 'http://api.example.com/rides/?page=2',
                    'description': 'URL to next page',
                },
                'previous': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': None,
                    'description': 'URL to previous page',
                },
                'results': schema,
            },
        }


# ============================================
# RIDE SEARCH PAGINATION
# ============================================

class RideSearchPagination(PageNumberPagination):
    """
    Pagination for ride search results.
    
    Configuration:
    - Default page size: 10 items (smaller for search results)
    - Max page size: 50 items
    - Optimized for mobile app display
    
    Use Cases:
    - Ride search results
    - Available rides listing
    - Nearby rides
    
    Example:
        class RideSearchView(APIView):
            pagination_class = RideSearchPagination
    """
    
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """Return paginated response with custom format."""
        return Response(OrderedDict([
            ('success', True),
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
    
    def get_paginated_response_schema(self, schema):
        """Return schema for drf-spectacular API documentation."""
        return {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean', 'example': True},
                'count': {'type': 'integer', 'example': 45},
                'total_pages': {'type': 'integer', 'example': 5},
                'current_page': {'type': 'integer', 'example': 1},
                'page_size': {'type': 'integer', 'example': 10},
                'next': {'type': 'string', 'nullable': True, 'format': 'uri'},
                'previous': {'type': 'string', 'nullable': True, 'format': 'uri'},
                'results': schema,
            },
        }


# ============================================
# HISTORY PAGINATION
# ============================================

class HistoryPagination(PageNumberPagination):
    """
    Pagination for user history (rides, bookings, transactions).
    
    Configuration:
    - Default page size: 15 items
    - Max page size: 100 items
    - Balanced for history viewing
    
    Use Cases:
    - Ride history
    - Booking history
    - Transaction history
    - Payment history
    
    Example:
        class RideHistoryView(ListAPIView):
            pagination_class = HistoryPagination
    """
    
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """Return paginated response with custom format."""
        return Response(OrderedDict([
            ('success', True),
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
    
    def get_paginated_response_schema(self, schema):
        """Return schema for drf-spectacular API documentation."""
        return {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean', 'example': True},
                'count': {'type': 'integer', 'example': 75},
                'total_pages': {'type': 'integer', 'example': 5},
                'current_page': {'type': 'integer', 'example': 1},
                'page_size': {'type': 'integer', 'example': 15},
                'next': {'type': 'string', 'nullable': True, 'format': 'uri'},
                'previous': {'type': 'string', 'nullable': True, 'format': 'uri'},
                'results': schema,
            },
        }


# ============================================
# ADMIN PAGINATION
# ============================================

class AdminPagination(PageNumberPagination):
    """
    Pagination for admin panel endpoints.
    
    Configuration:
    - Default page size: 25 items
    - Max page size: 200 items
    - Larger page sizes for admin data tables
    
    Use Cases:
    - Admin user management
    - Admin ride management
    - Admin analytics
    - Admin reports
    
    Example:
        class AdminUserListView(ListAPIView):
            pagination_class = AdminPagination
    """
    
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 200
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """Return paginated response with custom format."""
        return Response(OrderedDict([
            ('success', True),
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
    
    def get_paginated_response_schema(self, schema):
        """Return schema for drf-spectacular API documentation."""
        return {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean', 'example': True},
                'count': {'type': 'integer', 'example': 500},
                'total_pages': {'type': 'integer', 'example': 20},
                'current_page': {'type': 'integer', 'example': 1},
                'page_size': {'type': 'integer', 'example': 25},
                'next': {'type': 'string', 'nullable': True, 'format': 'uri'},
                'previous': {'type': 'string', 'nullable': True, 'format': 'uri'},
                'results': schema,
            },
        }


# ============================================
# CHAT MESSAGE PAGINATION
# ============================================

class ChatMessagePagination(PageNumberPagination):
    """
    Pagination for chat messages (newest first).
    
    Configuration:
    - Default page size: 50 messages
    - Max page size: 100 messages
    - Ordered newest first (for loading older messages)
    
    Use Cases:
    - Chat message history
    - Loading older messages
    - Real-time chat pagination
    
    Example:
        class ChatMessageListView(ListAPIView):
            pagination_class = ChatMessagePagination
            
            def get_queryset(self):
                return ChatMessage.objects.order_by('-created_at')
    
    Note:
        Ensure your queryset is ordered by -created_at (newest first)
        for proper pagination behavior.
    """
    
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """Return paginated response with custom format."""
        return Response(OrderedDict([
            ('success', True),
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
    
    def get_paginated_response_schema(self, schema):
        """Return schema for drf-spectacular API documentation."""
        return {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean', 'example': True},
                'count': {'type': 'integer', 'example': 250},
                'total_pages': {'type': 'integer', 'example': 5},
                'current_page': {'type': 'integer', 'example': 1},
                'page_size': {'type': 'integer', 'example': 50},
                'next': {'type': 'string', 'nullable': True, 'format': 'uri'},
                'previous': {'type': 'string', 'nullable': True, 'format': 'uri'},
                'results': schema,
            },
        }


# ============================================
# EXPORTS
# ============================================

__all__ = [
    'StandardResultsPagination',
    'RideSearchPagination',
    'HistoryPagination',
    'AdminPagination',
    'ChatMessagePagination',
]
