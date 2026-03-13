"""
CoRide Platform - Rides Celery Tasks
=====================================
Background tasks for rides module.

Tasks:
- send_ride_reminders: Send notifications to passengers before ride starts
- update_expired_rides: Mark rides as expired if departure time has passed
"""

import logging
from datetime import timedelta
from celery import shared_task
from django.db.models import Q
from utils.helpers import get_current_ist

logger = logging.getLogger('coride')

# ============================================
# RIDE REMINDERS TASK
# ============================================

@shared_task(
    bind=True,
    name='rides.tasks.send_ride_reminders',
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def send_ride_reminders(self):
    """
    Send ride reminder notifications to passengers.
    
    This task runs every 30 minutes via Celery Beat scheduler.
    Finds rides starting in the next 30 minutes and sends push
    notifications to all confirmed passengers.
    
    Process:
    1. Find rides with departure_time in next 30 minutes
    2. Get all confirmed bookings for these rides
    3. Send push notification to each passenger
    4. Mark ride as reminder_sent to avoid duplicate notifications
    5. Log count of notifications sent
    
    Returns:
        dict: Result with count of reminders sent
        
    Raises:
        Exception: Any database or notification errors (will retry)
        
    Example:
        # Manual execution
        from rides.tasks import send_ride_reminders
        result = send_ride_reminders.delay()
    """
    try:
        logger.info("Starting ride reminders task...")
        
        # Import here to avoid circular imports
        from rides.models import Ride
        from bookings.models import Booking
        from notifications.tasks import send_push_notification
        from utils.constants import RideStatus, BookingStatus
        
        # Calculate time window (next 30 minutes)
        current_time = get_current_ist()
        reminder_time = current_time + timedelta(minutes=30)
        
        # Find rides starting in next 30 minutes that haven't been reminded
        upcoming_rides = Ride.objects.filter(
            status__in=[RideStatus.SCHEDULED, RideStatus.ACTIVE],
            departure_time__gte=current_time,
            departure_time__lte=reminder_time,
            reminder_sent=False
        )
        
        reminder_count = 0
        
        for ride in upcoming_rides:
            # Get all confirmed bookings for this ride
            confirmed_bookings = Booking.objects.filter(
                ride=ride,
                status=BookingStatus.CONFIRMED
            ).select_related('passenger')
            
            # Send notification to each passenger
            for booking in confirmed_bookings:
                try:
                    # Send push notification asynchronously
                    send_push_notification.delay(
                        user_id=booking.passenger.id,
                        title='Ride Starting Soon',
                        body=f'Your ride from {ride.origin_name} to {ride.destination_name} starts in 30 minutes!',
                        data={
                            'type': 'ride_reminder',
                            'ride_id': ride.id,
                            'booking_id': booking.id,
                            'departure_time': ride.departure_time.isoformat(),
                        }
                    )
                    reminder_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to send reminder for booking {booking.id}: {str(e)}")
            
            # Mark ride as reminded
            ride.reminder_sent = True
            ride.save(update_fields=['reminder_sent'])
            
            logger.info(f"Sent reminders for ride {ride.id} to {confirmed_bookings.count()} passengers")
        
        logger.info(f"Successfully sent {reminder_count} ride reminders")
        
        return {
            'success': True,
            'reminder_count': reminder_count,
            'rides_processed': upcoming_rides.count(),
            'message': f'Sent {reminder_count} ride reminders'
        }
        
    except Exception as exc:
        logger.error(f"Error in send_ride_reminders task: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


# ============================================
# UPDATE EXPIRED RIDES TASK
# ============================================

@shared_task(
    bind=True,
    name='rides.tasks.update_expired_rides',
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def update_expired_rides(self):
    """
    Update status of rides that have expired.
    
    This task runs every 5 minutes via Celery Beat scheduler.
    Finds scheduled rides whose departure time has passed and
    marks them as expired. Notifies all passengers.
    
    Process:
    1. Find scheduled rides with departure_time in the past
    2. Mark rides as EXPIRED
    3. Get all confirmed bookings for expired rides
    4. Send notification to passengers about ride expiration
    5. Log count of expired rides
    
    Returns:
        dict: Result with count of expired rides
        
    Raises:
        Exception: Any database or notification errors (will retry)
        
    Example:
        # Manual execution
        from rides.tasks import update_expired_rides
        result = update_expired_rides.delay()
    """
    try:
        logger.info("Starting update expired rides task...")
        
        # Import here to avoid circular imports
        from rides.models import Ride
        from bookings.models import Booking
        from notifications.tasks import send_push_notification
        from utils.constants import RideStatus, BookingStatus
        
        # Get current time
        current_time = get_current_ist()
        
        # Find rides that should be expired
        expired_rides = Ride.objects.filter(
            status__in=[RideStatus.SCHEDULED, RideStatus.ACTIVE],
            departure_time__lt=current_time
        )
        
        expired_count = expired_rides.count()
        notification_count = 0
        
        for ride in expired_rides:
            # Update ride status to EXPIRED
            ride.status = RideStatus.EXPIRED
            ride.save(update_fields=['status'])
            
            # Get all confirmed bookings
            confirmed_bookings = Booking.objects.filter(
                ride=ride,
                status=BookingStatus.CONFIRMED
            ).select_related('passenger')
            
            # Notify passengers about ride expiration
            for booking in confirmed_bookings:
                try:
                    # Update booking status
                    booking.status = BookingStatus.CANCELLED_BY_DRIVER
                    booking.save(update_fields=['status'])
                    
                    # Send notification
                    send_push_notification.delay(
                        user_id=booking.passenger.id,
                        title='Ride Expired',
                        body=f'The ride from {ride.origin_name} to {ride.destination_name} has expired.',
                        data={
                            'type': 'ride_expired',
                            'ride_id': ride.id,
                            'booking_id': booking.id,
                        }
                    )
                    notification_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to notify passenger for booking {booking.id}: {str(e)}")
            
            logger.info(f"Marked ride {ride.id} as expired and notified {confirmed_bookings.count()} passengers")
        
        if expired_count > 0:
            logger.info(f"Successfully marked {expired_count} rides as expired")
        else:
            logger.info("No expired rides found")
        
        return {
            'success': True,
            'expired_count': expired_count,
            'notifications_sent': notification_count,
            'message': f'Marked {expired_count} rides as expired'
        }
        
    except Exception as exc:
        logger.error(f"Error in update_expired_rides task: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


# ============================================
# ADDITIONAL RIDE TASKS
# ============================================

@shared_task(
    bind=True,
    name='rides.tasks.auto_complete_rides',
    max_retries=3,
    default_retry_delay=60,
)
def auto_complete_rides(self):
    """
    Automatically complete rides that are in progress for too long.
    
    Finds rides in IN_PROGRESS status for more than 12 hours
    and marks them as COMPLETED.
    
    Returns:
        dict: Result with count of auto-completed rides
    """
    try:
        logger.info("Starting auto-complete rides task...")
        
        from rides.models import Ride
        from utils.constants import RideStatus
        
        # Get current time
        current_time = get_current_ist()
        auto_complete_time = current_time - timedelta(hours=12)
        
        # Find rides in progress for too long
        stale_rides = Ride.objects.filter(
            status=RideStatus.IN_PROGRESS,
            actual_start_time__lt=auto_complete_time
        )
        
        count = stale_rides.count()
        
        if count > 0:
            # Mark as completed
            stale_rides.update(
                status=RideStatus.COMPLETED,
                actual_end_time=current_time
            )
            logger.info(f"Auto-completed {count} stale rides")
        else:
            logger.info("No stale rides found")
        
        return {
            'success': True,
            'completed_count': count,
            'message': f'Auto-completed {count} stale rides'
        }
        
    except Exception as exc:
        logger.error(f"Error in auto_complete_rides task: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(
    bind=True,
    name='rides.tasks.calculate_ride_statistics',
    max_retries=3,
    default_retry_delay=60,
)
def calculate_ride_statistics(self, ride_id):
    """
    Calculate and update ride statistics after completion.
    
    Args:
        ride_id: ID of the completed ride
        
    Returns:
        dict: Result with calculated statistics
    """
    try:
        logger.info(f"Calculating statistics for ride {ride_id}")
        
        from rides.models import Ride
        from bookings.models import Booking
        from utils.constants import BookingStatus
        from utils.helpers import calculate_distance
        
        ride = Ride.objects.get(id=ride_id)
        
        # Calculate actual distance if GPS tracking was used
        if hasattr(ride, 'tracking_points') and ride.tracking_points.exists():
            total_distance = 0
            points = list(ride.tracking_points.order_by('timestamp'))
            
            for i in range(len(points) - 1):
                distance = calculate_distance(
                    points[i].latitude,
                    points[i].longitude,
                    points[i + 1].latitude,
                    points[i + 1].longitude
                )
                total_distance += distance
            
            ride.actual_distance = total_distance
        
        # Calculate passenger count
        completed_bookings = Booking.objects.filter(
            ride=ride,
            status=BookingStatus.COMPLETED
        )
        ride.actual_passenger_count = completed_bookings.count()
        
        # Calculate total earnings
        total_earnings = sum(booking.amount for booking in completed_bookings)
        ride.total_earnings = total_earnings
        
        ride.save()
        
        logger.info(f"Statistics calculated for ride {ride_id}")
        
        return {
            'success': True,
            'ride_id': ride_id,
            'actual_distance': float(ride.actual_distance) if ride.actual_distance else None,
            'passenger_count': ride.actual_passenger_count,
            'total_earnings': float(total_earnings),
        }
        
    except Exception as exc:
        logger.error(f"Error calculating ride statistics: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
