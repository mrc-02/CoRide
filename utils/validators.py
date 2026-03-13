"""
CoRide Platform - Validators Module
====================================
Django/DRF compatible validators for the entire carpooling platform.
All validators raise ValidationError with clear error messages.

Usage:
    from utils.validators import validate_phone_number, validate_driving_license
    
    # In Django models
    phone = models.CharField(validators=[validate_phone_number])
    
    # In DRF serializers
    phone = serializers.CharField(validators=[validate_phone_number])
"""

import re
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Union, Any
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from utils.constants import MIN_RIDE_PRICE, MAX_RIDE_PRICE, MIN_RIDE_ADVANCE_BOOKING_MINUTES
from utils.helpers import get_current_ist

# ============================================
# PHONE VALIDATORS
# ============================================

def validate_phone_number(value: str) -> None:
    """
    Validate Indian mobile number format.
    
    Rules:
    - Must be exactly 10 digits
    - Must start with 6, 7, 8, or 9
    - No country code or special characters
    
    Args:
        value: Phone number string to validate
        
    Raises:
        ValidationError: If phone number is invalid
        
    Example:
        >>> validate_phone_number('9876543210')  # Valid
        >>> validate_phone_number('1234567890')  # Invalid - starts with 1
    """
    if not value:
        raise ValidationError('Phone number is required.')
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', str(value))
    
    # Remove leading 0 if present
    if digits.startswith('0'):
        digits = digits[1:]
    
    # Check length
    if len(digits) != 10:
        raise ValidationError('Phone number must be exactly 10 digits.')
    
    # Check starting digit
    if not digits[0] in '6789':
        raise ValidationError('Phone number must start with 6, 7, 8, or 9.')
    
    # Check if all digits
    if not digits.isdigit():
        raise ValidationError('Phone number must contain only digits.')


def validate_phone_with_country_code(value: str) -> None:
    """
    Validate phone number in E.164 format with Indian country code.
    
    Rules:
    - Must start with +91
    - Followed by exactly 10 digits
    - Total length: 13 characters
    
    Args:
        value: Phone number string to validate
        
    Raises:
        ValidationError: If phone number format is invalid
        
    Example:
        >>> validate_phone_with_country_code('+919876543210')  # Valid
        >>> validate_phone_with_country_code('919876543210')   # Invalid - no +
    """
    if not value:
        raise ValidationError('Phone number with country code is required.')
    
    # Check format
    pattern = r'^\+91[6-9]\d{9}$'
    if not re.match(pattern, str(value)):
        raise ValidationError(
            'Phone number must be in format +919876543210 '
            '(+91 followed by 10 digits starting with 6, 7, 8, or 9).'
        )


# ============================================
# DOCUMENT VALIDATORS
# ============================================

def validate_driving_license(value: str) -> None:
    """
    Validate Indian driving license number format.
    
    Format: XX00XXXXXXXXXX
    - State code: 2 letters
    - RTO code: 2 digits  
    - Year: 4 digits
    - Serial number: 7 digits
    
    Args:
        value: Driving license number to validate
        
    Raises:
        ValidationError: If format is invalid
        
    Example:
        >>> validate_driving_license('MH1220230001234')  # Valid
        >>> validate_driving_license('123456789012345')  # Invalid
    """
    if not value:
        raise ValidationError('Driving license number is required.')
    
    # Convert to uppercase and remove spaces
    dl_number = str(value).upper().replace(' ', '')
    
    # Check length
    if len(dl_number) != 15:
        raise ValidationError('Driving license number must be exactly 15 characters.')
    
    # Check format: 2 letters + 2 digits + 4 digits + 7 digits
    pattern = r'^[A-Z]{2}\d{2}\d{4}\d{7}$'
    if not re.match(pattern, dl_number):
        raise ValidationError(
            'Invalid driving license format. Expected format: XX00XXXXXXXXXX '
            '(2 letters + 2 digits + 4 digits + 7 digits).'
        )


