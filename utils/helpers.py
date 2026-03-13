"""
CoRide Platform - Helper Functions
===================================
Production-ready utility functions for the entire platform.
Includes OTP generation, distance calculation, pricing, formatting, and more.

Usage:
    from utils.helpers import generate_otp, calculate_distance, success_response
"""

import secrets
import string
import uuid
import hmac
import hashlib
import re
from datetime import datetime, timedelta
from decimal import Decimal
from math import radians, sin, cos, sqrt, atan2
from typing import Optional, Dict, Tuple
import pytz
from django.conf import settings
import logging

logger = logging.getLogger('coride')

# ============================================
# OTP AND ID GENERATION
# ============================================

def generate_otp(length: int = 6) -> str:
    """
    Generate cryptographically secure random numeric OTP.
    
    Args:
        length: Length of OTP (default: 6)
        
    Returns:
        String of random digits
        
    Example:
        >>> generate_otp(6)
        '847293'
    """
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def generate_ride_start_otp() -> str:
    """
    Generate 4-digit OTP for starting a ride.
    
    Returns:
        4-digit numeric string
        
    Example:
        >>> generate_ride_start_otp()
        '5829'
    """
    return generate_otp(length=4)


def generate_unique_id() -> str:
    """
    Generate unique UUID4 identifier.
    
    Returns:
        UUID4 as string
        
    Example:
        >>> generate_unique_id()
        'a3f2c8d1-4b5e-6f7a-8c9d-0e1f2a3b4c5d'
    """
    return str(uuid.uuid4())


def generate_booking_reference() -> str:
    """
    Generate unique booking reference code.
    
    Format: CR-YYYYMMDD-XXXXXX
    CR = CoRide prefix
    YYYYMMDD = Current date
    XXXXXX = Random alphanumeric (uppercase)
    
    Returns:
        Booking reference string
        
    Example:
        >>> generate_booking_reference()
        'CR-20240115-A3K9P2'
    """
    date_str = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return f'CR-{date_str}-{random_str}'


