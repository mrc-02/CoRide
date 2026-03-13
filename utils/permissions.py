"""
CoRide Platform - Custom Permissions Module
============================================
Django REST Framework permission classes for role-based access control.
All permissions inherit from BasePermission and provide clear error messages.

Usage:
    from utils.permissions import IsVerifiedDriver, IsRideDriver
    
    # In views
    class RideViewSet(viewsets.ModelViewSet):
        permission_classes = [IsVerifiedDriver]
    
    # Multiple permissions (all must pass)
    permission_classes = [IsAuthenticated, IsVerifiedDriver, IsNotSuspended]
"""

from rest_framework.permissions import BasePermission
from utils.constants import UserRole, DriverVerificationStatus

# ============================================
# ROLE-BASED PERMISSIONS
# ============================================

class IsPassenger(BasePermission):
    """
    Permission class to check if user is a passenger.
    
    Requirements:
    - User must be authenticated
    - User role must be 'passenger'
    
    Use Cases:
    - Booking rides
    - Viewing ride search results
    - Rating drivers
    
    Example:
        class BookingViewSet(viewsets.ModelViewSet):
            permission_classes = [IsPassenger]
    """
    
    message = 'Only passengers can perform this action.'
    
    def has_permission(self, request, view):
        """Check if user is authenticated and has passenger role."""
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role == UserRole.PASSENGER
        )


class IsDriver(BasePermission):
    """
    Permission class to check if user is a driver.
    
    Requirements:
    - User must be authenticated
    - User role must be 'driver'
    
    Use Cases:
    - Creating rides
    - Viewing driver dashboard
    - Managing vehicle information
    
    Example:
        class RideCreateView(APIView):
            permission_classes = [IsDriver]
    """
    
    message = 'Only drivers can perform this action.'
    
    def has_permission(self, request, view):
        """Check if user is authenticated and has driver role."""
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role == UserRole.DRIVER
        )


class IsVerifiedDriver(BasePermission):
    """
    Permission class to check if user is a verified driver.
    
    Requirements:
    - User must be authenticated
    - User role must be 'driver'
    - Driver verification_status must be 'approved'
    
    Use Cases:
    - Publishing rides
    - Starting rides
    - Receiving payments
    
    Example:
        class RidePublishView(APIView):
            permission_classes = [IsVerifiedDriver]
    """
    
    message = 'Only verified drivers can perform this action.'
    
    def has_permission(self, request, view):
        """Check if user is authenticated, is driver, and is verified."""
        if not (request.user and request.user.is_authenticated):
            return False
        
        if not hasattr(request.user, 'role') or request.user.role != UserRole.DRIVER:
            return False
        
        # Check if driver profile exists and is verified
        if hasattr(request.user, 'driver_profile'):
            return request.user.driver_profile.verification_status == DriverVerificationStatus.APPROVED
        
        return False


class IsAdminUser(BasePermission):
    """
    Permission class to check if user is an admin.
    
    Requirements:
    - User must be authenticated
    - User role must be 'admin' or 'super_admin'
    
    Use Cases:
    - Accessing admin panel
    - Viewing analytics
    - Managing users
    
    Example:
        class AdminDashboardView(APIView):
            permission_classes = [IsAdminUser]
    """
    
    message = 'Only admin users can perform this action.'
    
    def has_permission(self, request, view):
        """Check if user is authenticated and has admin role."""
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]
        )


class IsSuperAdmin(BasePermission):
    """
    Permission class to check if user is a super admin.
    
    Requirements:
    - User must be authenticated
    - User role must be 'super_admin'
    
    Use Cases:
    - Managing admin users
    - System configuration
    - Critical operations
    
    Example:
        class SystemConfigView(APIView):
            permission_classes = [IsSuperAdmin]
    """
    
    message = 'Only super admins can perform this action.'
    
    def has_permission(self, request, view):
        """Check if user is authenticated and has super_admin role."""
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role == UserRole.SUPER_ADMIN
        )


