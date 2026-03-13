"""
CoRide Platform - Response Utilities Module
============================================
Standardized response helpers for REST API and WebSocket responses.
Provides consistent response format across all endpoints.

Usage:
    from utils.responses import APIResponse, WebSocketResponse
    
    # In views
    return APIResponse.success(data={'user_id': 123}, message='User created')
    return APIResponse.error('Invalid data', error_code='VALIDATION_ERROR')
    
    # In WebSocket consumers
    await self.send_json(WebSocketResponse.event('message', {'text': 'Hello'}))
"""

from datetime import datetime
from typing import Optional, Dict, Any
from rest_framework.response import Response
from rest_framework import status

# ============================================
# HTTP STATUS CODES
# ============================================

# Success codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_202_ACCEPTED = 202
HTTP_204_NO_CONTENT = 204

# Client error codes
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_406_NOT_ACCEPTABLE = 406
HTTP_409_CONFLICT = 409
HTTP_422_UNPROCESSABLE_ENTITY = 422
HTTP_423_LOCKED = 423
HTTP_429_TOO_MANY_REQUESTS = 429

# Server error codes
HTTP_500_INTERNAL_SERVER_ERROR = 500
HTTP_501_NOT_IMPLEMENTED = 501
HTTP_502_BAD_GATEWAY = 502
HTTP_503_SERVICE_UNAVAILABLE = 503
HTTP_504_GATEWAY_TIMEOUT = 504


# ============================================
# API RESPONSE CLASS
# ============================================

