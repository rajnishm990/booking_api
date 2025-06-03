from django.contrib import admin

from django.contrib import admin
from .models import FitnessClass, Booking

@admin.register(FitnessClass)
class FitnessClassAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'class_type', 'instructor_name', 
        'scheduled_datetime', 'available_slots', 'total_slots', 'is_active'
    ]
    list_filter = ['class_type', 'is_active', 'scheduled_datetime']
    search_fields = ['name', 'instructor_name']
    ordering = ['scheduled_datetime']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'booking_reference', 'client_name', 'client_email', 
        'fitness_class', 'booking_datetime', 'is_cancelled'
    ]
    list_filter = ['is_cancelled', 'booking_datetime']
    search_fields = ['client_name', 'client_email', 'booking_reference']
    readonly_fields = ['booking_reference', 'booking_datetime']