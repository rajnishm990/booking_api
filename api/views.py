from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from .models import FitnessClass, Booking
from .serializers import (
    FitnessClassSerializer, 
    BookingCreateSerializer, 
    BookingSerializer
)
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
def get_classes(request):
    """
    GET /api/classes
    Returns list of upcoming fitness classes with available slots
    """
    try:
        # Only show upcoming classes that are active
        classes = FitnessClass.objects.filter(
            scheduled_datetime__gt=timezone.now(),
            is_active=True
        ).order_by('scheduled_datetime')
        
        serializer = FitnessClassSerializer(
            classes, 
            many=True, 
            context={'request': request}
        )
        
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        })
        
    except Exception as e:
        logger.error(f"Error fetching classes: {str(e)}")
        return Response({
            'success': False,
            'error': 'Something went wrong while fetching classes'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_booking(request):
    """
    POST /api/book
    Creates a new booking for a fitness class
    """
    try:
        serializer = BookingCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Use transaction to prevent race conditions
        with transaction.atomic():
            booking = serializer.save()
        
        # Return booking details
        booking_data = BookingSerializer(booking).data
        
        return Response({
            'success': True,
            'message': 'Booking created successfully!',
            'data': booking_data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Booking creation error: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to create booking. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_user_bookings(request):
    """
    GET /api/bookings?email=user@example.com
    Returns all bookings for a specific email address
    """
    try:
        email = request.query_params.get('email')
        
        if not email:
            return Response({
                'success': False,
                'error': 'Email parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        bookings = Booking.objects.filter(
            client_email=email.lower(),
            is_cancelled=False
        ).select_related('fitness_class').order_by('-booking_datetime')
        
        if not bookings.exists():
            return Response({
                'success': True,
                'message': 'No bookings found for this email',
                'data': []
            })
        
        serializer = BookingSerializer(bookings, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        })
        
    except Exception as e:
        logger.error(f"Error fetching user bookings: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to fetch bookings'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
