from django.test import TestCase
from django.urls import reverse 
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import timedelta
from .models import FitnessClass, Booking

class FitnessClassModelTest(TestCase):
    def setUp(self):
        self.future_time =timezone.now() + timedelta(days=1)
        self.fitness_class = FitnessClass.objects.create(
            name="Test Yoga Class",
            class_type="yoga",
            instructor_name="Test Instructor",
            scheduled_datetime=self.future_time,
            total_slots=10,
            available_slots=5
        )
    def test_class_creation(self):
        """Test if fitness class is created properly"""
        self.assertEqual(self.fitness_class.name, "Test Yoga Class")
        self.assertEqual(self.fitness_class.total_slots, 10)
        self.assertTrue(self.fitness_class.is_upcoming)
    
    def test_timezone_conversion(self):
        """Test timezone conversion functionality"""
        utc_time = self.fitness_class.get_datetime_in_timezone('UTC')
        self.assertIsNotNone(utc_time)

class BookingAPITest(APITestCase):
    def setUp(self):
        self.future_time = timezone.now() + timedelta(days=1)
        self.fitness_class = FitnessClass.objects.create(
            name="Test HIIT Class",
            class_type="hiit",
            instructor_name="Test Instructor",
            scheduled_datetime=self.future_time,
            total_slots=5,
            available_slots=5
        )
    
    def test_get_classes(self):
        """Test GET /api/classes/ endpoint"""
        url = reverse('get_classes')
        response = self.client.get(url)
        
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
    
    def test_create_booking(self):
        """Test POST /api/book/ endpoint"""
        url = reverse('create_booking')
        
        data = {
            'class_id': self.fitness_class.id,
            'client_name': 'Test User',
            'client_email': 'test@example.com'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.assertTrue(response.data['success'])
        
        # Check if booking was created
        self.assertTrue(
            Booking.objects.filter(client_email='test@example.com').exists()
        )
        
        # Check if available slots decreased
        self.fitness_class.refresh_from_db()
        self.assertEqual(self.fitness_class.available_slots, 4)
    
    def test_duplicate_booking_prevention(self):
        """Test that duplicate bookings are prevented"""
        # Create first booking
        Booking.objects.create(
            fitness_class=self.fitness_class,
            client_name='Test User',
            client_email='test@example.com'
        )
        
        # Try to create duplicate booking
        url = reverse('create_booking')
        data = {
            'class_id': self.fitness_class.id,
            'client_name': 'Test User',
            'client_email': 'test@example.com'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_user_bookings(self):
        """Test GET /api/bookings/ endpoint"""
        # Create a booking first
        booking = Booking.objects.create(
            fitness_class=self.fitness_class,
            client_name='Test User',
            client_email='test@example.com'
        )
        
        url = reverse('get_user_bookings')
        response = self.client.get(url, {'email': 'test@example.com'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
