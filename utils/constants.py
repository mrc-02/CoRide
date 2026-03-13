"""
CoRide Platform - Constants Module
===================================
Centralized constants for the entire carpooling platform.
All status codes, roles, types, and business logic limits defined here.

Usage:
    from utils.constants import UserRole, RideStatus, PLATFORM_COMMISSION_PERCENT
"""

# ============================================
# USER ROLES
# ============================================
class UserRole:
    """
    User role types in the CoRide platform.
    
    - PASSENGER: Regular user who books rides
    - DRIVER: User who offers rides
    - ADMIN: Platform administrator with limited access
    - SUPER_ADMIN: Full platform access and control
    """
    PASSENGER = 'passenger'
    DRIVER = 'driver'
    ADMIN = 'admin'
    SUPER_ADMIN = 'super_admin'
    
    CHOICES = [
        (PASSENGER, 'Passenger'),
        (DRIVER, 'Driver'),
        (ADMIN, 'Admin'),
        (SUPER_ADMIN, 'Super Admin'),
    ]


# ============================================
# RIDE STATUS
# ============================================
class RideStatus:
    """
    Ride lifecycle status codes.
    
    - CREATED: Ride created but not yet scheduled
    - SCHEDULED: Ride scheduled for future date/time
    - ACTIVE: Ride is available for booking
    - IN_PROGRESS: Ride has started and is ongoing
    - COMPLETED: Ride finished successfully
    - CANCELLED: Ride cancelled by driver
    - EXPIRED: Ride expired (past departure time without starting)
    """
    CREATED = 'created'
    SCHEDULED = 'scheduled'
    ACTIVE = 'active'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    EXPIRED = 'expired'
    
    CHOICES = [
        (CREATED, 'Created'),
        (SCHEDULED, 'Scheduled'),
        (ACTIVE, 'Active'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
        (EXPIRED, 'Expired'),
    ]


# ============================================
# BOOKING STATUS
# ============================================
class BookingStatus:
    """
    Booking lifecycle status codes.
    
    - PENDING: Booking created, awaiting confirmation
    - CONFIRMED: Booking confirmed by driver
    - CANCELLED_BY_PASSENGER: Passenger cancelled the booking
    - CANCELLED_BY_DRIVER: Driver cancelled the booking
    - COMPLETED: Booking completed successfully
    - NO_SHOW: Passenger didn't show up for the ride
    - REFUNDED: Payment refunded to passenger
    """
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED_BY_PASSENGER = 'cancelled_by_passenger'
    CANCELLED_BY_DRIVER = 'cancelled_by_driver'
    COMPLETED = 'completed'
    NO_SHOW = 'no_show'
    REFUNDED = 'refunded'
    
    CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (CANCELLED_BY_PASSENGER, 'Cancelled by Passenger'),
        (CANCELLED_BY_DRIVER, 'Cancelled by Driver'),
        (COMPLETED, 'Completed'),
        (NO_SHOW, 'No Show'),
        (REFUNDED, 'Refunded'),
    ]


# ============================================
# PAYMENT STATUS
# ============================================
class PaymentStatus:
    """
    Payment transaction status codes.
    
    - PENDING: Payment initiated but not processed
    - PROCESSING: Payment being processed by gateway
    - SUCCESS: Payment completed successfully
    - FAILED: Payment failed
    - REFUNDED: Full refund processed
    - PARTIALLY_REFUNDED: Partial refund processed
    """
    PENDING = 'pending'
    PROCESSING = 'processing'
    SUCCESS = 'success'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    PARTIALLY_REFUNDED = 'partially_refunded'
    
    CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (SUCCESS, 'Success'),
        (FAILED, 'Failed'),
        (REFUNDED, 'Refunded'),
        (PARTIALLY_REFUNDED, 'Partially Refunded'),
    ]


# ============================================
# PAYMENT METHOD
# ============================================
class PaymentMethod:
    """
    Payment method types supported by CoRide.
    
    - UPI: Unified Payments Interface (India)
    - CARD: Credit/Debit card
    - NET_BANKING: Internet banking
    - WALLET: Third-party wallets (Paytm, PhonePe, etc.)
    - CORIDE_WALLET: CoRide platform wallet
    - CASH: Cash payment (for specific scenarios)
    """
    UPI = 'upi'
    CARD = 'card'
    NET_BANKING = 'net_banking'
    WALLET = 'wallet'
    CORIDE_WALLET = 'coride_wallet'
    CASH = 'cash'
    
    CHOICES = [
        (UPI, 'UPI'),
        (CARD, 'Card'),
        (NET_BANKING, 'Net Banking'),
        (WALLET, 'Wallet'),
        (CORIDE_WALLET, 'CoRide Wallet'),
        (CASH, 'Cash'),
    ]