def validate_vehicle_registration(value: str) -> None:
    """
    Validate Indian vehicle registration number format.
    
    Formats supported:
    - XX00XX0000 (old format)
    - XX00XXX0000 (new format)
    
    Args:
        value: Vehicle registration number to validate
        
    Raises:
        ValidationError: If format is invalid
        
    Example:
        >>> validate_vehicle_registration('MH12AB1234')   # Valid
        >>> validate_vehicle_registration('KA01MNP9999')  # Valid
    """
    if not value:
        raise ValidationError('Vehicle registration number is required.')
    
    # Convert to uppercase and remove spaces/hyphens
    reg_number = str(value).upper().replace(' ', '').replace('-', '')
    
    # Check old format: XX00XX0000
    old_pattern = r'^[A-Z]{2}\d{2}[A-Z]{2}\d{4}$'
    # Check new format: XX00XXX0000  
    new_pattern = r'^[A-Z]{2}\d{2}[A-Z]{3}\d{4}$'
    
    if not (re.match(old_pattern, reg_number) or re.match(new_pattern, reg_number)):
        raise ValidationError(
            'Invalid vehicle registration format. Expected formats: '
            'XX00XX0000 or XX00XXX0000 (state code + RTO + letters + numbers).'
        )


def validate_aadhaar_number(value: str) -> None:
    """
    Validate Indian Aadhaar number format and basic checksum.
    
    Rules:
    - Exactly 12 digits
    - Cannot start with 0 or 1
    - Basic Verhoeff algorithm check
    
    Args:
        value: Aadhaar number to validate
        
    Raises:
        ValidationError: If Aadhaar number is invalid
        
    Example:
        >>> validate_aadhaar_number('234567890123')  # Valid format
        >>> validate_aadhaar_number('123456789012')  # Invalid - starts with 1
    """
    if not value:
        raise ValidationError('Aadhaar number is required.')
    
    # Remove spaces and hyphens
    aadhaar = re.sub(r'[\s-]', '', str(value))
    
    # Check length
    if len(aadhaar) != 12:
        raise ValidationError('Aadhaar number must be exactly 12 digits.')
    
    # Check if all digits
    if not aadhaar.isdigit():
        raise ValidationError('Aadhaar number must contain only digits.')
    
    # Check starting digit
    if aadhaar[0] in '01':
        raise ValidationError('Aadhaar number cannot start with 0 or 1.')
    
    # Basic Verhoeff algorithm check (simplified)
    if not _verify_aadhaar_checksum(aadhaar):
        raise ValidationError('Invalid Aadhaar number checksum.')