# ============================================
# LOCATION AND DISTANCE
# ============================================

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.
    
    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point
        
    Returns:
        Distance in kilometers (rounded to 2 decimal places)
        
    Example:
        >>> calculate_distance(28.6139, 77.2090, 19.0760, 72.8777)
        1151.89
    """
    # Handle same point
    if lat1 == lat2 and lon1 == lon2:
        return 0.0
    
    # Validate coordinates
    if not is_valid_coordinates(lat1, lon1) or not is_valid_coordinates(lat2, lon2):
        logger.error(f"Invalid coordinates: ({lat1}, {lon1}) or ({lat2}, {lon2})")
        return 0.0
    
    # Earth radius in kilometers
    R = 6371.0
    
    # Convert to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)


def calculate_eta(distance_km: float, avg_speed_kmh: int = 40) -> int:
    """
    Calculate estimated time of arrival in minutes.
    
    Args:
        distance_km: Distance in kilometers
        avg_speed_kmh: Average speed in km/h (default: 40)
        
    Returns:
        ETA in minutes (rounded up)
        
    Example:
        >>> calculate_eta(25.5, 50)
        31
    """
    if distance_km <= 0:
        return 0
    
    hours = distance_km / avg_speed_kmh
    minutes = int(hours * 60)
    return max(minutes, 1)  # Minimum 1 minute


def is_valid_coordinates(lat: float, lon: float) -> bool:
    """
    Validate latitude and longitude values.
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> is_valid_coordinates(28.6139, 77.2090)
        True
    """
    return -90 <= lat <= 90 and -180 <= lon <= 180


def get_nearby_radius_bounds(lat: float, lon: float, radius_km: float) -> Dict[str, float]:
    """
    Calculate bounding box for nearby search optimization.
    
    Much faster than calculating distance for every point.
    Use this for initial database filtering.
    
    Args:
        lat: Center latitude
        lon: Center longitude
        radius_km: Search radius in kilometers
        
    Returns:
        Dictionary with min/max lat/lon bounds
        
    Example:
        >>> get_nearby_radius_bounds(28.6139, 77.2090, 50)
        {'min_lat': 28.16, 'max_lat': 29.06, 'min_lon': 76.59, 'max_lon': 77.82}
    """
    # Approximate degrees per kilometer
    lat_degree_km = 111.0
    lon_degree_km = 111.0 * cos(radians(lat))
    
    lat_delta = radius_km / lat_degree_km
    lon_delta = radius_km / lon_degree_km
    
    return {
        'min_lat': round(lat - lat_delta, 6),
        'max_lat': round(lat + lat_delta, 6),
        'min_lon': round(lon - lon_delta, 6),
        'max_lon': round(lon + lon_delta, 6),
    }


def geocode_address(address: str) -> Optional[Dict[str, any]]:
    """
    Convert address to coordinates using Google Maps Geocoding API.
    
    Args:
        address: Address string to geocode
        
    Returns:
        Dictionary with lat, lon, formatted_address or None on error
        
    Example:
        >>> geocode_address("India Gate, New Delhi")
        {'lat': 28.6129, 'lon': 77.2295, 'formatted_address': 'India Gate, New Delhi, Delhi 110001'}
    """
    try:
        import googlemaps
        
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        result = gmaps.geocode(address)
        
        if result:
            location = result[0]['geometry']['location']
            return {
                'lat': location['lat'],
                'lon': location['lng'],
                'formatted_address': result[0]['formatted_address']
            }
        
        logger.warning(f"No geocoding results for address: {address}")
        return None
        
    except Exception as e:
        logger.error(f"Geocoding error for '{address}': {str(e)}")
        return None


# ============================================
# PRICING AND FINANCE
# ============================================

def calculate_ride_price(distance_km: float, price_per_km: Optional[Decimal] = None) -> Decimal:
    """
    Calculate total ride price based on distance.
    
    Args:
        distance_km: Distance in kilometers
        price_per_km: Price per kilometer (default: ₹8/km)
        
    Returns:
        Total price as Decimal
        
    Example:
        >>> calculate_ride_price(25.5)
        Decimal('204.00')
    """
    if price_per_km is None:
        price_per_km = Decimal('8.00')  # Default ₹8 per km
    
    total = Decimal(str(distance_km)) * price_per_km
    return total.quantize(Decimal('0.01'))


def calculate_platform_commission(amount: Decimal) -> Decimal:
    """
    Calculate platform commission (15% of amount).
    
    Args:
        amount: Total transaction amount
        
    Returns:
        Commission amount rounded to 2 decimal places
        
    Example:
        >>> calculate_platform_commission(Decimal('200.00'))
        Decimal('30.00')
    """
    commission_percent = Decimal(str(settings.PLATFORM_COMMISSION_PERCENT)) / Decimal('100')
    commission = amount * commission_percent
    return commission.quantize(Decimal('0.01'))


def calculate_driver_earnings(total_amount: Decimal) -> Decimal:
    """
    Calculate driver earnings after platform commission.
    
    Args:
        total_amount: Total ride amount
        
    Returns:
        Driver earnings (total - commission)
        
    Example:
        >>> calculate_driver_earnings(Decimal('200.00'))
        Decimal('170.00')
    """
    commission = calculate_platform_commission(total_amount)
    earnings = total_amount - commission
    return earnings.quantize(Decimal('0.01'))


def calculate_cancellation_charge(amount: Decimal, minutes_before_ride: int) -> Decimal:
    """
    Calculate cancellation charge based on time before ride.
    
    Rules:
    - Free cancellation if 30+ minutes before ride
    - 10% charge if less than 30 minutes before ride
    - Full charge if ride already started (negative minutes)
    
    Args:
        amount: Total booking amount
        minutes_before_ride: Minutes until ride starts (negative if started)
        
    Returns:
        Cancellation charge amount
        
    Example:
        >>> calculate_cancellation_charge(Decimal('200.00'), 45)
        Decimal('0.00')
        >>> calculate_cancellation_charge(Decimal('200.00'), 15)
        Decimal('20.00')
    """
    if minutes_before_ride >= settings.FREE_CANCELLATION_MINUTES:
        return Decimal('0.00')
    elif minutes_before_ride < 0:
        # Ride already started - full charge
        return amount
    else:
        # Less than 30 minutes - 10% charge
        charge_percent = Decimal(str(settings.CANCELLATION_CHARGE_PERCENT)) / Decimal('100')
        charge = amount * charge_percent
        return charge.quantize(Decimal('0.01'))


# ============================================
# PHONE AND EMAIL
# ============================================

def format_phone_number(phone: str) -> str:
    """
    Format phone number to E.164 format for India (+91).
    
    Args:
        phone: Phone number in various formats
        
    Returns:
        E.164 formatted phone number
        
    Example:
        >>> format_phone_number('9876543210')
        '+919876543210'
        >>> format_phone_number('09876543210')
        '+919876543210'
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Remove leading 0 if present
    if digits.startswith('0'):
        digits = digits[1:]
    
    # Remove country code if already present
    if digits.startswith('91') and len(digits) == 12:
        digits = digits[2:]
    
    # Add country code
    return f'+91{digits}'


