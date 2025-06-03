from rest_framework import serializers
from django.utils import timezone
from .models import FitnessClass, Booking
import pytz
import logging

logger = logging.getLogger(__name__)

class FitnessClassSerializer(serializers.ModelSerializer):
    """
    Serializer for fitness class data with timezone conversion
    """
    scheduled_datetime_local = serializers.SerializerMethodField()
    
    class Meta:
        model = FitnessClass
        fields = [
            'id', 'name', 'class_type', 'instructor_name', 
            'scheduled_datetime', 'scheduled_datetime_local', 
            'duration_minutes', 'total_slots', 'available_slots'
        ]
    
    def get_scheduled_datetime_local(self, obj):
        """
        Return datetime in user's timezone if provided in context
        """
        request = self.context.get('request')
        if request and hasattr(request, 'META'):
            user_timezone = request.META.get('HTTP_X_TIMEZONE', 'Asia/Kolkata')
            try:
                return obj.get_datetime_in_timezone(user_timezone).isoformat()
            except Exception as e:
                logger.error(f"Timezone conversion error: {e}")
                return obj.scheduled_datetime.isoformat()
        return obj.scheduled_datetime.isoformat()

class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new bookings
    """
    class_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Booking
        fields = ['class_id', 'client_name', 'client_email']
    
    def validate_class_id(self, value):
        """Check if class exists and has available slots"""
        try:
            fitness_class = FitnessClass.objects.get(id=value, is_active=True)
        except FitnessClass.DoesNotExist:
            raise serializers.ValidationError("Invalid class ID or class not available")
        
        if not fitness_class.is_upcoming:
            raise serializers.ValidationError("Cannot book past classes")
        
        if fitness_class.is_fully_booked:
            raise serializers.ValidationError("Sorry, this class is fully booked")
        
        return value
    
    def validate_client_email(self, value):
        """Basic email validation"""
        if not value or '@' not in value:
            raise serializers.ValidationError("Please provide a valid email address")
        return value.lower()
    
    def validate(self, attrs):
        """Check for duplicate bookings"""
        class_id = attrs['class_id']
        client_email = attrs['client_email']
        
        if Booking.objects.filter(
            fitness_class_id=class_id, 
            client_email=client_email,
            is_cancelled=False
        ).exists():
            raise serializers.ValidationError(
                "You've already booked this class. Multiple bookings not allowed."
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create booking and update available slots"""
        class_id = validated_data.pop('class_id')
        fitness_class = FitnessClass.objects.select_for_update().get(id=class_id)
        
        # Double-check availability (race condition protection)
        if fitness_class.available_slots <= 0:
            raise serializers.ValidationError("Class just got fully booked")
        
        # Create booking
        booking = Booking.objects.create(
            fitness_class=fitness_class,
            **validated_data
        )
        
        # Update available slots
        fitness_class.available_slots -= 1
        fitness_class.save()
        
        logger.info(f"New booking created: {booking.booking_reference}")
        return booking

class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying booking information
    """
    class_name = serializers.CharField(source='fitness_class.name', read_only=True)
    class_datetime = serializers.DateTimeField(source='fitness_class.scheduled_datetime', read_only=True)
    instructor = serializers.CharField(source='fitness_class.instructor_name', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'booking_reference', 'class_name', 'class_datetime', 
            'instructor', 'client_name', 'booking_datetime'
        ]