def _verify_aadhaar_checksum(aadhaar: str) -> bool:
    """
    Simplified Verhoeff algorithm check for Aadhaar validation.
    
    Args:
        aadhaar: 12-digit Aadhaar number
        
    Returns:
        True if checksum is valid, False otherwise
    """
    # Verhoeff multiplication table
    multiplication_table = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
        [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
        [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
        [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
        [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
        [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
        [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
        [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    ]
    
    # Permutation table
    permutation_table = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
        [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
        [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
        [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
        [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
        [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
        [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
    ]
    
    check = 0
    for i, digit in enumerate(reversed(aadhaar)):
        check = multiplication_table[check][permutation_table[i % 8][int(digit)]]
    
    return check == 0


def validate_pan_number(value: str) -> None:
    """
    Validate Indian PAN (Permanent Account Number) format.
    
    Format: AAAAA0000A
    - 5 letters + 4 digits + 1 letter
    - Case insensitive
    
    Args:
        value: PAN number to validate
        
    Raises:
        ValidationError: If PAN format is invalid
        
    Example:
        >>> validate_pan_number('ABCDE1234F')  # Valid
        >>> validate_pan_number('12345ABCDE')  # Invalid
    """
    if not value:
        raise ValidationError('PAN number is required.')
    
    # Convert to uppercase and remove spaces
    pan = str(value).upper().replace(' ', '')
    
    # Check length
    if len(pan) != 10:
        raise ValidationError('PAN number must be exactly 10 characters.')
    
    # Check format: 5 letters + 4 digits + 1 letter
    pattern = r'^[A-Z]{5}\d{4}[A-Z]$'
    if not re.match(pattern, pan):
        raise ValidationError(
            'Invalid PAN format. Expected format: AAAAA0000A '
            '(5 letters + 4 digits + 1 letter).'
        )


# ============================================
# FILE VALIDATORS
# ============================================

def validate_image_file(file: UploadedFile) -> None:
    """
    Validate image file type and size.
    
    Rules:
    - Allowed types: jpg, jpeg, png, webp
    - Maximum size: 5MB
    
    Args:
        file: Django UploadedFile object
        
    Raises:
        ValidationError: If file is invalid
        
    Example:
        >>> validate_image_file(uploaded_image)  # Valid JPG under 5MB
    """
    if not file:
        raise ValidationError('Image file is required.')
    
    # Check file extension
    allowed_extensions = ['jpg', 'jpeg', 'png', 'webp']
    file_extension = file.name.rsplit('.', 1)[-1].lower() if '.' in file.name else ''
    
    if file_extension not in allowed_extensions:
        raise ValidationError(
            f'Invalid image format. Allowed formats: {", ".join(allowed_extensions).upper()}.'
        )
    
    # Check file size (5MB = 5 * 1024 * 1024 bytes)
    max_size = 5 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError('Image file size cannot exceed 5MB.')


def validate_document_file(file: UploadedFile) -> None:
    """
    Validate document file type and size.
    
    Rules:
    - Allowed types: jpg, jpeg, png, pdf
    - Maximum size: 10MB
    
    Args:
        file: Django UploadedFile object
        
    Raises:
        ValidationError: If file is invalid
        
    Example:
        >>> validate_document_file(uploaded_pdf)  # Valid PDF under 10MB
    """
    if not file:
        raise ValidationError('Document file is required.')
    
    # Check file extension
    allowed_extensions = ['jpg', 'jpeg', 'png', 'pdf']
    file_extension = file.name.rsplit('.', 1)[-1].lower() if '.' in file.name else ''
    
    if file_extension not in allowed_extensions:
        raise ValidationError(
            f'Invalid document format. Allowed formats: {", ".join(allowed_extensions).upper()}.'
        )
    
    # Check file size (10MB = 10 * 1024 * 1024 bytes)
    max_size = 10 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError('Document file size cannot exceed 10MB.')


# ============================================
# LOCATION VALIDATORS
# ============================================

def validate_latitude(value: float) -> None:
    """
    Validate latitude coordinate.
    
    Rules:
    - Must be between -90 and 90 degrees
    
    Args:
        value: Latitude value to validate
        
    Raises:
        ValidationError: If latitude is invalid
        
    Example:
        >>> validate_latitude(28.6139)   # Valid
        >>> validate_latitude(95.0)     # Invalid - exceeds range
    """
    try:
        lat = float(value)
    except (TypeError, ValueError):
        raise ValidationError('Latitude must be a valid number.')
    
    if not -90 <= lat <= 90:
        raise ValidationError('Latitude must be between -90 and 90 degrees.')


def validate_longitude(value: float) -> None:
    """
    Validate longitude coordinate.
    
    Rules:
    - Must be between -180 and 180 degrees
    
    Args:
        value: Longitude value to validate
        
    Raises:
        ValidationError: If longitude is invalid
        
    Example:
        >>> validate_longitude(77.2090)  # Valid
        >>> validate_longitude(185.0)   # Invalid - exceeds range
    """
    try:
        lon = float(value)
    except (TypeError, ValueError):
        raise ValidationError('Longitude must be a valid number.')
    
    if not -180 <= lon <= 180:
        raise ValidationError('Longitude must be between -180 and 180 degrees.')


def validate_coordinates(lat: float, lon: float) -> None:
    """
    Validate latitude and longitude coordinates for India.
    
    Rules:
    - Valid lat/lon ranges
    - Within India bounding box:
      * Latitude: 6.0 to 37.6
      * Longitude: 68.7 to 97.4
    
    Args:
        lat: Latitude value
        lon: Longitude value
        
    Raises:
        ValidationError: If coordinates are invalid or outside India
        
    Example:
        >>> validate_coordinates(28.6139, 77.2090)  # Valid - New Delhi
        >>> validate_coordinates(40.7128, -74.0060) # Invalid - New York
    """
    # First validate individual coordinates
    validate_latitude(lat)
    validate_longitude(lon)
    
    # Check if coordinates are within India bounding box
    india_lat_min, india_lat_max = 6.0, 37.6
    india_lon_min, india_lon_max = 68.7, 97.4
    
    if not (india_lat_min <= lat <= india_lat_max):
        raise ValidationError('Latitude must be within India (6.0 to 37.6 degrees).')
    
    if not (india_lon_min <= lon <= india_lon_max):
        raise ValidationError('Longitude must be within India (68.7 to 97.4 degrees).')


# ============================================
# RIDE VALIDATORS
# ============================================

def validate_seat_count(value: int) -> None:
    """
    Validate number of available seats in a ride.
    
    Rules:
    - Must be integer between 1 and 6
    
    Args:
        value: Number of seats to validate
        
    Raises:
        ValidationError: If seat count is invalid
        
    Example:
        >>> validate_seat_count(4)   # Valid
        >>> validate_seat_count(8)   # Invalid - exceeds maximum
    """
    try:
        seats = int(value)
    except (TypeError, ValueError):
        raise ValidationError('Seat count must be a valid integer.')
    
    if not 1 <= seats <= 6:
        raise ValidationError('Seat count must be between 1 and 6.')


def validate_price(value: Union[int, float, Decimal]) -> None:
    """
    Validate ride price amount.
    
    Rules:
    - Must be positive number
    - Minimum: ₹10 (from constants)
    - Maximum: ₹10,000 (from constants)
    
    Args:
        value: Price amount to validate
        
    Raises:
        ValidationError: If price is invalid
        
    Example:
        >>> validate_price(150)     # Valid
        >>> validate_price(5)       # Invalid - below minimum
        >>> validate_price(15000)   # Invalid - above maximum
    """
    try:
        price = Decimal(str(value))
    except (TypeError, ValueError):
        raise ValidationError('Price must be a valid number.')
    
    if price <= 0:
        raise ValidationError('Price must be greater than zero.')
    
    if price < MIN_RIDE_PRICE:
        raise ValidationError(f'Price cannot be less than ₹{MIN_RIDE_PRICE}.')
    
    if price > MAX_RIDE_PRICE:
        raise ValidationError(f'Price cannot be more than ₹{MAX_RIDE_PRICE}.')


def validate_future_datetime(value: datetime) -> None:
    """
    Validate that datetime is at least 30 minutes in the future.
    
    Rules:
    - Must be at least 30 minutes from now
    - Prevents booking rides too close to departure
    
    Args:
        value: Datetime to validate
        
    Raises:
        ValidationError: If datetime is not far enough in future
        
    Example:
        >>> validate_future_datetime(datetime.now() + timedelta(hours=2))  # Valid
        >>> validate_future_datetime(datetime.now() + timedelta(minutes=10)) # Invalid
    """
    if not isinstance(value, datetime):
        raise ValidationError('Invalid datetime format.')
    
    current_time = get_current_ist()
    min_future_time = current_time + timedelta(minutes=MIN_RIDE_ADVANCE_BOOKING_MINUTES)
    
    if value <= min_future_time:
        raise ValidationError(
            f'Departure time must be at least {MIN_RIDE_ADVANCE_BOOKING_MINUTES} minutes in the future.'
        )


def validate_departure_not_too_far(value: datetime) -> None:
    """
    Validate that departure time is not too far in the future.
    
    Rules:
    - Must be within 30 days from now
    - Prevents booking rides too far in advance
    
    Args:
        value: Departure datetime to validate
        
    Raises:
        ValidationError: If datetime is too far in future
        
    Example:
        >>> validate_departure_not_too_far(datetime.now() + timedelta(days=15))  # Valid
        >>> validate_departure_not_too_far(datetime.now() + timedelta(days=45))  # Invalid
    """
    if not isinstance(value, datetime):
        raise ValidationError('Invalid datetime format.')
    
    current_time = get_current_ist()
    max_future_time = current_time + timedelta(days=30)
    
    if value > max_future_time:
        raise ValidationError('Departure time cannot be more than 30 days in the future.')


# ============================================
# USER VALIDATORS
# ============================================

def validate_full_name(value: str) -> None:
    """
    Validate user's full name format.
    
    Rules:
    - Minimum 2 characters
    - Only letters, spaces, dots, hyphens allowed
    - No numbers or special characters
    
    Args:
        value: Full name to validate
        
    Raises:
        ValidationError: If name format is invalid
        
    Example:
        >>> validate_full_name('John Doe')        # Valid
        >>> validate_full_name('John123')        # Invalid - contains numbers
        >>> validate_full_name('Mary-Jane Smith') # Valid
    """
    if not value:
        raise ValidationError('Full name is required.')
    
    name = str(value).strip()
    
    # Check minimum length
    if len(name) < 2:
        raise ValidationError('Full name must be at least 2 characters long.')
    
    # Check for valid characters only (letters, spaces, dots, hyphens)
    pattern = r'^[a-zA-Z\s.-]+$'
    if not re.match(pattern, name):
        raise ValidationError(
            'Full name can only contain letters, spaces, dots, and hyphens.'
        )
    
    # Check for consecutive spaces
    if '  ' in name:
        raise ValidationError('Full name cannot contain consecutive spaces.')


def validate_age(dob: date) -> None:
    """
    Validate user's age based on date of birth.
    
    Rules:
    - User must be at least 18 years old
    - Date of birth cannot be in the future
    
    Args:
        dob: Date of birth to validate
        
    Raises:
        ValidationError: If age requirements are not met
        
    Example:
        >>> validate_age(date(1990, 5, 15))  # Valid - over 18
        >>> validate_age(date(2010, 5, 15))  # Invalid - under 18
    """
    if not isinstance(dob, date):
        raise ValidationError('Invalid date of birth format.')
    
    today = date.today()
    
    # Check if date is in the future
    if dob > today:
        raise ValidationError('Date of birth cannot be in the future.')
    
    # Calculate age
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    
    if age < 18:
        raise ValidationError('You must be at least 18 years old to use CoRide.')


def validate_password_strength(value: str) -> List[str]:
    """
    Validate password strength and return list of unmet requirements.
    
    Requirements:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter  
    - At least 1 digit
    - At least 1 special character
    - Cannot be entirely numeric
    
    Args:
        value: Password to validate
        
    Returns:
        List of unmet requirements (empty if password is strong)
        
    Example:
        >>> validate_password_strength('Password123!')  # Returns []
        >>> validate_password_strength('weak')          # Returns list of issues
    """
    if not value:
        return ['Password is required.']
    
    password = str(value)
    issues = []
    
    # Check minimum length
    if len(password) < 8:
        issues.append('Password must be at least 8 characters long.')
    
    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        issues.append('Password must contain at least one uppercase letter.')
    
    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        issues.append('Password must contain at least one lowercase letter.')
    
    # Check for digit
    if not re.search(r'\d', password):
        issues.append('Password must contain at least one digit.')
    
    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        issues.append('Password must contain at least one special character.')
    
    # Check if entirely numeric
    if password.isdigit():
        issues.append('Password cannot be entirely numeric.')
    
    return issues


# ============================================
# RATING VALIDATORS
# ============================================

def validate_rating(value: float) -> None:
    """
    Validate rating value.
    
    Rules:
    - Must be between 1.0 and 5.0
    - Must be in increments of 0.5
    
    Args:
        value: Rating value to validate
        
    Raises:
        ValidationError: If rating is invalid
        
    Example:
        >>> validate_rating(4.5)  # Valid
        >>> validate_rating(3.7)  # Invalid - not in 0.5 increments
        >>> validate_rating(6.0)  # Invalid - exceeds maximum
    """
    try:
        rating = float(value)
    except (TypeError, ValueError):
        raise ValidationError('Rating must be a valid number.')
    
    # Check range
    if not 1.0 <= rating <= 5.0:
        raise ValidationError('Rating must be between 1.0 and 5.0.')
    
    # Check increments of 0.5
    if (rating * 2) % 1 != 0:
        raise ValidationError('Rating must be in increments of 0.5 (e.g., 1.0, 1.5, 2.0).')


# ============================================
# PROMO CODE VALIDATORS
# ============================================

def validate_promo_code_format(value: str) -> None:
    """
    Validate promo code format.
    
    Rules:
    - Uppercase letters and numbers only
    - Length between 4 and 20 characters
    - No spaces or special characters
    
    Args:
        value: Promo code to validate
        
    Raises:
        ValidationError: If promo code format is invalid
        
    Example:
        >>> validate_promo_code_format('SAVE20')     # Valid
        >>> validate_promo_code_format('save-20')    # Invalid - lowercase and hyphen
        >>> validate_promo_code_format('AB')         # Invalid - too short
    """
    if not value:
        raise ValidationError('Promo code is required.')
    
    code = str(value).strip()
    
    # Check length
    if not 4 <= len(code) <= 20:
        raise ValidationError('Promo code must be between 4 and 20 characters long.')
    
    # Check format (uppercase letters and numbers only)
    pattern = r'^[A-Z0-9]+$'
    if not re.match(pattern, code):
        raise ValidationError(
            'Promo code can only contain uppercase letters and numbers. '
            'No spaces or special characters allowed.'
        )