class IsPassengerOrDriver(BasePermission):
    """
    Permission class to check if user is either passenger or driver.
    
    Requirements:
    - User must be authenticated
    - User role must be 'passenger' or 'driver'
    
    Use Cases:
    - Viewing profile
    - Accessing chat
    - Viewing notifications
    
    Example:
        class ProfileView(APIView):
            permission_classes = [IsPassengerOrDriver]
    """
    
    message = 'Authentication required.'
    
    def has_permission(self, request, view):
        """Check if user is authenticated and has passenger or driver role."""
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role in [UserRole.PASSENGER, UserRole.DRIVER]
        )


# ============================================
# RESOURCE-SPECIFIC PERMISSIONS
# ============================================

class IsRideDriver(BasePermission):
    """
    Permission class to check if user is the driver of a specific ride.
    
    Requirements:
    - User must be authenticated
    - User must be the driver who created the ride
    - Ride ID obtained from view kwargs (ride_id or pk)
    
    Use Cases:
    - Updating ride details
    - Starting ride
    - Cancelling ride
    
    Example:
        class RideUpdateView(UpdateAPIView):
            permission_classes = [IsRideDriver]
    """
    
    message = 'You are not the driver of this ride.'
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user is the driver of the ride."""
        # obj is the Ride instance
        return obj.driver.user == request.user


class IsRideParticipant(BasePermission):
    """
    Permission class to check if user is a participant in a ride.
    
    Requirements:
    - User must be authenticated
    - User must be either:
      * The driver of the ride, OR
      * A confirmed passenger in the ride
    
    Use Cases:
    - Accessing ride chat
    - Viewing ride tracking
    - Viewing ride details
    
    Example:
        class RideChatView(APIView):
            permission_classes = [IsRideParticipant]
    """
    
    message = 'You are not a participant in this ride.'
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user is driver or confirmed passenger of the ride."""
        from utils.constants import BookingStatus
        
        # Check if user is the driver
        if obj.driver.user == request.user:
            return True
        
        # Check if user is a confirmed passenger
        confirmed_bookings = obj.bookings.filter(
            passenger=request.user,
            status=BookingStatus.CONFIRMED
        )
        return confirmed_bookings.exists()


class IsBookingOwner(BasePermission):
    """
    Permission class to check if user owns a booking.
    
    Requirements:
    - User must be authenticated
    - User must be the passenger who created the booking
    
    Use Cases:
    - Cancelling booking
    - Viewing booking details
    - Rating after ride completion
    
    Example:
        class BookingCancelView(APIView):
            permission_classes = [IsBookingOwner]
    """
    
    message = 'You do not own this booking.'
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user is the passenger who made the booking."""
        # obj is the Booking instance
        return obj.passenger == request.user


class IsOwnerOrAdmin(BasePermission):
    """
    Permission class to check if user owns resource or is admin.
    
    Requirements:
    - User must be authenticated
    - User must either:
      * Own the object (object.user == request.user), OR
      * Be an admin or super_admin
    
    Use Cases:
    - Editing user profiles
    - Deleting resources
    - Viewing private information
    
    Example:
        class UserProfileUpdateView(UpdateAPIView):
            permission_classes = [IsOwnerOrAdmin]
    
    Note:
        Works with any model that has a 'user' field.
    """
    
    message = 'You do not have permission to access this resource.'
    
    def has_permission(self, request, view):
        """Check if user is authenticated."""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user owns the object or is admin."""
        # Check if user is admin
        if hasattr(request.user, 'role') and request.user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            return True
        
        # Check if user owns the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # If object is the user itself
        if hasattr(obj, 'id') and obj == request.user:
            return True
        
        return False


# ============================================
# VERIFICATION PERMISSIONS
# ============================================

