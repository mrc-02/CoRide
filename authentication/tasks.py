"""
CoRide Platform - Authentication Celery Tasks
==============================================
Background tasks for authentication module.

Tasks:
- cleanup_expired_otps: Remove expired OTP records from database
"""

import logging
from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from utils.helpers import get_current_ist

logger = logging.getLogger('coride')

# ============================================
# OTP CLEANUP TASK
# ============================================

@shared_task(
    bind=True,
    name='authentication.tasks.cleanup_expired_otps',
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def cleanup_expired_otps(self):
    """
    Cleanup expired OTP records from the database.
    
    This task runs every hour via Celery Beat scheduler.
    Deletes OTP records that are older than 10 minutes.
    
    Process:
    1. Calculate expiry time (current time - 10 minutes)
    2. Query OTP records older than expiry time
    3. Delete expired records
    4. Log count of deleted records
    
    Returns:
        dict: Result with count of deleted OTPs
        
    Raises:
        Exception: Any database or processing errors (will retry)
        
    Example:
        # Manual execution
        from authentication.tasks import cleanup_expired_otps
        result = cleanup_expired_otps.delay()
    """
    try:
        logger.info("Starting OTP cleanup task...")
        
        # Import here to avoid circular imports
        from authentication.models import OTP
        from utils.constants import OTP_EXPIRY_MINUTES
        
        # Calculate expiry time
        current_time = get_current_ist()
        expiry_time = current_time - timedelta(minutes=OTP_EXPIRY_MINUTES)
        
        # Find expired OTPs
        expired_otps = OTP.objects.filter(created_at__lt=expiry_time)
        count = expired_otps.count()
        
        # Delete expired OTPs
        if count > 0:
            expired_otps.delete()
            logger.info(f"Successfully deleted {count} expired OTP records")
        else:
            logger.info("No expired OTPs found")
        
        return {
            'success': True,
            'deleted_count': count,
            'expiry_time': expiry_time.isoformat(),
            'message': f'Deleted {count} expired OTP records'
        }
        
    except Exception as exc:
        logger.error(f"Error in cleanup_expired_otps task: {str(exc)}")
        
        # Retry the task with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


# ============================================
# ADDITIONAL AUTHENTICATION TASKS
# ============================================

@shared_task(
    bind=True,
    name='authentication.tasks.send_otp_sms',
    max_retries=3,
    default_retry_delay=30,
)
def send_otp_sms(self, phone_number, otp_code):
    """
    Send OTP via SMS using Twilio.
    
    This is an async task to avoid blocking the API response.
    
    Args:
        phone_number: Phone number to send OTP to
        otp_code: OTP code to send
        
    Returns:
        dict: Result with SMS status
        
    Example:
        from authentication.tasks import send_otp_sms
        send_otp_sms.delay('+919876543210', '123456')
    """
    try:
        logger.info(f"Sending OTP to {phone_number}")
        
        # Import Twilio client
        from twilio.rest import Client
        from django.conf import settings
        
        # Initialize Twilio client
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        
        # Send SMS
        message = client.messages.create(
            body=f'Your CoRide verification code is: {otp_code}. Valid for 10 minutes.',
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        logger.info(f"OTP sent successfully. SID: {message.sid}")
        
        return {
            'success': True,
            'message_sid': message.sid,
            'status': message.status,
        }
        
    except Exception as exc:
        logger.error(f"Error sending OTP SMS: {str(exc)}")
        raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))


@shared_task(
    bind=True,
    name='authentication.tasks.unlock_locked_accounts',
    max_retries=3,
    default_retry_delay=60,
)
def unlock_locked_accounts(self):
    """
    Unlock user accounts that were locked due to failed login attempts.
    
    Accounts are locked for 30 minutes after too many failed attempts.
    This task runs periodically to unlock accounts after the lockout period.
    
    Returns:
        dict: Result with count of unlocked accounts
    """
    try:
        logger.info("Starting account unlock task...")
        
        from users.models import User
        from utils.constants import ACCOUNT_LOCKOUT_MINUTES
        
        # Calculate unlock time
        current_time = get_current_ist()
        unlock_time = current_time - timedelta(minutes=ACCOUNT_LOCKOUT_MINUTES)
        
        # Find locked accounts that should be unlocked
        locked_users = User.objects.filter(
            is_locked=True,
            locked_at__lt=unlock_time
        )
        
        count = locked_users.count()
        
        # Unlock accounts
        if count > 0:
            locked_users.update(
                is_locked=False,
                locked_at=None,
                failed_login_attempts=0
            )
            logger.info(f"Successfully unlocked {count} user accounts")
        else:
            logger.info("No accounts to unlock")
        
        return {
            'success': True,
            'unlocked_count': count,
            'message': f'Unlocked {count} user accounts'
        }
        
    except Exception as exc:
        logger.error(f"Error in unlock_locked_accounts task: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