# ============================================
# DRIVER VERIFICATION STATUS
# ============================================
class DriverVerificationStatus:
    """
    Driver verification and approval status.
    
    - PENDING: Driver registered, documents not submitted
    - DOCUMENTS_SUBMITTED: All documents uploaded
    - UNDER_REVIEW: Admin reviewing documents
    - APPROVED: Driver verified and approved
    - REJECTED: Driver verification rejected
    - SUSPENDED: Driver account suspended
    """
    PENDING = 'pending'
    DOCUMENTS_SUBMITTED = 'documents_submitted'
    UNDER_REVIEW = 'under_review'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    SUSPENDED = 'suspended'
    
    CHOICES = [
        (PENDING, 'Pending'),
        (DOCUMENTS_SUBMITTED, 'Documents Submitted'),
        (UNDER_REVIEW, 'Under Review'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (SUSPENDED, 'Suspended'),
    ]


# ============================================
# VEHICLE TYPE
# ============================================
class VehicleType:
    """
    Vehicle types supported on CoRide platform.
    
    - SEDAN: 4-door sedan cars
    - SUV: Sport Utility Vehicles
    - HATCHBACK: Compact hatchback cars
    - MUV: Multi Utility Vehicles
    - AUTO: Auto rickshaw (3-wheeler)
    - BIKE: Two-wheeler motorcycle
    """
    SEDAN = 'sedan'
    SUV = 'suv'
    HATCHBACK = 'hatchback'
    MUV = 'muv'
    AUTO = 'auto'
    BIKE = 'bike'
    
    CHOICES = [
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (HATCHBACK, 'Hatchback'),
        (MUV, 'MUV'),
        (AUTO, 'Auto'),
        (BIKE, 'Bike'),
    ]


# ============================================
# NOTIFICATION TYPE
# ============================================
class NotificationType:
    """
    Push notification types for various platform events.
    
    Covers booking, ride, payment, verification, and system notifications.
    """
    BOOKING_CONFIRMED = 'booking_confirmed'
    BOOKING_CANCELLED = 'booking_cancelled'
    RIDE_STARTING_SOON = 'ride_starting_soon'
    DRIVER_ARRIVING = 'driver_arriving'
    RIDE_STARTED = 'ride_started'
    RIDE_COMPLETED = 'ride_completed'
    PAYMENT_SUCCESS = 'payment_success'
    PAYMENT_FAILED = 'payment_failed'
    REFUND_PROCESSED = 'refund_processed'
    PROMO_CODE = 'promo_code'
    ACCOUNT_VERIFIED = 'account_verified'
    DOCUMENT_APPROVED = 'document_approved'
    DOCUMENT_REJECTED = 'document_rejected'
    SYSTEM_ALERT = 'system_alert'
    
    CHOICES = [
        (BOOKING_CONFIRMED, 'Booking Confirmed'),
        (BOOKING_CANCELLED, 'Booking Cancelled'),
        (RIDE_STARTING_SOON, 'Ride Starting Soon'),
        (DRIVER_ARRIVING, 'Driver Arriving'),
        (RIDE_STARTED, 'Ride Started'),
        (RIDE_COMPLETED, 'Ride Completed'),
        (PAYMENT_SUCCESS, 'Payment Success'),
        (PAYMENT_FAILED, 'Payment Failed'),
        (REFUND_PROCESSED, 'Refund Processed'),
        (PROMO_CODE, 'Promo Code'),
        (ACCOUNT_VERIFIED, 'Account Verified'),
        (DOCUMENT_APPROVED, 'Document Approved'),
        (DOCUMENT_REJECTED, 'Document Rejected'),
        (SYSTEM_ALERT, 'System Alert'),
    ]


# ============================================
# OTP PURPOSE
# ============================================
class OTPPurpose:
    """
    OTP (One-Time Password) usage purposes.
    
    - SIGNUP: New user registration
    - LOGIN: User login verification
    - FORGOT_PASSWORD: Password reset
    - PHONE_VERIFY: Phone number verification
    - RIDE_START: OTP to start ride (driver verification)
    """
    SIGNUP = 'signup'
    LOGIN = 'login'
    FORGOT_PASSWORD = 'forgot_password'
    PHONE_VERIFY = 'phone_verify'
    RIDE_START = 'ride_start'
    
    CHOICES = [
        (SIGNUP, 'Signup'),
        (LOGIN, 'Login'),
        (FORGOT_PASSWORD, 'Forgot Password'),
        (PHONE_VERIFY, 'Phone Verification'),
        (RIDE_START, 'Ride Start'),
    ]


# ============================================
# GENDER
# ============================================
class Gender:
    """
    Gender options for user profiles.
    
    Includes privacy option for users who prefer not to disclose.
    """
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'
    PREFER_NOT_TO_SAY = 'prefer_not_to_say'
    
    CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other'),
        (PREFER_NOT_TO_SAY, 'Prefer Not to Say'),
    ]


