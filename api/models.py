from django.db import models
from django.core.validators import MinValueValidator, EmailValidator
from django.utils import timezone 
import pytz
import logging 

logger = logging.getLogger(__name__)

class FitnessClass(models.Model):

    """
    Represents a fitness class offered by the studio
    """
    CLASS_TYPES = [
        ('yoga', 'Yoga'),
        ('zumba', 'Zumba'),
        ('hiit', 'HIIT'),
        ('pilates', 'Pilates'),
        ('cardio', 'Cardio'),
    ]

    name = models.CharField(max_length=100, help_text="Name of the fitness class")
    class_type = models.CharField(max_length=20, choices=CLASS_TYPES)
    instructor_name = models.CharField(max_length=100)
    scheduled_datetime = models.DateTimeField(help_text="Class start time in IST")
    duration_minutes = models.PositiveIntegerField(default=60)
    total_slots = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], 
        help_text="Maximum number of participants"
    )
    available_slots = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        help_text="Current available slots"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_datetime']
        indexes = [
            models.Index(fields=['scheduled_datetime', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.instructor_name} ({self.scheduled_datetime})"
    
    def save(self, *args , **kwargs):
        # available slots shouldn't exceed total slots
        if self.available_slots > self.total_slots:
            self.available_slots = self.total_slots 
        super().save(*args, **kwargs)
    
    def get_datetime_in_timezone(self,target_timezone):
        ''' convert class datetime to specific timezone'''
        try:
            tz = pytz.timezone(target_timezone)
            return self.scheduled_datetime.astimezone(tz)
        except pytz.exceptions.UnknownTimeZoneError:
            logger.warning(f"Unknown timezone: {target_timezone}, returning IST")
            return self.scheduled_datetime
    @property
    def is_fully_booked(self):
        return self.available_slots == 0
    
    @property
    def is_upcoming(self):
        return self.scheduled_datetime > timezone.now()

class Booking(models.Model):
    """ represents the booking done by a client for fitness class  """

    fitness_class = models.ForeignKey(
        FitnessClass, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField(validators=[EmailValidator()])
    booking_reference = models.CharField(max_length=20, unique=True)
    booking_datetime = models.DateTimeField(auto_now_add=True)
    is_cancelled = models.BooleanField(default=False)
    
    class Meta:
        # Prevent duplicate bookings for same email and class
        unique_together = ['fitness_class', 'client_email']
        indexes = [
            models.Index(fields=['client_email']),
            models.Index(fields=['booking_reference']),
        ]
    
    def __str__(self):
        return f"{self.client_name} - {self.fitness_class.name} ({self.booking_reference})"
    
    def save(self, *args, **kwargs):
        # Generate booking reference if not exists
        if not self.booking_reference:
            self.booking_reference = self.generate_booking_ref()
        super().save(*args, **kwargs)
    
    def generate_booking_ref(self):
        """Generate unique booking reference"""
        import random
        import string
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=8))



