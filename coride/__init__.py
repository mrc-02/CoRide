"""
CoRide Platform - Main Package Initialization
==============================================
Initializes the CoRide Django application and Celery worker.

This ensures that the Celery app is loaded when Django starts,
allowing Celery to discover and register all tasks.
"""

# Platform metadata
__version__ = '1.0.0'
__platform__ = 'CoRide'
__description__ = 'Production-ready carpooling platform'

# Import Celery app to ensure it's loaded with Django
# This makes sure that shared_task decorator works properly
from .celery import app as celery_app

# Make Celery app available at package level
__all__ = ('celery_app',)