# ============================================
# INCIDENT TYPE
# ============================================
class IncidentType:
    """
    Types of incidents that can be reported during rides.
    
    Used for safety and dispute resolution.
    """
    ACCIDENT = 'accident'
    HARASSMENT = 'harassment'
    FRAUD = 'fraud'
    ROUTE_DEVIATION = 'route_deviation'
    VEHICLE_BREAKDOWN = 'vehicle_breakdown'
    PAYMENT_DISPUTE = 'payment_dispute'
    OTHER = 'other'
    
    CHOICES = [
        (ACCIDENT, 'Accident'),
        (HARASSMENT, 'Harassment'),
        (FRAUD, 'Fraud'),
        (ROUTE_DEVIATION, 'Route Deviation'),
        (VEHICLE_BREAKDOWN, 'Vehicle Breakdown'),
        (PAYMENT_DISPUTE, 'Payment Dispute'),
        (OTHER, 'Other'),
    ]


# ============================================
# DOCUMENT TYPE
# ============================================
class DocumentType:
    """
    Document types required for driver verification.
    
    All documents must be uploaded and verified before driver approval.
    """
    DRIVING_LICENSE = 'driving_license'
    AADHAAR = 'aadhaar'
    PAN_CARD = 'pan_card'
    VEHICLE_REGISTRATION = 'vehicle_registration'
    VEHICLE_INSURANCE = 'vehicle_insurance'
    VEHICLE_PHOTO = 'vehicle_photo'
    PROFILE_PHOTO = 'profile_photo'
    
    CHOICES = [
        (DRIVING_LICENSE, 'Driving License'),
        (AADHAAR, 'Aadhaar Card'),
        (PAN_CARD, 'PAN Card'),
        (VEHICLE_REGISTRATION, 'Vehicle Registration'),
        (VEHICLE_INSURANCE, 'Vehicle Insurance'),
        (VEHICLE_PHOTO, 'Vehicle Photo'),
        (PROFILE_PHOTO, 'Profile Photo'),
    ]


# ============================================
# RIDE PREFERENCES
# ============================================
class RidePreference:
    """
    Ride preferences and amenities offered by drivers.
    
    Passengers can filter rides based on these preferences.
    """
    AC = 'ac'
    NON_AC = 'non_ac'
    MUSIC_ALLOWED = 'music_allowed'
    NO_MUSIC = 'no_music'
    PETS_ALLOWED = 'pets_allowed'
    NO_PETS = 'no_pets'
    SMOKING_ALLOWED = 'smoking_allowed'
    NO_SMOKING = 'no_smoking'
    WOMEN_ONLY = 'women_only'
    
    CHOICES = [
        (AC, 'AC'),
        (NON_AC, 'Non-AC'),
        (MUSIC_ALLOWED, 'Music Allowed'),
        (NO_MUSIC, 'No Music'),
        (PETS_ALLOWED, 'Pets Allowed'),
        (NO_PETS, 'No Pets'),
        (SMOKING_ALLOWED, 'Smoking Allowed'),
        (NO_SMOKING, 'No Smoking'),
        (WOMEN_ONLY, 'Women Only'),
    ]


