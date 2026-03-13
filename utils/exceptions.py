"""
CoRide Platform - Custom Exceptions Module
===========================================
Custom exception classes and DRF exception handler for the entire platform.
Provides consistent error responses and proper HTTP status codes.

Usage:
    from utils.exceptions import RideNotFoundException, custom_exception_handler
    
    # In views
    raise RideNotFoundException(details={'ride_id': 123})
    
    # In settings.py
    REST_FRAMEWORK = {
        'EXCEPTION_HANDLER': 'utils.exceptions.custom_exception_handler',
    }
"""

import logging
from datetime import datetime
from typing import Dict, Optional, Any
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, OperationalError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    ValidationError,
    AuthenticationFailed,
    PermissionDenied,
    NotFound,
    MethodNotAllowed,
    NotAcceptable,
    UnsupportedMediaType,
    Throttled,
    ParseError,
)

logger = logging.getLogger('coride')

# ============================================
# CUSTOM EXCEPTION HANDLER
# ============================================

def custom_exception_handler(exc: Exception, context: Dict) -> Response:
    """
    Custom exception handler for Django REST Framework.
    
    Handles all types of exceptions and returns consistent JSON responses.
    Logs 5xx errors for monitoring and debugging.
    
    Args:
        exc: Exception instance
        context: Context dictionary with request and view info
        
    Returns:
        Response object with standardized error format
        
    Response Format:
        {
            "success": false,
            "error_code": "ERROR_CODE",
            "message": "Human readable message",
            "details": {},
            "timestamp": "ISO timestamp",
            "path": "request path"
        }
    """
    request = context.get('request')
    path = request.path if request else 'unknown'
    
    # Handle CoRide custom exceptions
    if isinstance(exc, CoRideException):
        return exc.to_response(path=path)
    
    # Handle DRF exceptions first
    response = exception_handler(exc, context)
    
    if response is not None:
        error_data = {
            'success': False,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'path': path,
        }
        
        # Handle specific DRF exceptions
        if isinstance(exc, ValidationError):
            error_data.update({
                'error_code': 'VALIDATION_ERROR',
                'message': 'Validation failed',
                'details': response.data,
            })
        elif isinstance(exc, AuthenticationFailed):
            error_data.update({
                'error_code': 'AUTHENTICATION_FAILED',
                'message': 'Authentication credentials were not provided or are invalid',
                'details': {'detail': str(exc)},
            })
        elif isinstance(exc, PermissionDenied):
            error_data.update({
                'error_code': 'PERMISSION_DENIED',
                'message': 'You do not have permission to perform this action',
                'details': {'detail': str(exc)},
            })
        elif isinstance(exc, NotFound):
            error_data.update({
                'error_code': 'NOT_FOUND',
                'message': 'The requested resource was not found',
                'details': {'detail': str(exc)},
            })
        elif isinstance(exc, MethodNotAllowed):
            error_data.update({
                'error_code': 'METHOD_NOT_ALLOWED',
                'message': f'Method {exc.method} not allowed',
                'details': {'allowed_methods': exc.allowed_methods},
            })
        elif isinstance(exc, Throttled):
            error_data.update({
                'error_code': 'RATE_LIMIT_EXCEEDED',
                'message': 'Request rate limit exceeded',
                'details': {
                    'available_in': f'{exc.wait} seconds' if exc.wait else 'unknown',
                    'throttle_scope': getattr(exc, 'scope', 'unknown'),
                },
            })
        elif isinstance(exc, ParseError):
            error_data.update({
                'error_code': 'PARSE_ERROR',
                'message': 'Malformed request data',
                'details': {'detail': str(exc)},
            })
        else:
            # Generic DRF exception
            error_data.update({
                'error_code': 'API_ERROR',
                'message': 'An API error occurred',
                'details': response.data,
            })
        
        response.data = error_data
        return response
    
    # Handle Django ValidationError
    if isinstance(exc, DjangoValidationError):
        error_data = {
            'success': False,
            'error_code': 'VALIDATION_ERROR',
            'message': 'Validation failed',
            'details': {'errors': exc.messages if hasattr(exc, 'messages') else [str(exc)]},
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'path': path,
        }
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle database errors
    if isinstance(exc, IntegrityError):
        logger.error(f"Database integrity error: {str(exc)}", exc_info=True)
        error_data = {
            'success': False,
            'error_code': 'DATABASE_INTEGRITY_ERROR',
            'message': 'A database constraint was violated',
            'details': {'error': 'Data integrity violation'},
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'path': path,
        }
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
    
    if isinstance(exc, OperationalError):
        logger.error(f"Database operational error: {str(exc)}", exc_info=True)
        error_data = {
            'success': False,
            'error_code': 'DATABASE_ERROR',
            'message': 'A database error occurred',
            'details': {'error': 'Database temporarily unavailable'},
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'path': path,
        }
        return Response(error_data, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    # Handle unexpected exceptions (5xx errors)
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    error_data = {
        'success': False,
        'error_code': 'INTERNAL_SERVER_ERROR',
        'message': 'An internal server error occurred',
        'details': {'error': 'Please try again later'},
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'path': path,
    }
    return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================
# BASE EXCEPTION CLASS
# ============================================

class CoRideException(Exception):
    """
    Base exception class for all CoRide platform exceptions.
    
    Provides consistent error handling with status codes, error codes,
    and standardized response format.
    
    Attributes:
        status_code: HTTP status code
        error_code: Unique error identifier
        message: Human-readable error message
        details: Additional error details dictionary
    """
    
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'CORIDE_ERROR'
    message = 'An error occurred'
    
    def __init__(self, message: Optional[str] = None, details: Optional[Dict] = None):
        """
        Initialize CoRide exception.
        
        Args:
            message: Custom error message (optional)
            details: Additional error details (optional)
        """
        self.message = message or self.message
        self.details = details or {}
        super().__init__(self.message)
    
    def to_response(self, path: str = 'unknown') -> Response:
        """
        Convert exception to DRF Response object.
        
        Args:
            path: Request path for logging
            
        Returns:
            Response object with standardized error format
        """
        error_data = {
            'success': False,
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'path': path,
        }
        
        # Log 5xx errors
        if self.status_code >= 500:
            logger.error(f"{self.error_code}: {self.message}", extra={'details': self.details})
        
        return Response(error_data, status=self.status_code)


# ============================================
# AUTHENTICATION EXCEPTIONS
# ============================================

class InvalidCredentialsException(CoRideException):
    """Exception raised when user provides invalid login credentials."""
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = 'INVALID_CREDENTIALS'
    message = 'Invalid phone number or password'


class TokenExpiredException(CoRideException):
    """Exception raised when JWT token has expired."""
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = 'TOKEN_EXPIRED'
    message = 'Authentication token has expired'


class TokenInvalidException(CoRideException):
    """Exception raised when JWT token is invalid or malformed."""
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = 'TOKEN_INVALID'
    message = 'Authentication token is invalid'


class AccountSuspendedException(CoRideException):
    """Exception raised when user account is suspended."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = 'ACCOUNT_SUSPENDED'
    message = 'Your account has been suspended. Please contact support'


class AccountBannedException(CoRideException):
    """Exception raised when user account is permanently banned."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = 'ACCOUNT_BANNED'
    message = 'Your account has been permanently banned'


class PhoneNotVerifiedException(CoRideException):
    """Exception raised when phone number is not verified."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = 'PHONE_NOT_VERIFIED'
    message = 'Phone number must be verified to perform this action'


class EmailNotVerifiedException(CoRideException):
    """Exception raised when email address is not verified."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = 'EMAIL_NOT_VERIFIED'
    message = 'Email address must be verified to perform this action'


class AccountLockedException(CoRideException):
    """Exception raised when account is locked due to too many failed login attempts."""
    status_code = status.HTTP_423_LOCKED
    error_code = 'ACCOUNT_LOCKED'
    message = 'Account is temporarily locked due to too many failed login attempts'


# ============================================
# OTP EXCEPTIONS
# ============================================

class OTPExpiredException(CoRideException):
    """Exception raised when OTP has expired."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'OTP_EXPIRED'
    message = 'OTP has expired. Please request a new one'


class OTPInvalidException(CoRideException):
    """Exception raised when provided OTP is invalid."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'OTP_INVALID'
    message = 'Invalid OTP. Please check and try again'


class OTPAlreadyUsedException(CoRideException):
    """Exception raised when OTP has already been used."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'OTP_ALREADY_USED'
    message = 'OTP has already been used. Please request a new one'


class OTPLimitExceededException(CoRideException):
    """Exception raised when OTP request limit is exceeded."""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = 'OTP_LIMIT_EXCEEDED'
    message = 'Too many OTP requests. Please try again later'


class OTPSendFailedException(CoRideException):
    """Exception raised when OTP sending fails."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = 'OTP_SEND_FAILED'
    message = 'Failed to send OTP. Please try again'


# ============================================
# USER EXCEPTIONS
# ============================================

class UserNotFoundException(CoRideException):
    """Exception raised when user is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    error_code = 'USER_NOT_FOUND'
    message = 'User not found'


class UserAlreadyExistsException(CoRideException):
    """Exception raised when trying to create user that already exists."""
    status_code = status.HTTP_409_CONFLICT
    error_code = 'USER_ALREADY_EXISTS'
    message = 'User with this phone number already exists'


class ProfileIncompleteException(CoRideException):
    """Exception raised when user profile is incomplete."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'PROFILE_INCOMPLETE'
    message = 'Please complete your profile to continue'


class InvalidPhoneNumberException(CoRideException):
    """Exception raised when phone number format is invalid."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'INVALID_PHONE_NUMBER'
    message = 'Invalid phone number format'


# ============================================
# DRIVER EXCEPTIONS
# ============================================

class DriverNotFoundException(CoRideException):
    """Exception raised when driver is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    error_code = 'DRIVER_NOT_FOUND'
    message = 'Driver not found'


class DriverNotVerifiedException(CoRideException):
    """Exception raised when driver is not verified."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = 'DRIVER_NOT_VERIFIED'
    message = 'Driver verification is required to perform this action'


class DriverAlreadyRegisteredException(CoRideException):
    """Exception raised when user is already registered as driver."""
    status_code = status.HTTP_409_CONFLICT
    error_code = 'DRIVER_ALREADY_REGISTERED'
    message = 'You are already registered as a driver'


class DriverSuspendedException(CoRideException):
    """Exception raised when driver account is suspended."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = 'DRIVER_SUSPENDED'
    message = 'Your driver account has been suspended'


class VehicleNotFoundException(CoRideException):
    """Exception raised when vehicle is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    error_code = 'VEHICLE_NOT_FOUND'
    message = 'Vehicle not found'


class DocumentUploadFailedException(CoRideException):
    """Exception raised when document upload fails."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'DOCUMENT_UPLOAD_FAILED'
    message = 'Failed to upload document. Please try again'


# ============================================
# RIDE EXCEPTIONS
# ============================================

class RideNotFoundException(CoRideException):
    """Exception raised when ride is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    error_code = 'RIDE_NOT_FOUND'
    message = 'Ride not found'


class RideAlreadyStartedException(CoRideException):
    """Exception raised when trying to modify a ride that has already started."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'RIDE_ALREADY_STARTED'
    message = 'Cannot modify ride that has already started'


class RideAlreadyCompletedException(CoRideException):
    """Exception raised when trying to modify a completed ride."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'RIDE_ALREADY_COMPLETED'
    message = 'Ride has already been completed'


class RideAlreadyCancelledException(CoRideException):
    """Exception raised when trying to modify a cancelled ride."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'RIDE_ALREADY_CANCELLED'
    message = 'Ride has already been cancelled'


class RideExpiredException(CoRideException):
    """Exception raised when ride has expired."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'RIDE_EXPIRED'
    message = 'Ride has expired and is no longer available'


class InvalidRideStatusException(CoRideException):
    """Exception raised when ride status is invalid for the requested operation."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'INVALID_RIDE_STATUS'
    message = 'Invalid ride status for this operation'


class RideNotStartedException(CoRideException):
    """Exception raised when trying to perform action on ride that hasn't started."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'RIDE_NOT_STARTED'
    message = 'Ride has not started yet'


class InvalidRideOTPException(CoRideException):
    """Exception raised when ride start OTP is invalid."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'INVALID_RIDE_OTP'
    message = 'Invalid ride start OTP'


# ============================================
# BOOKING EXCEPTIONS
# ============================================

class BookingNotFoundException(CoRideException):
    """Exception raised when booking is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    error_code = 'BOOKING_NOT_FOUND'
    message = 'Booking not found'


class InsufficientSeatsException(CoRideException):
    """Exception raised when not enough seats are available."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'INSUFFICIENT_SEATS'
    message = 'Not enough seats available for this booking'


class BookingAlreadyCancelledException(CoRideException):
    """Exception raised when trying to modify a cancelled booking."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'BOOKING_ALREADY_CANCELLED'
    message = 'Booking has already been cancelled'


class BookingAlreadyConfirmedException(CoRideException):
    """Exception raised when trying to modify a confirmed booking."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'BOOKING_ALREADY_CONFIRMED'
    message = 'Booking has already been confirmed'


class CannotBookOwnRideException(CoRideException):
    """Exception raised when user tries to book their own ride."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'CANNOT_BOOK_OWN_RIDE'
    message = 'You cannot book your own ride'


class RideFullException(CoRideException):
    """Exception raised when ride is fully booked."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'RIDE_FULL'
    message = 'This ride is fully booked'


class DuplicateBookingException(CoRideException):
    """Exception raised when user tries to book the same ride twice."""
    status_code = status.HTTP_409_CONFLICT
    error_code = 'DUPLICATE_BOOKING'
    message = 'You have already booked this ride'


# ============================================
# PAYMENT EXCEPTIONS
# ============================================

class PaymentFailedException(CoRideException):
    """Exception raised when payment processing fails."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'PAYMENT_FAILED'
    message = 'Payment processing failed. Please try again'


class PaymentNotFoundException(CoRideException):
    """Exception raised when payment record is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    error_code = 'PAYMENT_NOT_FOUND'
    message = 'Payment record not found'


class RefundFailedException(CoRideException):
    """Exception raised when refund processing fails."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'REFUND_FAILED'
    message = 'Refund processing failed. Please contact support'


class InsufficientWalletBalanceException(CoRideException):
    """Exception raised when wallet balance is insufficient."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'INSUFFICIENT_WALLET_BALANCE'
    message = 'Insufficient wallet balance for this transaction'


class InvalidPaymentSignatureException(CoRideException):
    """Exception raised when payment signature verification fails."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'INVALID_PAYMENT_SIGNATURE'
    message = 'Invalid payment signature'


class PaymentAlreadyProcessedException(CoRideException):
    """Exception raised when payment has already been processed."""
    status_code = status.HTTP_409_CONFLICT
    error_code = 'PAYMENT_ALREADY_PROCESSED'
    message = 'Payment has already been processed'


class OrderCreationFailedException(CoRideException):
    """Exception raised when payment order creation fails."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = 'ORDER_CREATION_FAILED'
    message = 'Failed to create payment order. Please try again'


# ============================================
# LOCATION EXCEPTIONS
# ============================================

class InvalidCoordinatesException(CoRideException):
    """Exception raised when coordinates are invalid."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'INVALID_COORDINATES'
    message = 'Invalid latitude or longitude coordinates'


class GeocodingFailedException(CoRideException):
    """Exception raised when geocoding service fails."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = 'GEOCODING_FAILED'
    message = 'Failed to geocode address. Please try again'


class RouteCalculationFailedException(CoRideException):
    """Exception raised when route calculation fails."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = 'ROUTE_CALCULATION_FAILED'
    message = 'Failed to calculate route. Please try again'


# ============================================
# NOTIFICATION EXCEPTIONS
# ============================================

class NotificationSendFailedException(CoRideException):
    """Exception raised when notification sending fails."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = 'NOTIFICATION_SEND_FAILED'
    message = 'Failed to send notification'


class FCMTokenNotFoundException(CoRideException):
    """Exception raised when FCM token is not found for user."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = 'FCM_TOKEN_NOT_FOUND'
    message = 'Push notification token not found for user'


# ============================================
# PERMISSION EXCEPTIONS
# ============================================

class UnauthorizedActionException(CoRideException):
    """Exception raised when user is not authorized to perform action."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = 'UNAUTHORIZED_ACTION'
    message = 'You are not authorized to perform this action'


class ResourceOwnershipException(CoRideException):
    """Exception raised when user doesn't own the requested resource."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = 'RESOURCE_OWNERSHIP_ERROR'
    message = 'You can only access your own resources'


# ============================================
# EXPORTS
# ============================================

__all__ = [
    # Exception handler
    'custom_exception_handler',
    
    # Base exception
    'CoRideException',
    
    # Authentication exceptions
    'InvalidCredentialsException',
    'TokenExpiredException',
    'TokenInvalidException',
    'AccountSuspendedException',
    'AccountBannedException',
    'PhoneNotVerifiedException',
    'EmailNotVerifiedException',
    'AccountLockedException',
    
    # OTP exceptions
    'OTPExpiredException',
    'OTPInvalidException',
    'OTPAlreadyUsedException',
    'OTPLimitExceededException',
    'OTPSendFailedException',
    
    # User exceptions
    'UserNotFoundException',
    'UserAlreadyExistsException',
    'ProfileIncompleteException',
    'InvalidPhoneNumberException',
    
    # Driver exceptions
    'DriverNotFoundException',
    'DriverNotVerifiedException',
    'DriverAlreadyRegisteredException',
    'DriverSuspendedException',
    'VehicleNotFoundException',
    'DocumentUploadFailedException',
    
    # Ride exceptions
    'RideNotFoundException',
    'RideAlreadyStartedException',
    'RideAlreadyCompletedException',
    'RideAlreadyCancelledException',
    'RideExpiredException',
    'InvalidRideStatusException',
    'RideNotStartedException',
    'InvalidRideOTPException',
    
    # Booking exceptions
    'BookingNotFoundException',
    'InsufficientSeatsException',
    'BookingAlreadyCancelledException',
    'BookingAlreadyConfirmedException',
    'CannotBookOwnRideException',
    'RideFullException',
    'DuplicateBookingException',
    
    # Payment exceptions
    'PaymentFailedException',
    'PaymentNotFoundException',
    'RefundFailedException',
    'InsufficientWalletBalanceException',
    'InvalidPaymentSignatureException',
    'PaymentAlreadyProcessedException',
    'OrderCreationFailedException',
    
    # Location exceptions
    'InvalidCoordinatesException',
    'GeocodingFailedException',
    'RouteCalculationFailedException',
    
    # Notification exceptions
    'NotificationSendFailedException',
    'FCMTokenNotFoundException',
    
    # Permission exceptions
    'UnauthorizedActionException',
    'ResourceOwnershipException',
]