class IsPhoneVerified(BasePermission):
    """
    Permission class to check if user's phone is verified.
    
    Requirements:
    - User must be authenticated
    - User's phone_verified field must be True
    
    Use Cases:
    - Creating rides
    - Making bookings
    - Accessing payment features
    
    Example:
        class BookingCreateView(CreateAPIView):
            permission_classes = [IsPhoneVerified]
    """
    
    message = 'Please verify your phone number first.'
    
    def has_permission(self, request, view):
        """Check if user is authenticated and phone is verified."""
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'phone_verified') and
            request.user.phone_verified
        )


class IsProfileComplete(BasePermission):
    """
    Permission class to check if user profile is complete.
    
    Requirements:
    - User must be authenticated
    - User must have:
      * Full name
      * Phone number
      * Profile photo
    
    Use Cases:
    - Creating rides
    - Making bookings
    - Accessing premium features
    
    Example:
        class RideCreateView(CreateAPIView):
            permission_classes = [IsProfileComplete]
    """
    
    message = 'Please complete your profile first.'
    
    def has_permission(self, request, view):
        """Check if user is authenticated and profile is complete."""
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Check required profile fields
        has_name = bool(request.user.full_name)
        has_phone = bool(request.user.phone_number)
        has_photo = bool(request.user.profile_photo) if hasattr(request.user, 'profile_photo') else False
        
        return has_name and has_phone and has_photo


class IsNotSuspended(BasePermission):
    """
    Permission class to check if user account is not suspended.
    
    Requirements:
    - User must be authenticated
    - User status must not be 'suspended' or 'banned'
    
    Use Cases:
    - All authenticated endpoints
    - Preventing suspended users from actions
    
    Example:
        class RideViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, IsNotSuspended]
    """
    
    message = 'Your account has been suspended.'
    
    def has_permission(self, request, view):
        """Check if user is authenticated and not suspended."""
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Check if user has status field
        if hasattr(request.user, 'status'):
            return request.user.status not in ['suspended', 'banned']
        
        # Check if user is active
        return request.user.is_active


# ============================================
# ADMIN PANEL PERMISSIONS
# ============================================

class CanAccessAdminPanel(BasePermission):
    """
    Permission class to check if user can access admin panel.
    
    Requirements:
    - User must be authenticated
    - User must have admin or super_admin role
    - User's admin record must be active
    
    Use Cases:
    - Admin panel views
    - Admin API endpoints
    - Analytics and reports
    
    Example:
        class AdminPanelView(APIView):
            permission_classes = [CanAccessAdminPanel]
    """
    
    message = 'Access denied to admin panel.'
    
    def has_permission(self, request, view):
        """Check if user can access admin panel."""
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Check if user has admin role
        if not (hasattr(request.user, 'role') and 
                request.user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]):
            return False
        
        # Check if admin record exists and is active
        if hasattr(request.user, 'admin_profile'):
            return request.user.admin_profile.is_active
        
        # Super admins always have access
        return request.user.role == UserRole.SUPER_ADMIN


# ============================================
# COMPOSITE PERMISSIONS
# ============================================

class IsAuthenticatedAndVerified(BasePermission):
    """
    Composite permission: User must be authenticated with verified phone and complete profile.
    
    Combines:
    - IsPhoneVerified
    - IsProfileComplete
    
    Use Cases:
    - Critical operations requiring full verification
    - Payment processing
    - Creating rides or bookings
    
    Example:
        class PaymentView(APIView):
            permission_classes = [IsAuthenticatedAndVerified]
    """
    
    message = 'Please verify your phone and complete your profile.'
    
    def has_permission(self, request, view):
        """Check if user is authenticated, phone verified, and profile complete."""
        phone_verified = IsPhoneVerified().has_permission(request, view)
        profile_complete = IsProfileComplete().has_permission(request, view)
        return phone_verified and profile_complete