class APIResponse:
    """
    Standardized API response helper class.
    
    Provides static methods for creating consistent REST API responses
    across all endpoints in the CoRide platform.
    
    All responses include:
    - success: Boolean indicating success/failure
    - message: Human-readable message
    - timestamp: ISO 8601 timestamp
    - data/error_code/details: Additional context
    """
    
    @staticmethod
    def success(data: Optional[Any] = None, message: str = "Success", status_code: int = HTTP_200_OK) -> Response:
        """
        Create a successful response.
        
        Args:
            data: Response data (optional)
            message: Success message
            status_code: HTTP status code (default: 200)
            
        Returns:
            Response object with success format
            
        Example:
            >>> APIResponse.success({'user_id': 123}, 'User retrieved')
            Response({'success': True, 'message': 'User retrieved', 'data': {...}})
        """
        response_data = {
            'success': True,
            'message': message,
            'data': data,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
        }
        return Response(response_data, status=status_code)
    
    @staticmethod
    def created(data: Optional[Any] = None, message: str = "Created successfully") -> Response:
        """
        Create a 201 Created response.
        
        Args:
            data: Created resource data (optional)
            message: Success message
            
        Returns:
            Response object with 201 status
            
        Example:
            >>> APIResponse.created({'ride_id': 456}, 'Ride created')
            Response({'success': True, 'message': 'Ride created', ...}, status=201)
        """
        return APIResponse.success(data=data, message=message, status_code=HTTP_201_CREATED)
    
    @staticmethod
    def updated(data: Optional[Any] = None, message: str = "Updated successfully") -> Response:
        """
        Create a 200 OK response for update operations.
        
        Args:
            data: Updated resource data (optional)
            message: Success message
            
        Returns:
            Response object with 200 status
            
        Example:
            >>> APIResponse.updated({'ride_id': 456}, 'Ride updated')
            Response({'success': True, 'message': 'Ride updated', ...})
        """
        return APIResponse.success(data=data, message=message, status_code=HTTP_200_OK)
    
    @staticmethod
    def deleted(message: str = "Deleted successfully") -> Response:
        """
        Create a 200 OK response for delete operations.
        
        Args:
            message: Success message
            
        Returns:
            Response object with 200 status and no data
            
        Example:
            >>> APIResponse.deleted('Ride deleted')
            Response({'success': True, 'message': 'Ride deleted', 'data': None})
        """
        return APIResponse.success(data=None, message=message, status_code=HTTP_200_OK)
    
    @staticmethod
    def error(
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict] = None,
        status_code: int = HTTP_400_BAD_REQUEST
    ) -> Response:
        """
        Create an error response.
        
        Args:
            message: Error message
            error_code: Error code identifier (optional)
            details: Additional error details (optional)
            status_code: HTTP status code (default: 400)
            
        Returns:
            Response object with error format
            
        Example:
            >>> APIResponse.error('Invalid phone', 'INVALID_PHONE', {'field': 'phone'})
            Response({'success': False, 'message': 'Invalid phone', ...}, status=400)
        """
        response_data = {
            'success': False,
            'message': message,
            'error_code': error_code,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat() + 'Z',
        }
        return Response(response_data, status=status_code)
    
    @staticmethod
    def not_found(message: str = "Resource not found") -> Response:
        """
        Create a 404 Not Found response.
        
        Args:
            message: Error message
            
        Returns:
            Response object with 404 status
            
        Example:
            >>> APIResponse.not_found('Ride not found')
            Response({'success': False, 'message': 'Ride not found', ...}, status=404)
        """
        return APIResponse.error(
            message=message,
            error_code='NOT_FOUND',
            status_code=HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def unauthorized(message: str = "Authentication required") -> Response:
        """
        Create a 401 Unauthorized response.
        
        Args:
            message: Error message
            
        Returns:
            Response object with 401 status
            
        Example:
            >>> APIResponse.unauthorized('Invalid token')
            Response({'success': False, 'message': 'Invalid token', ...}, status=401)
        """
        return APIResponse.error(
            message=message,
            error_code='UNAUTHORIZED',
            status_code=HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def forbidden(message: str = "Permission denied") -> Response:
        """
        Create a 403 Forbidden response.
        
        Args:
            message: Error message
            
        Returns:
            Response object with 403 status
            
        Example:
            >>> APIResponse.forbidden('Only drivers can create rides')
            Response({'success': False, 'message': '...', ...}, status=403)
        """
        return APIResponse.error(
            message=message,
            error_code='FORBIDDEN',
            status_code=HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def validation_error(errors: Dict, message: str = "Validation failed") -> Response:
        """
        Create a 422 Unprocessable Entity response for validation errors.
        
        Args:
            errors: Dictionary of field-level validation errors
            message: Error message
            
        Returns:
            Response object with 422 status
            
        Example:
            >>> APIResponse.validation_error({'phone': ['Invalid format']})
            Response({'success': False, 'message': 'Validation failed', 
                     'details': {'phone': [...]}, ...}, status=422)
        """
        return APIResponse.error(
            message=message,
            error_code='VALIDATION_ERROR',
            details=errors,
            status_code=HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    @staticmethod
    def server_error(message: str = "Internal server error") -> Response:
        """
        Create a 500 Internal Server Error response.
        
        Args:
            message: Error message
            
        Returns:
            Response object with 500 status
            
        Example:
            >>> APIResponse.server_error('Database connection failed')
            Response({'success': False, 'message': '...', ...}, status=500)
        """
        return APIResponse.error(
            message=message,
            error_code='INTERNAL_SERVER_ERROR',
            status_code=HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @staticmethod
    def paginated(data: list, paginator, request, message: str = "Success") -> Response:
        """
        Create a paginated response using a paginator instance.
        
        Args:
            data: List of items for current page
            paginator: Paginator instance
            request: Request object
            message: Success message
            
        Returns:
            Response object with pagination metadata
            
        Example:
            >>> APIResponse.paginated(rides, paginator, request)
            Response({'success': True, 'count': 100, 'results': [...], ...})
        """
        return paginator.get_paginated_response(data)


# ============================================
# WEBSOCKET RESPONSE CLASS
# ============================================

class WebSocketResponse:
    """
    Standardized WebSocket response helper class.
    
    Provides static methods for creating consistent WebSocket messages
    for real-time features (chat, tracking, notifications).
    
    All WebSocket messages include:
    - type: Event type identifier
    - data: Event payload
    - timestamp: ISO 8601 timestamp
    """
    
    @staticmethod
    def event(event_type: str, data: Any) -> Dict:
        """
        Create a WebSocket event message.
        
        Args:
            event_type: Type of event (e.g., 'message', 'location_update')
            data: Event payload data
            
        Returns:
            Dictionary for WebSocket JSON response
            
        Example:
            >>> WebSocketResponse.event('message', {'text': 'Hello', 'user_id': 123})
            {'type': 'message', 'data': {...}, 'timestamp': '2024-01-15T10:30:00Z'}
            
            # In WebSocket consumer
            await self.send_json(WebSocketResponse.event('location_update', {
                'lat': 28.6139,
                'lon': 77.2090
            }))
        """
        return {
            'type': event_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
        }
    
    @staticmethod
    def error(message: str, code: Optional[str] = None) -> Dict:
        """
        Create a WebSocket error message.
        
        Args:
            message: Error message
            code: Error code identifier (optional)
            
        Returns:
            Dictionary for WebSocket JSON error response
            
        Example:
            >>> WebSocketResponse.error('Invalid message format', 'INVALID_FORMAT')
            {'type': 'error', 'message': '...', 'code': 'INVALID_FORMAT', ...}
            
            # In WebSocket consumer
            await self.send_json(WebSocketResponse.error(
                'You are not authorized to send messages',
                'UNAUTHORIZED'
            ))
        """
        return {
            'type': 'error',
            'message': message,
            'code': code,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
        }
    
    @staticmethod
    def success(message: str, data: Optional[Any] = None) -> Dict:
        """
        Create a WebSocket success message.
        
        Args:
            message: Success message
            data: Additional data (optional)
            
        Returns:
            Dictionary for WebSocket JSON success response
            
        Example:
            >>> WebSocketResponse.success('Message sent', {'message_id': 789})
            {'type': 'success', 'message': 'Message sent', 'data': {...}, ...}
        """
        return {
            'type': 'success',
            'message': message,
            'data': data,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
        }
    
    @staticmethod
    def notification(notification_type: str, title: str, body: str, data: Optional[Dict] = None) -> Dict:
        """
        Create a WebSocket notification message.
        
        Args:
            notification_type: Type of notification
            title: Notification title
            body: Notification body text
            data: Additional notification data (optional)
            
        Returns:
            Dictionary for WebSocket JSON notification
            
        Example:
            >>> WebSocketResponse.notification(
            ...     'booking_confirmed',
            ...     'Booking Confirmed',
            ...     'Your ride has been confirmed',
            ...     {'booking_id': 456}
            ... )
            {'type': 'notification', 'notification_type': '...', ...}
        """
        return {
            'type': 'notification',
            'notification_type': notification_type,
            'title': title,
            'body': body,
            'data': data or {},
            'timestamp': datetime.utcnow().isoformat() + 'Z',
        }
    
    @staticmethod
    def location_update(lat: float, lon: float, user_id: int, additional_data: Optional[Dict] = None) -> Dict:
        """
        Create a WebSocket location update message for ride tracking.
        
        Args:
            lat: Latitude
            lon: Longitude
            user_id: User ID sending location
            additional_data: Additional tracking data (optional)
            
        Returns:
            Dictionary for WebSocket JSON location update
            
        Example:
            >>> WebSocketResponse.location_update(28.6139, 77.2090, 123, {'speed': 45})
            {'type': 'location_update', 'lat': 28.6139, 'lon': 77.2090, ...}
        """
        response = {
            'type': 'location_update',
            'lat': lat,
            'lon': lon,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
        }
        
        if additional_data:
            response.update(additional_data)
        
        return response
    
    @staticmethod
    def chat_message(message_id: int, sender_id: int, text: str, sender_name: str) -> Dict:
        """
        Create a WebSocket chat message.
        
        Args:
            message_id: Message ID
            sender_id: Sender user ID
            text: Message text
            sender_name: Sender's name
            
        Returns:
            Dictionary for WebSocket JSON chat message
            
        Example:
            >>> WebSocketResponse.chat_message(789, 123, 'Hello!', 'John Doe')
            {'type': 'chat_message', 'message_id': 789, 'text': 'Hello!', ...}
        """
        return {
            'type': 'chat_message',
            'message_id': message_id,
            'sender_id': sender_id,
            'sender_name': sender_name,
            'text': text,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
        }


# ============================================
# EXPORTS
# ============================================

__all__ = [
    # Response classes
    'APIResponse',
    'WebSocketResponse',
    
    # HTTP status codes - Success
    'HTTP_200_OK',
    'HTTP_201_CREATED',
    'HTTP_202_ACCEPTED',
    'HTTP_204_NO_CONTENT',
    
    # HTTP status codes - Client errors
    'HTTP_400_BAD_REQUEST',
    'HTTP_401_UNAUTHORIZED',
    'HTTP_403_FORBIDDEN',
    'HTTP_404_NOT_FOUND',
    'HTTP_405_METHOD_NOT_ALLOWED',
    'HTTP_406_NOT_ACCEPTABLE',
    'HTTP_409_CONFLICT',
    'HTTP_422_UNPROCESSABLE_ENTITY',
    'HTTP_423_LOCKED',
    'HTTP_429_TOO_MANY_REQUESTS',
    
    # HTTP status codes - Server errors
    'HTTP_500_INTERNAL_SERVER_ERROR',
    'HTTP_501_NOT_IMPLEMENTED',
    'HTTP_502_BAD_GATEWAY',
    'HTTP_503_SERVICE_UNAVAILABLE',
    'HTTP_504_GATEWAY_TIMEOUT',
]
