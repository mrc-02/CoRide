from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    """
    # Phone number field
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    
    # Profile picture using Cloudinary
    profile_picture = models.CharField(max_length=500, blank=True, null=True)
    
    # User type: rider, driver, or both
    USER_TYPE_CHOICES = (
        ('rider', 'Rider'),
        ('driver', 'Driver'),
        ('both', 'Both (Rider & Driver)'),
    )
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='rider'
    )
    
    # Additional fields
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=255, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Verification fields
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    # Account status
    is_active = models.BooleanField(default=True)
    is_banned = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['user_type']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def is_driver(self):
        return self.user_type in ['driver', 'both']
    
    def is_rider(self):
        return self.user_type in ['rider', 'both']
