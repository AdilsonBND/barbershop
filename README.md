# Barbershop Appointment System

## Overview

This project is a complete online appointment system for a barbershop developed as a final project for the CS50W course. The system allows clients to book appointments with barbers, barbers to manage their appointments, and administrators to control the entire system. It was developed using Django in the backend, Vue.js in the frontend, and PostgreSQL as the database, all running in Docker containers.

Key highlights of the current version:
- Frontend admin tools to manage barbers and services (no longer only via Django Admin)
- Approval workflow for barbers (admins must approve a barber profile before it’s publicly listed and bookable)
- Barbers can mark appointments as Completed
- Barber working hours are optional per day

## Distinctiveness and Complexity

### Why is this project distinct from other course projects?

This project differs from other course projects (Commerce, Wiki, Network, Mail) in several fundamental ways:

**1. Specific Business Model**: Unlike the Commerce project which is a generic e-commerce, this system is specifically designed for the services sector, with a focus on real-time service appointment booking. This is not a buy-and-sell marketplace, but rather a personal service time and service reservation system.

**2. Data Relationship Complexity**: The system manages multiple types of users (clients, barbers, administrators) with different levels of access and interaction. Each user type sees a completely different interface and functionality, something not present in previous projects.

**3. Availability Management**: The system implements complex availability verification logic, considering not only existing appointments but also each barber's working hours, days of the week, and time constraints. This logic is not found in any other course project.

**4. Multiple Interface System**: While previous projects generally had a standard interface, this system implements three distinct interfaces:
   - Client interface (book, view history)
   - Barber interface (manage appointments, confirm)
   - Administrative interface (customized Django admin and admin tools in the SPA)

**5. Unique Use Cases**: The system implements specific workflows for the personal services industry, such as:
   - Real-time availability verification
   - Appointment status (scheduled, confirmed, in progress, completed, cancelled)
   - No-show control
   - Management of barber availability by day of the week

### Why is this project complex?

**1. Complete Full-Stack Architecture**: The project implements complete separation between backend (Django REST Framework) and frontend (Vue.js), with communication via REST API. This architecture is more complex than Django template-based implementations seen in previous projects.

**2. Multi-Level Authentication and Authorization System**: Implements three distinct permission levels:
   - Clients: can create and view their own appointments
   - Barbers: can view their appointments, confirm, cancel and see availability
   - Administrators: full access to the system via Django admin

**3. Inter-Related Data Models**: The system has four main models:
   - CustomUser: custom user with types (client, barber, admin)
   - BarberProfile: extended profile with working hours for each day of the week
   - Service: services offered by the barbershop
   - Appointment: appointments with multiple states and complex relationships

**4. Complete REST API**: Implements complete Django REST Framework ViewSets with:
   - Dynamic filters based on user type
   - Custom serializers for different operations
   - Custom actions for cancellation, appointment confirmation
   - Dashboard endpoints with statistics specific to user type

**5. Modern SPA Frontend**: Vue.js 3 with:
   - Complete routing system
   - State management with Pinia
   - Reusable components
   - API consumption with axios
   - Responsive design for mobile

**6. Complete Containerization**: Docker Compose with:
   - PostgreSQL database service
   - Django backend
   - Vue.js frontend with hot-reload
   - Volumes for data persistence
   - Network configuration

**7. Complex Business Logic**: Implements:
   - Time slot availability verification
   - Schedule conflict validation
   - Dynamic available slot generation
   - Permission-based data filtering
   - Statistics customized by user type

**8. Security and Validation**: 
   - Token-based authentication
   - Password validation
   - CORS configuration
   - Custom permissions per action
   - Complex model validation

## Project Structure

### Main Files

```
barbershop/
├── barbershop/          # Django main settings
│   ├── settings.py      # Project settings
│   ├── urls.py          # Main URLs
│   ├── wsgi.py          # WSGI config
│   └── asgi.py          # ASGI config
├── users/               # User app
│   ├── models.py        # CustomUser, BarberProfile, Service, Appointment
│   ├── admin.py         # Django Admin configuration
│   └── migrations/      # Database migrations
├── api/                 # REST API
│   ├── views.py         # API ViewSets and views
│   ├── serializers.py   # DRF serializers
│   └── urls.py          # API URLs
├── frontend/            # Vue.js frontend
│   ├── src/
│   │   ├── views/       # Page components
│   │   ├── stores/      # Pinia stores
│   │   ├── router/      # Vue Router
│   │   ├── services/    # API service
│   │   └── App.vue      # Main component
│   ├── package.json
│   └── vite.config.js
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Docker configuration
├── Dockerfile.backend   # Backend Dockerfile
├── Dockerfile.frontend  # Frontend Dockerfile
└── manage.py           # Django management
```

### Backend (Django)