class IsActiveDriver(BasePermission):
    """
    Composite permission: User must be verified driver who is not suspended.
    
    Combines:
    - IsVerifiedDriver
    - IsNotSuspended
    
    Use Cases:
    - Publishing rides
    - Starting rides
    - Receiving bookings
    
    Example:
        class RidePublishView(APIView):
            permission_classes = [IsActiveDriver]
    """
    
    message = 'Only active verified drivers can perform this action.'
    
    def has_permission(self, request, view):
        """Check if user is verified driver and not suspended."""
        verified_driver = IsVerifiedDriver().has_permission(request, view)
        not_suspended = IsNotSuspended().has_permission(request, view)
        return verified_driver and not_suspended


class IsActivePassenger(BasePermission):
    """
    Composite permission: User must be passenger who is not suspended.
    
    Combines:
    - IsPassenger
    - IsNotSuspended
    
    Use Cases:
    - Making bookings
    - Searching rides
    - Rating drivers
    
    Example:
        class BookingCreateView(CreateAPIView):
            permission_classes = [IsActivePassenger]
    """
    
    message = 'Only active passengers can perform this action.'
    
    def has_permission(self, request, view):
        """Check if user is passenger and not suspended."""
        is_passenger = IsPassenger().has_permission(request, view)
        not_suspended = IsNotSuspended().has_permission(request, view)
        return is_passenger and not_suspended


class CanCreateRide(BasePermission):
    """
    Composite permission: User must meet all requirements to create a ride.
    
    Combines:
    - IsVerifiedDriver
    - IsPhoneVerified
    - IsProfileComplete
    - IsNotSuspended
    
    Use Cases:
    - Creating new rides
    
    Example:
        class RideCreateView(CreateAPIView):
            permission_classes = [CanCreateRide]
    """
    
    message = 'You do not meet the requirements to create a ride.'
    
    def has_permission(self, request, view):
        """Check if user can create a ride."""
        verified_driver = IsVerifiedDriver().has_permission(request, view)
        phone_verified = IsPhoneVerified().has_permission(request, view)
        profile_complete = IsProfileComplete().has_permission(request, view)
        not_suspended = IsNotSuspended().has_permission(request, view)
        
        return verified_driver and phone_verified and profile_complete and not_suspended


class CanMakeBooking(BasePermission):
    """
    Composite permission: User must meet all requirements to make a booking.
    
    Combines:
    - IsPassenger
    - IsPhoneVerified
    - IsProfileComplete
    - IsNotSuspended
    
    Use Cases:
    - Creating new bookings
    
    Example:
        class BookingCreateView(CreateAPIView):
            permission_classes = [CanMakeBooking]
    """
    
    message = 'You do not meet the requirements to make a booking.'
    
    def has_permission(self, request, view):
        """Check if user can make a booking."""
        is_passenger = IsPassenger().has_permission(request, view)
        phone_verified = IsPhoneVerified().has_permission(request, view)
        profile_complete = IsProfileComplete().has_permission(request, view)
        not_suspended = IsNotSuspended().has_permission(request, view)
        
        return is_passenger and phone_verified and profile_complete and not_suspended


# ============================================
# EXPORTS
# ============================================

__all__ = [
    # Role-based permissions
    'IsPassenger',
    'IsDriver',
    'IsVerifiedDriver',
    'IsAdminUser',
    'IsSuperAdmin',
    'IsPassengerOrDriver',
    
    # Resource-specific permissions
    'IsRideDriver',
    'IsRideParticipant',
    'IsBookingOwner',
    'IsOwnerOrAdmin',
    
    # Verification permissions
    'IsPhoneVerified',
    'IsProfileComplete',
    'IsNotSuspended',
    
    # Admin panel permissions
    'CanAccessAdminPanel',
    
    # Composite permissions
    'IsAuthenticatedAndVerified',
    'IsActiveDriver',
    'IsActivePassenger',
    'CanCreateRide',
    'CanMakeBooking',
]
