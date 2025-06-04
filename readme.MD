# Fitness Studio Booking API

A Django REST API for managing fitness class bookings at a fictional fitness studio.

## Features

- **Class Management**: View upcoming fitness classes (Yoga, Zumba, HIIT, etc.)
- **Booking System**: Book classes with automatic slot management
- **User Bookings**: View all bookings by email address
- **Timezone Support**: Automatic timezone conversion for class schedules
- **Validation**: Comprehensive input validation and error handling
- **Race Condition Protection**: Database transactions prevent overbooking

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fitness_studio
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup database**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create sample data**
   ```bash
   python manage.py populate_db --classes 20 --bookings 15
   ```

6. **Run the server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### 1. GET /api/classes/
Returns all upcoming fitness classes with available slots.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Morning Yoga Flow",
      "class_type": "yoga",
      "instructor_name": "Sarah Johnson",
      "scheduled_datetime": "2025-06-04T07:00:00+05:30",
      "scheduled_datetime_local": "2025-06-04T07:00:00+05:30",
      "duration_minutes": 60,
      "total_slots": 15,
      "available_slots": 12
    }
  ],
  "count": 1
}
```

### 2. POST /api/book/
Creates a new booking for a fitness class.

**Request:**
```json
{
  "class_id": 1,
  "client_name": "John Doe",
  "client_email": "john.doe@email.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Booking created successfully!",
  "data": {
    "booking_reference": "ABC12345",
    "class_name": "Morning Yoga Flow",
    "class_datetime": "2025-06-04T07:00:00+05:30",
    "instructor": "Sarah Johnson",
    "client_name": "John Doe",
    "booking_datetime": "2025-06-03T10:30:00+05:30"
  }
}
```

### 3. GET /api/bookings/?email=user@example.com
Returns all bookings for a specific email address.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "booking_reference": "ABC12345",
      "class_name": "Morning Yoga Flow",
      "class_datetime": "2025-06-04T07:00:00+05:30",
      "instructor": "Sarah Johnson",
      "client_name": "John Doe",
      "booking_datetime": "2025-06-03T10:30:00+05:30"
    }
  ],
  "count": 1
}
```

## Sample cURL Commands

### Get all classes
```bash
curl -X GET "http://localhost:8000/api/classes/" \
  -H "Content-Type: application/json"
```

### Create a booking
```bash
curl -X POST "http://localhost:8000/api/book/" \
  -H "Content-Type: application/json" \
  -d '{
    "class_id": 1,
    "client_name": "John Doe",
    "client_email": "john.doe@email.com"
  }'
```

### Get user bookings
```bash
curl -X GET "http://localhost:8000/api/bookings/?email=john.doe@email.com" \
  -H "Content-Type: application/json"
```

### Populate Database with Sample Data
```bash
# Create 20 classes and 15 bookings
python manage.py populate_db --classes 20 --bookings 15

# Create custom amount
python manage.py populate_db --classes 50 --bookings 30
```

### Other Useful Commands
```bash
# Create superuser for admin access
python manage.py createsuperuser

# Run tests
python manage.py test

# Check for any issues
python manage.py check

# View database shell
python manage.py shell
```

## Performance Considerations

### Database Optimization
- **Select Related**: Optimized queries with proper joins
- **Database Indexes**: Strategic indexes on frequently queried fields
- **Atomic Transactions**: Race condition prevention
- **Query Optimization**: Minimal database queries per request

### Scalability Features
- **Pagination**: Built-in pagination for large datasets
- **Efficient Serialization**: Optimized data serialization
- **Proper Error Handling**: Graceful degradation under load
- **Logging**: Comprehensive logging for monitoring


