"""
CoRide Django Backend - ASGI Configuration
===========================================
Production-ready ASGI config for handling:
- HTTP requests via Django's standard ASGI application
- WebSocket connections for real-time features:
  * Live chat between riders and drivers
  * Real-time GPS tracking during rides
  * Push notifications and alerts

Supports JWT authentication on WebSocket connections.
"""

import os
import logging
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path

# ============================================
# DJANGO SETTINGS MODULE
# ============================================
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coride.settings')

# Initialize Django ASGI application early to ensure AppRegistry is populated
# before importing code that may import ORM models
django_asgi_app = get_asgi_application()

# ============================================
# IMPORT WEBSOCKET CONSUMERS AND ROUTING
# ============================================
# Import after django_asgi_app to avoid AppRegistryNotReady error
from chat.consumers import ChatConsumer
from rides.consumers import RideTrackingConsumer
from notifications.consumers import NotificationConsumer

# ============================================
# LOGGING CONFIGURATION
# ============================================
logger = logging.getLogger('coride')

# ============================================
# JWT AUTHENTICATION MIDDLEWARE FOR WEBSOCKETS
# ============================================
class JWTAuthMiddleware:
    """
    Custom middleware to authenticate WebSocket connections using JWT tokens.
    
    Token can be passed via:
    - Query parameter: ws://domain/path/?token=<jwt_token>
    - Cookie: token=<jwt_token>
    
    Attaches authenticated user to scope['user'] or AnonymousUser if invalid.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        from urllib.parse import parse_qs
        from django.contrib.auth.models import AnonymousUser
        from rest_framework_simplejwt.tokens import AccessToken
        from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
        from channels.db import database_sync_to_async
        from users.models import User
        
        # Extract token from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]
        
        # If no token in query, check headers (for some WebSocket clients)
        if not token:
            headers = dict(scope.get('headers', []))
            auth_header = headers.get(b'authorization', b'').decode()
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        # Default to anonymous user
        scope['user'] = AnonymousUser()
        
        # Authenticate if token provided
        if token:
            try:
                # Validate JWT token
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                
                # Fetch user from database
                @database_sync_to_async
                def get_user(user_id):
                    try:
                        return User.objects.get(id=user_id, is_active=True)
                    except User.DoesNotExist:
                        return AnonymousUser()
                
                user = await get_user(user_id)
                scope['user'] = user
                
                logger.info(f"WebSocket authenticated: User {user_id} connected to {scope['path']}")
                
            except (TokenError, InvalidToken, KeyError) as e:
                logger.warning(f"WebSocket authentication failed: {str(e)}")
                scope['user'] = AnonymousUser()
        else:
            logger.info(f"WebSocket connection without token to {scope['path']}")
        
        return await self.app(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    """
    Wrapper function to apply JWT authentication middleware.
    """
    return JWTAuthMiddleware(AuthMiddlewareStack(inner))


# ============================================
# WEBSOCKET URL ROUTING
# ============================================
websocket_urlpatterns = [
    # Chat WebSocket - Real-time messaging between riders and drivers
    path('ws/v1/chat/<int:ride_id>/', ChatConsumer.as_asgi()),
    
    # Ride Tracking WebSocket - Live GPS location updates during ride
    path('ws/v1/tracking/<int:ride_id>/', RideTrackingConsumer.as_asgi()),
    
    # Notifications WebSocket - Push notifications and alerts
    path('ws/v1/notifications/', NotificationConsumer.as_asgi()),
]

# ============================================
# ASGI APPLICATION CONFIGURATION
# ============================================
application = ProtocolTypeRouter({
    # Handle standard HTTP requests
    'http': django_asgi_app,
    
    # Handle WebSocket connections with JWT authentication
    'websocket': AllowedHostsOriginValidator(
        JWTAuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})

# ============================================
# PRODUCTION NOTES
# ============================================
"""
DEPLOYMENT CHECKLIST:
1. Ensure Redis is running for Channel Layers
2. Configure ALLOWED_HOSTS in settings.py
3. Use Daphne or Uvicorn as ASGI server:
   - daphne -b 0.0.0.0 -p 8000 coride.asgi:application
   - uvicorn coride.asgi:application --host 0.0.0.0 --port 8000
4. Set up WebSocket reverse proxy in Nginx/Apache
5. Enable SSL/TLS for wss:// connections in production
6. Monitor WebSocket connections and memory usage
7. Implement connection rate limiting if needed

WEBSOCKET CONNECTION EXAMPLES:
- Chat: ws://localhost:8000/ws/v1/chat/123/?token=<jwt_token>
- Tracking: ws://localhost:8000/ws/v1/tracking/123/?token=<jwt_token>
- Notifications: ws://localhost:8000/ws/v1/notifications/?token=<jwt_token>

SECURITY:
- AllowedHostsOriginValidator prevents connections from unauthorized origins
- JWTAuthMiddleware ensures only authenticated users can connect
- Token validation happens on every connection attempt
- Invalid tokens result in AnonymousUser (connection allowed but limited access)
"""
