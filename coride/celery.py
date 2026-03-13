"""
CoRide Platform - Celery Configuration
=======================================
Celery application configuration for background task processing.

Handles:
- OTP cleanup
- Ride reminders and notifications
- Payment processing
- Daily reports
- Scheduled periodic tasks

Usage:
    # Start Celery worker
    celery -A coride worker -l info
    
    # Start Celery beat scheduler
    celery -A coride beat -l info
    
    # Start both together
    celery -A coride worker -B -l info
"""

import os
import logging
from celery import Celery
from celery.signals import after_setup_logger, task_failure, task_success
from django.conf import settings

# Set default Django settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coride.settings')

# Create Celery application
app = Celery('coride')

# Load configuration from Django settings with CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed Django apps
# Looks for tasks.py in each app
app.autodiscover_tasks()

# Configure timezone
app.conf.timezone = 'Asia/Kolkata'
app.conf.enable_utc = False

# Configure task result backend
app.conf.result_backend = settings.CELERY_RESULT_BACKEND
app.conf.broker_url = settings.CELERY_BROKER_URL

# Task serialization
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']

# Task execution settings
app.conf.task_track_started = True
app.conf.task_time_limit = 30 * 60  # 30 minutes hard limit
app.conf.task_soft_time_limit = 25 * 60  # 25 minutes soft limit
app.conf.task_acks_late = True  # Acknowledge task after completion
app.conf.worker_prefetch_multiplier = 1  # One task at a time per worker

# Result backend settings
app.conf.result_expires = 3600  # Results expire after 1 hour

# ============================================
# CELERY BEAT SCHEDULE (Periodic Tasks)
# ============================================

app.conf.beat_schedule = {
    # Cleanup expired OTPs every hour
    'cleanup-expired-otps': {
        'task': 'authentication.tasks.cleanup_expired_otps',
        'schedule': 3600.0,  # Every hour (in seconds)
        'options': {
            'expires': 3500,  # Task expires if not executed within 58 minutes
        },
    },
    
    # Send ride reminders every 30 minutes
    'send-ride-reminders': {
        'task': 'rides.tasks.send_ride_reminders',
        'schedule': 1800.0,  # Every 30 minutes
        'options': {
            'expires': 1700,  # Task expires if not executed within 28 minutes
        },
    },
    
    # Update expired rides every 5 minutes
    'update-expired-rides': {
        'task': 'rides.tasks.update_expired_rides',
        'schedule': 300.0,  # Every 5 minutes
        'options': {
            'expires': 280,  # Task expires if not executed within 4.5 minutes
        },
    },
    
    # Process pending payouts daily at midnight IST
    'process-pending-payouts': {
        'task': 'payments.tasks.process_pending_payouts',
        'schedule': {
            'hour': 0,
            'minute': 0,
        },
        'options': {
            'expires': 3600,  # Task expires if not executed within 1 hour
        },
    },
    
    # Send daily reports at 9 AM IST
    'send-daily-reports': {
        'task': 'admin_panel.tasks.send_daily_reports',
        'schedule': {
            'hour': 9,
            'minute': 0,
        },
        'options': {
            'expires': 3600,  # Task expires if not executed within 1 hour
        },
    },
}

# ============================================
# LOGGING CONFIGURATION
# ============================================

logger = logging.getLogger('coride')


@after_setup_logger.connect
def setup_celery_logging(logger, *args, **kwargs):
    """Configure Celery logging after logger setup."""
    logger.info("=" * 60)
    logger.info("CoRide Celery Worker Starting")
    logger.info("=" * 60)
    logger.info(f"Broker: {app.conf.broker_url}")
    logger.info(f"Result Backend: {app.conf.result_backend}")
    logger.info(f"Timezone: {app.conf.timezone}")
    logger.info(f"Registered Tasks: {len(app.tasks)}")
    logger.info("=" * 60)


@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    """Log successful task completion."""
    logger.info(f"Task {sender.name} completed successfully")


@task_failure.connect
def task_failure_handler(sender=None, exception=None, traceback=None, **kwargs):
    """Log task failures."""
    logger.error(f"Task {sender.name} failed with exception: {exception}")
    logger.error(f"Traceback: {traceback}")


# ============================================
# CELERY SIGNALS
# ============================================

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """
    Configure periodic tasks after Celery is configured.
    
    This signal is called after Celery configuration is complete.
    Use it to add additional periodic tasks or log configuration.
    """
    logger.info("Celery Beat Scheduler configured with periodic tasks:")
    for task_name, task_config in app.conf.beat_schedule.items():
        schedule = task_config.get('schedule')
        if isinstance(schedule, dict):
            logger.info(f"  - {task_name}: Daily at {schedule.get('hour')}:{schedule.get('minute'):02d}")
        else:
            logger.info(f"  - {task_name}: Every {schedule} seconds")


# ============================================
# DEBUG TASK
# ============================================

@app.task(bind=True)
def debug_task(self):
    """
    Debug task to test Celery configuration.
    
    Usage:
        from coride.celery import debug_task
        debug_task.delay()
    """
    logger.info(f'Request: {self.request!r}')
    return 'Celery is working!'


# ============================================
# ERROR HANDLING
# ============================================

class CeleryTaskError(Exception):
    """Base exception for Celery task errors."""
    pass


def handle_task_error(task, exc, task_id, args, kwargs, einfo):
    """
    Global error handler for all Celery tasks.
    
    Args:
        task: Task instance
        exc: Exception raised
        task_id: Task ID
        args: Task positional arguments
        kwargs: Task keyword arguments
        einfo: Exception info
    """
    logger.error(f"Task {task.name} [{task_id}] failed")
    logger.error(f"Exception: {exc}")
    logger.error(f"Args: {args}")
    logger.error(f"Kwargs: {kwargs}")
    logger.error(f"Exception Info: {einfo}")


# Register global error handler
app.conf.task_annotations = {
    '*': {
        'on_failure': handle_task_error,
    }
}


# ============================================
# PRODUCTION NOTES
# ============================================
"""
DEPLOYMENT CHECKLIST:

1. Install Redis:
   - Windows: Download from https://github.com/microsoftarchive/redis/releases
   - Linux: sudo apt-get install redis-server
   - Start: redis-server

2. Start Celery Worker:
   celery -A coride worker -l info --pool=solo (Windows)
   celery -A coride worker -l info (Linux/Mac)

3. Start Celery Beat (Scheduler):
   celery -A coride beat -l info

4. Start Both Together:
   celery -A coride worker -B -l info --pool=solo (Windows)

5. Production Deployment:
   - Use supervisor or systemd to manage Celery processes
   - Run multiple workers for high availability
   - Monitor with Flower: celery -A coride flower
   - Set up proper logging and error tracking

6. Monitoring:
   - Install Flower: pip install flower
   - Run: celery -A coride flower
   - Access: http://localhost:5555

7. Environment Variables:
   - Ensure CELERY_BROKER_URL is set in .env
   - Ensure CELERY_RESULT_BACKEND is set in .env
   - Redis must be running and accessible

8. Task Queues (Optional):
   - Create separate queues for different task priorities
   - Route tasks to specific queues
   - Scale workers per queue

Example systemd service file (Linux):
-------------------------------------
[Unit]
Description=CoRide Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/coride
ExecStart=/path/to/venv/bin/celery -A coride worker -l info
Restart=always

[Install]
WantedBy=multi-user.target
"""