**Models** (`users/models.py`):
- `CustomUser`: Custom user extending AbstractUser with types (client, barber, admin)
- `BarberProfile`: Barber profile with working hours for each day of the week
- `Service`: Services offered (haircut, beard trim, etc.)
- `Appointment`: Appointments with multiple states

**API** (`api/views.py` and `api/serializers.py`):
- `UserViewSet`: CRUD for users with filters by type
- `BarberProfileViewSet`: Barber profile management with availability endpoint and admin-only approve action
- `ServiceViewSet`: Service listing and management
- `AppointmentViewSet`: CRUD for appointments with cancellation, confirmation, and completion actions
- Authentication endpoints: register, login, logout
- Dashboard stats: statistics specific to user type

### Frontend (Vue.js)

**Views** (`frontend/src/views/`):
- `Login.vue`: Login page
- `Register.vue`: Registration page
- `Dashboard.vue`: Dashboard with statistics by user type
- `Appointments.vue`: Appointment list with actions
- `NewAppointment.vue`: Form to create new appointment
- `Barbers.vue`: List of available barbers
- `Services.vue`: List of offered services
- `BarberProfile.vue`: Barber self-profile management (working hours, availability)
- `AdminBarbers.vue`: Admin management of barbers (create/edit/delete/approve)
- `AdminServices.vue`: Admin management of services (create/edit/delete)

**Store** (`frontend/src/stores/user.js`):
- Authentication state management
- Login, logout, registration
- Profile update

## How to Run

### Prerequisites
- Docker and Docker Compose installed

### Installation and Execution

1. **Clone the repository** (if applicable)

2. **Run with Docker Compose**:
```bash
docker-compose up
```

This will start:
- PostgreSQL on port 5432
- Django backend on port 8000
- Vue.js frontend on port 8080

3. **Access the application**:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- Django Admin: http://localhost:8000/admin

### Create Superuser

To access Django admin, create a superuser:

```bash
docker-compose exec backend python manage.py createsuperuser
```

**Important**: After creating the superuser, you must assign administrator access in Django admin:

1. Access http://localhost:8000/admin
2. Login with the superuser credentials
3. Go to "Custom users" in the admin panel
4. Find your superuser account
5. Edit the user and set "User type" to "Administrator"
6. Save the changes

This step is required to give the superuser full administrative privileges in the application.

### Test Users

You can create users through the registration interface or Django admin:

**Client**:
- Username: client1
- Password: (any)
- Type: client

**Barber**:
- Username: barber1
- Password: (any)  
- Type: barber
- After creating, add working hours in the barber's profile

**Administrator**:
- Use Django admin with the created superuser

## Main Features

### For Clients:
- Registration and login
- View dashboard with statistics
- See available barbers
- See offered services
- Create new appointments
- View appointment history
- Cancel appointments

### For Barbers:
- Registration and login
- View dashboard with today's appointments
- See all assigned appointments
- Confirm appointments
- Mark appointments as Completed
- Cancel appointments
- Manage working hours via `BarberProfile` page (optional per day)
- See approval notice until an admin approves the profile

### For Administrators:
- Full access to Django admin
- Manage all users
- Manage services (also via SPA)
- Manage barbers (also via SPA: create/edit/delete/approve)
- Approve barber profiles (required before public listing/booking)
- View all appointments
- General system statistics

## Technologies Used

- **Backend**: Django 4.2, Django REST Framework
- **Frontend**: Vue.js 3, Vue Router, Pinia, Axios
- **Database**: PostgreSQL
- **Containerization**: Docker, Docker Compose
- **Build Tool**: Vite

## Additional Information

### Permissions and Security
- Token-based authentication system
- Custom permissions per user type
- Data validation on all endpoints
- CORS configured for development
- Public endpoints only return approved barbers; bookings are blocked for unapproved barbers

### Development
- Hot-reload enabled in frontend
- Docker volumes for development
- Automatic migrations on startup
- Persistent static and media files

### Future Extensions
- Notification system
- Payment integration
- Reviews and comments
- Visual calendar for barbers
- Google Calendar integration
- Email reminder system

## API Summary (selected endpoints)

Authentication
```
POST /api/register/
POST /api/login/
POST /api/logout/
```

Users
```
GET /api/users/
GET /api/users/me/
PATCH /api/users/me/
```

Barbers
```
GET /api/barbers/                 # Public: only approved barbers
GET /api/barbers/{id}/
GET /api/barbers/{id}/availability/?date=YYYY-MM-DD
GET /api/barbers/my_profile/      # Barber’s own profile
POST /api/barbers/{id}/approve/   # Admin only
```

Services
```
GET /api/services/
GET /api/services/{id}/
```

Appointments
```
GET  /api/appointments/
POST /api/appointments/
POST /api/appointments/{id}/confirm/
POST /api/appointments/{id}/cancel/
POST /api/appointments/{id}/complete/
```
