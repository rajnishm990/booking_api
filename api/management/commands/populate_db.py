from django.core.management.base import BaseCommand 
from django.utils import timezone 
from datetime import timedelta
from api.models import FitnessClass, Booking
import random

class Command(BaseCommand):
    help = "populate Database with sample data of fitness classes and bookng"

    def add_arguments(self, parser):
        parser.add_argument('--classes', type=int , default=20 , help='Number of fitness classes to add')
    
        parser.add_argument('--bookings', type=int , default=15 , help='Number of sample bookings to create')
    
    def handle(self, *args, **options):
        self.stdout.write('Starting DB population')

        #clear existing data 
        FitnessClass.objects.all().delete()
        Booking.objects.all().delete()
        # Create fitness classes
        self.create_fitness_classes(options['classes'])
        
        # Create sample bookings
        self.create_sample_bookings(options['bookings'])
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {options['classes']} classes and {options['bookings']} bookings"
            )
        )
        
    def create_fitness_classes(self, count):
        """Create sample fitness classes"""
        
        class_names = {
            'yoga': ['Morning Yoga Flow', 'Sunset Yoga', 'Power Yoga', 'Beginner Yoga'],
            'zumba': ['High Energy Zumba', 'Latin Zumba Party', 'Zumba Fitness'],
            'hiit': ['HIIT Bootcamp', 'Cardio HIIT', 'Strength HIIT'],
            'pilates': ['Core Pilates', 'Reformer Pilates'],
            'cardio': ['Cardio Blast', 'Dance Cardio']
        }
        
        instructors = [
            'Sarah Johnson', 'Mike Chen', 'Priya Sharma', 'David Wilson',
            'Lisa Kumar', 'Alex Rodriguez', 'Maya Patel', 'John Smith'
        ]
        
        for i in range(count):
            class_type = random.choice(list(class_names.keys()))
            name = random.choice(class_names[class_type])
            
            # Create classes for next 30 days
            days_ahead = random.randint(1, 30)
            hour = random.choice([6, 7, 8, 9, 17, 18, 19, 20])  # Morning or evening
            
            scheduled_time = timezone.now() + timedelta(
                days=days_ahead,
                hours=hour - timezone.now().hour,
                minutes=random.choice([0, 30]) - timezone.now().minute,
                seconds=-timezone.now().second,
                microseconds=-timezone.now().microsecond
            )
            
            total_slots = random.randint(8, 25)
            
            FitnessClass.objects.create(
                name=f"{name} #{i+1}" if name in [c.name for c in FitnessClass.objects.all()] else name,
                class_type=class_type,
                instructor_name=random.choice(instructors),
                scheduled_datetime=scheduled_time,
                duration_minutes=random.choice([45, 60, 90]),
                total_slots=total_slots,
                available_slots=random.randint(0, total_slots),
                is_active=True
            )
    
    def create_sample_bookings(self, count):
        """Create sample bookings"""
        
        sample_clients = [
            ('John Doe', 'john.doe@email.com'),
            ('Jane Smith', 'jane.smith@email.com'),
            ('Bob Johnson', 'bob.johnson@email.com'),
            ('Alice Brown', 'alice.brown@email.com'),
            ('Charlie Wilson', 'charlie.wilson@email.com'),
            ('Diana Davis', 'diana.davis@email.com'),
            ('Eva Martinez', 'eva.martinez@email.com'),
            ('Frank Miller', 'frank.miller@email.com'),
        ]
        
        classes_with_slots = FitnessClass.objects.filter(available_slots__gt=0)
        
        for i in range(min(count, len(classes_with_slots))):
            fitness_class = random.choice(classes_with_slots)
            client_name, client_email = random.choice(sample_clients)
            
            # Make sure we don't create duplicate bookings
            if not Booking.objects.filter(
                fitness_class=fitness_class,
                client_email=client_email
            ).exists():
                Booking.objects.create(
                    fitness_class=fitness_class,
                    client_name=client_name,
                    client_email=client_email
                )
                
                # Update available slots
                fitness_class.available_slots -= 1
                fitness_class.save()
