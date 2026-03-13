"""
CoRide Django Backend - Main URL Configuration
===============================================
Production-ready URL routing for the carpooling platform.

API Structure:
- All APIs prefixed with /api/v1/
- Comprehensive API documentation (Swagger & ReDoc)
- Health check and monitoring endpoints
- Custom JSON error handlers
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from datetime import datetime
import logging

logger = logging.getLogger('coride')

# ============================================
# DJANGO ADMIN CUSTOMIZATION
# ============================================
admin.site.site_title = 'CoRide Admin'
admin.site.site_header = 'CoRide Platform'
admin.site.index_title = 'Platform Management'

# ============================================
# HEALTH CHECK ENDPOINT
# ============================================
@csrf_exempt
def health_check(request):
    """
    Health check endpoint for monitoring and load balancers.
    Tests database and Redis connectivity.
    
    Returns:
        JSON response with system health status
    """
    from django.db import connection
    from django.core.cache import cache
    
    health_status = {
        'status': 'healthy',
        'version': '1.0.0',
        'platform': 'CoRide',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'environment': 'development' if settings.DEBUG else 'production',
    }
    
    # Test database connection
    try:
        connection.ensure_connection()
        health_status['database'] = 'connected'
    except Exception as e:
        health_status['database'] = 'error'
        health_status['status'] = 'unhealthy'
        logger.error(f"Database health check failed: {str(e)}")
    
    # Test Redis connection
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status['redis'] = 'connected'
        else:
            health_status['redis'] = 'error'
            health_status['status'] = 'unhealthy'
    except Exception as e:
        health_status['redis'] = 'error'
        health_status['status'] = 'unhealthy'
        logger.error(f"Redis health check failed: {str(e)}")
    
    # Return 200 if healthy, 503 if unhealthy
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)

# ============================================
# API INFO ENDPOINT
# ============================================
@csrf_exempt
def api_info(request):
    """
    API information endpoint providing platform details and documentation links.
    
    Returns:
        JSON response with API metadata
    """
    return JsonResponse({
        'platform': 'CoRide',
        'version': '1.0.0',
        'description': 'CoRide Carpooling Platform API',
        'docs': '/api/docs/',
        'redoc': '/api/redoc/',
        'schema': '/api/schema/',
        'health': '/api/health/',
        'api_prefix': '/api/v1/',
    })

# ============================================
# MAIN URL PATTERNS
# ============================================
urlpatterns = [
    # ============================================
    # DJANGO ADMIN PANEL
    # ============================================
    path('django-admin/', admin.site.urls),
    
    # ============================================
    # API DOCUMENTATION
    # ============================================
    # OpenAPI schema download
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Swagger UI documentation
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # ReDoc UI documentation
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # ============================================
    # MONITORING ENDPOINTS
    # ============================================
    # Health check for load balancers and monitoring
    path('api/health/', health_check, name='health-check'),
    
    # API information and metadata
    path('api/', api_info, name='api-info'),
    
    # ============================================
    # API VERSION 1 ENDPOINTS
    # ============================================
    # Authentication (login, register, OTP, JWT tokens)
    path('api/v1/auth/', include(('authentication.urls', 'authentication'), namespace='auth')),
    
    # User profile management
    path('api/v1/users/', include(('users.urls', 'users'), namespace='users')),
    
    # Driver registration, verification, and management
    path('api/v1/drivers/', include(('drivers.urls', 'drivers'), namespace='drivers')),
    
    # Ride creation, search, and management
    path('api/v1/rides/', include(('rides.urls', 'rides'), namespace='rides')),
    
    # Booking creation, confirmation, and cancellation
    path('api/v1/bookings/', include(('bookings.urls', 'bookings'), namespace='bookings')),
    
    # Payment processing via Razorpay
    path('api/v1/payments/', include(('payments.urls', 'payments'), namespace='payments')),
    
    # Push notifications and alerts
    path('api/v1/notifications/', include(('notifications.urls', 'notifications'), namespace='notifications')),
    
    # User and driver ratings and reviews
    path('api/v1/ratings/', include(('ratings.urls', 'ratings'), namespace='ratings')),
    
    # Real-time chat between riders and drivers
    path('api/v1/chat/', include(('chat.urls', 'chat'), namespace='chat')),
    
    # Admin panel operations and analytics
    path('api/v1/admin-panel/', include(('admin_panel.urls', 'admin_panel'), namespace='admin-panel')),
]

# ============================================
# SERVE MEDIA FILES IN DEVELOPMENT
# ============================================
if settings.DEBUG:
    # Serve media files uploaded by users (in production, use Cloudinary)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Serve static files (in production, use collectstatic + CDN)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    logger.info("Development mode: Serving media and static files via Django")

# ============================================
# CUSTOM ERROR HANDLERS
# ============================================
def custom_404_handler(request, exception=None):
    """
    Custom 404 error handler returning JSON response.
    
    Args:
        request: HTTP request object
        exception: Exception that triggered 404
        
    Returns:
        JSON response with error details
    """
    return JsonResponse({
        'success': False,
        'error': {
            'code': 'NOT_FOUND',
            'message': 'The requested resource was not found.',
            'path': request.path,
        }
    }, status=404)


def custom_500_handler(request):
    """
    Custom 500 error handler returning JSON response.
    
    Args:
        request: HTTP request object
        
    Returns:
        JSON response with error details
    """
    logger.error(f"Internal server error on path: {request.path}")
    
    return JsonResponse({
        'success': False,
        'error': {
            'code': 'INTERNAL_SERVER_ERROR',
            'message': 'An internal server error occurred. Please try again later.',
            'path': request.path,
        }
    }, status=500)


# Assign custom error handlers
handler404 = custom_404_handler
handler500 = custom_500_handler

# ============================================
# PRODUCTION DEPLOYMENT NOTES
# ============================================
"""
DEPLOYMENT CHECKLIST:
1. Set DEBUG=False in production
2. Configure ALLOWED_HOSTS with actual domain
3. Use Cloudinary for media files (not Django static serve)
4. Set up Nginx/Apache to serve static files
5. Enable HTTPS and configure SSL certificates
6. Set up monitoring for /api/health/ endpoint
7. Configure rate limiting on authentication endpoints
8. Enable CORS for frontend domain only
9. Set up database connection pooling
10. Configure Redis for caching and sessions

URL STRUCTURE:
- API Base: /api/v1/
- Documentation: /api/docs/ (Swagger), /api/redoc/ (ReDoc)
- Health Check: /api/health/
- Admin Panel: /django-admin/
- WebSocket: ws://domain/ws/v1/ (see asgi.py)

SECURITY:
- All API endpoints require JWT authentication (except auth endpoints)
- CSRF protection enabled for non-API views
- Rate limiting configured in settings.py
- Custom error handlers prevent information leakage
"""