# ============================================
# ADMIN ROLES
# ============================================
class AdminRole:
    """
    Admin panel role types with different permission levels.
    
    - SUPER_ADMIN: Full platform access
    - OPERATIONS_ADMIN: Manage rides, drivers, users
    - FINANCE_ADMIN: Handle payments, refunds, settlements
    - SUPPORT_AGENT: Customer support and ticket resolution
    - SAFETY_TEAM: Handle safety incidents and reports
    - MODERATOR: Content moderation and user reports
    - ANALYST: View analytics and reports (read-only)
    """
    SUPER_ADMIN = 'super_admin'
    OPERATIONS_ADMIN = 'operations_admin'
    FINANCE_ADMIN = 'finance_admin'
    SUPPORT_AGENT = 'support_agent'
    SAFETY_TEAM = 'safety_team'
    MODERATOR = 'moderator'
    ANALYST = 'analyst'
    
    CHOICES = [
        (SUPER_ADMIN, 'Super Admin'),
        (OPERATIONS_ADMIN, 'Operations Admin'),
        (FINANCE_ADMIN, 'Finance Admin'),
        (SUPPORT_AGENT, 'Support Agent'),
        (SAFETY_TEAM, 'Safety Team'),
        (MODERATOR, 'Moderator'),
        (ANALYST, 'Analyst'),
    ]


# ============================================
# PLATFORM LIMITS AND BUSINESS RULES
# ============================================
"""
Platform-wide limits and business logic constants.
These values control core platform behavior and can be overridden via settings.
"""

# Ride and booking limits
MAX_SEATS_PER_RIDE = 6
MAX_SEATS_PER_BOOKING = 6
MAX_ACTIVE_RIDES_PER_DRIVER = 1

# Pricing limits (in INR)
MIN_RIDE_PRICE = 10
MAX_RIDE_PRICE = 10000

# Commission and charges
PLATFORM_COMMISSION_PERCENT = 15
CANCELLATION_CHARGE_PERCENT = 10
FREE_CANCELLATION_WINDOW_MINUTES = 30

# Search and discovery
RIDE_SEARCH_RADIUS_KM = 50
MAX_RIDE_SEARCH_RADIUS_KM = 100

# OTP configuration
OTP_LENGTH = 6
RIDE_START_OTP_LENGTH = 4
OTP_EXPIRY_MINUTES = 10

# File upload limits (in MB)
MAX_PROFILE_PHOTO_SIZE_MB = 5
MAX_DOCUMENT_SIZE_MB = 10

# Rating and quality
DRIVER_RATING_MINIMUM = 3.0

# Security and rate limiting
MAX_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCKOUT_MINUTES = 30

# Booking time windows
MIN_RIDE_ADVANCE_BOOKING_MINUTES = 30
MAX_RIDE_ADVANCE_BOOKING_DAYS = 30


# ============================================
# EXPORTS
# ============================================
__all__ = [
    # User and roles
    'UserRole',
    'Gender',
    'AdminRole',
    
    # Ride management
    'RideStatus',
    'RidePreference',
    'VehicleType',
    
    # Booking management
    'BookingStatus',
    
    # Payment management
    'PaymentStatus',
    'PaymentMethod',
    
    # Driver management
    'DriverVerificationStatus',
    'DocumentType',
    
    # Notifications
    'NotificationType',
    
    # Security
    'OTPPurpose',
    
    # Safety
    'IncidentType',
    
    # Platform limits
    'MAX_SEATS_PER_RIDE',
    'MAX_SEATS_PER_BOOKING',
    'MIN_RIDE_PRICE',
    'MAX_RIDE_PRICE',
    'OTP_LENGTH',
    'RIDE_START_OTP_LENGTH',
    'MAX_PROFILE_PHOTO_SIZE_MB',
    'MAX_DOCUMENT_SIZE_MB',
    'PLATFORM_COMMISSION_PERCENT',
    'CANCELLATION_CHARGE_PERCENT',
    'FREE_CANCELLATION_WINDOW_MINUTES',
    'RIDE_SEARCH_RADIUS_KM',
    'MAX_RIDE_SEARCH_RADIUS_KM',
    'DRIVER_RATING_MINIMUM',
    'OTP_EXPIRY_MINUTES',
    'MAX_LOGIN_ATTEMPTS',
    'ACCOUNT_LOCKOUT_MINUTES',
    'MAX_ACTIVE_RIDES_PER_DRIVER',
    'MIN_RIDE_ADVANCE_BOOKING_MINUTES',
    'MAX_RIDE_ADVANCE_BOOKING_DAYS',
]