def mask_phone_number(phone: str) -> str:
    """
    Mask middle digits of phone number for privacy.
    
    Args:
        phone: Phone number to mask
        
    Returns:
        Masked phone number
        
    Example:
        >>> mask_phone_number('+919876543210')
        '+91XXXXXX3210'
    """
    formatted = format_phone_number(phone)
    if len(formatted) >= 13:  # +91 + 10 digits
        return formatted[:3] + 'XXXXXX' + formatted[-4:]
    return formatted


def mask_email(email: str) -> str:
    """
    Mask email address for privacy.
    
    Args:
        email: Email address to mask
        
    Returns:
        Masked email address
        
    Example:
        >>> mask_email('john.doe@gmail.com')
        'jo****@gmail.com'
    """
    if '@' not in email:
        return email
    
    username, domain = email.split('@', 1)
    if len(username) <= 2:
        masked_username = username[0] + '*'
    else:
        masked_username = username[:2] + '****'
    
    return f'{masked_username}@{domain}'


def validate_indian_phone(phone: str) -> bool:
    """
    Validate Indian phone number format.
    
    Rules:
    - Must be 10 digits
    - Must start with 6, 7, 8, or 9
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> validate_indian_phone('9876543210')
        True
        >>> validate_indian_phone('1234567890')
        False
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Remove country code if present
    if digits.startswith('91') and len(digits) == 12:
        digits = digits[2:]
    
    # Remove leading 0 if present
    if digits.startswith('0'):
        digits = digits[1:]
    
    # Check length and starting digit
    return len(digits) == 10 and digits[0] in '6789'


# ============================================
# TIME AND DATE
# ============================================

def get_current_ist() -> datetime:
    """
    Get current datetime in Asia/Kolkata timezone.
    
    Returns:
        Current datetime with IST timezone
        
    Example:
        >>> get_current_ist()
        datetime.datetime(2024, 1, 15, 10, 30, 0, tzinfo=<DstTzInfo 'Asia/Kolkata'>)
    """
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)


def format_datetime_ist(dt: datetime) -> str:
    """
    Format datetime to readable string in IST.
    
    Args:
        dt: Datetime object to format
        
    Returns:
        Formatted string
        
    Example:
        >>> format_datetime_ist(datetime(2024, 1, 15, 10, 30))
        '15 Jan 2024, 10:30 AM'
    """
    ist = pytz.timezone('Asia/Kolkata')
    if dt.tzinfo is None:
        dt = ist.localize(dt)
    else:
        dt = dt.astimezone(ist)
    
    return dt.strftime('%d %b %Y, %I:%M %p')


def get_time_difference_minutes(dt1: datetime, dt2: datetime) -> int:
    """
    Calculate time difference between two datetimes in minutes.
    
    Args:
        dt1: First datetime
        dt2: Second datetime
        
    Returns:
        Difference in minutes (dt2 - dt1)
        
    Example:
        >>> get_time_difference_minutes(datetime(2024, 1, 15, 10, 0), datetime(2024, 1, 15, 10, 45))
        45
    """
    diff = dt2 - dt1
    return int(diff.total_seconds() / 60)


def is_future_datetime(dt: datetime) -> bool:
    """
    Check if datetime is in the future (IST).
    
    Args:
        dt: Datetime to check
        
    Returns:
        True if future, False otherwise
        
    Example:
        >>> is_future_datetime(datetime.now() + timedelta(hours=1))
        True
    """
    current = get_current_ist()
    
    # Make dt timezone-aware if needed
    if dt.tzinfo is None:
        ist = pytz.timezone('Asia/Kolkata')
        dt = ist.localize(dt)
    
    return dt > current


def get_ride_reminder_time(departure_time: datetime) -> datetime:
    """
    Calculate ride reminder time (30 minutes before departure).
    
    Args:
        departure_time: Ride departure datetime
        
    Returns:
        Reminder datetime
        
    Example:
        >>> get_ride_reminder_time(datetime(2024, 1, 15, 10, 0))
        datetime.datetime(2024, 1, 15, 9, 30)
    """
    return departure_time - timedelta(minutes=30)


# ============================================
# FILE AND IMAGE
# ============================================

def get_file_size_mb(file) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file: Django UploadedFile object
        
    Returns:
        File size in MB
        
    Example:
        >>> get_file_size_mb(uploaded_file)
        2.45
    """
    return round(file.size / (1024 * 1024), 2)


def get_file_extension(filename: str) -> str:
    """
    Extract file extension from filename.
    
    Args:
        filename: Name of the file
        
    Returns:
        Lowercase extension without dot
        
    Example:
        >>> get_file_extension('profile.JPG')
        'jpg'
    """
    return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''


