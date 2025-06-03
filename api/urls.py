from django.urls import path
from . import views

urlpatterns = [
    path('classes/', views.get_classes, name='get_classes'),
    path('book/', views.create_booking, name='create_booking'),
    path('bookings/', views.get_user_bookings, name='get_user_bookings'),
]