def generate_upload_path(instance, filename: str, folder: str) -> str:
    """
    Generate Cloudinary upload path for files.
    
    Format: coride/{folder}/{user_id}/{uuid}.{ext}
    
    Args:
        instance: Model instance
        filename: Original filename
        folder: Folder name (profiles, documents, vehicles)
        
    Returns:
        Upload path string
        
    Example:
        >>> generate_upload_path(user, 'photo.jpg', 'profiles')
        'coride/profiles/123/a3f2c8d1.jpg'
    """
    ext = get_file_extension(filename)
    unique_name = str(uuid.uuid4())[:8]
    user_id = getattr(instance, 'user_id', getattr(instance, 'id', 'unknown'))
    
    return f'coride/{folder}/{user_id}/{unique_name}.{ext}'


def is_valid_image(file) -> bool:
    """
    Validate image file type and size.
    
    Args:
        file: Django UploadedFile object
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> is_valid_image(uploaded_file)
        True
    """
    # Check file extension
    allowed_extensions = ['jpg', 'jpeg', 'png', 'webp']
    ext = get_file_extension(file.name)
    
    if ext not in allowed_extensions:
        return False
    
    # Check file size (max 5MB)
    if get_file_size_mb(file) > 5:
        return False
    
    return True


# ============================================
# RESPONSE HELPERS
# ============================================

def success_response(data=None, message: str = "Success", status: int = 200) -> Dict:
    """
    Generate standard success response format.
    
    Args:
        data: Response data (optional)
        message: Success message
        status: HTTP status code
        
    Returns:
        Standardized success response dictionary
        
    Example:
        >>> success_response({'user_id': 123}, 'User created')
        {'success': True, 'message': 'User created', 'data': {'user_id': 123}, 'timestamp': '...'}
    """
    return {
        'success': True,
        'message': message,
        'data': data,
        'timestamp': get_current_ist().isoformat(),
    }


def error_response(message: str, error_code: Optional[str] = None, 
                  details: Optional[Dict] = None, status: int = 400) -> Dict:
    """
    Generate standard error response format.
    
    Args:
        message: Error message
        error_code: Error code identifier (optional)
        details: Additional error details (optional)
        status: HTTP status code
        
    Returns:
        Standardized error response dictionary
        
    Example:
        >>> error_response('Invalid phone number', 'INVALID_PHONE')
        {'success': False, 'message': 'Invalid phone number', 'error_code': 'INVALID_PHONE', ...}
    """
    response = {
        'success': False,
        'message': message,
        'timestamp': get_current_ist().isoformat(),
    }
    
    if error_code:
        response['error_code'] = error_code
    
    if details:
        response['details'] = details
    
    return response


def paginated_response(data: list, page: int, total: int, page_size: int) -> Dict:
    """
    Generate standard paginated response format.
    
    Args:
        data: List of items for current page
        page: Current page number
        total: Total number of items
        page_size: Items per page
        
    Returns:
        Standardized paginated response dictionary
        
    Example:
        >>> paginated_response([...], 1, 50, 20)
        {'success': True, 'data': [...], 'pagination': {...}}
    """
    total_pages = (total + page_size - 1) // page_size
    
    return {
        'success': True,
        'data': data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total_items': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_previous': page > 1,
        },
        'timestamp': get_current_ist().isoformat(),
    }


# ============================================
# SECURITY HELPERS
# ============================================

def generate_hmac_signature(payload: str, secret: str) -> str:
    """
    Generate HMAC SHA256 signature for webhook verification.
    
    Args:
        payload: Data to sign
        secret: Secret key
        
    Returns:
        Hexadecimal signature string
        
    Example:
        >>> generate_hmac_signature('order_123|payment_456', 'secret_key')
        'a3f2c8d1...'
    """
    signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    )
    return signature.hexdigest()


def verify_razorpay_signature(order_id: str, payment_id: str, signature: str) -> bool:
    """
    Verify Razorpay payment signature.
    
    Args:
        order_id: Razorpay order ID
        payment_id: Razorpay payment ID
        signature: Signature to verify
        
    Returns:
        True if signature is valid, False otherwise
        
    Example:
        >>> verify_razorpay_signature('order_123', 'pay_456', 'signature_abc')
        True
    """
    try:
        payload = f'{order_id}|{payment_id}'
        expected_signature = generate_hmac_signature(payload, settings.RAZORPAY_KEY_SECRET)
        return hmac.compare_digest(expected_signature, signature)
    except Exception as e:
        logger.error(f"Razorpay signature verification error: {str(e)}")
        return False


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS and injection attacks.
    
    Args:
        text: User input text
        
    Returns:
        Sanitized text
        
    Example:
        >>> sanitize_input('<script>alert("xss")</script>')
        'scriptalert("xss")/script'
    """
    if not text:
        return ''
    
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    
    # Remove dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()
