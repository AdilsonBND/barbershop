from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

from users.models import CustomUser, BarberProfile, Service, Appointment
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    BarberProfileSerializer, ServiceSerializer, 
    AppointmentSerializer, AppointmentCreateSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for managing users"""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            # Allow anyone to register
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return CustomUser.objects.none()
            
        user = self.request.user
        if user.user_type == 'admin':
            return CustomUser.objects.all()
        elif user.user_type == 'barber':
            # Barbers can view clients who have appointments with them
            return CustomUser.objects.filter(
                id__in=Appointment.objects.filter(
                    barber=user
                ).values_list('client_id', flat=True)
            )
        else:
            # Clients can only view themselves
            return CustomUser.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user information"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """Update current user information"""
        serializer = self.get_serializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class BarberProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for barber profiles"""
    queryset = BarberProfile.objects.all()
    serializer_class = BarberProfileSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.user_type == 'admin':
            return BarberProfile.objects.all()
        elif user.is_authenticated and user.user_type == 'barber':
            # Barbers can only see their own profile
            return BarberProfile.objects.filter(user=user)
        else:
            # Public can see only approved barber profiles
            return BarberProfile.objects.filter(is_approved=True)
    
    def perform_create(self, serializer):
        # If user is a barber, automatically assign their profile
        if self.request.user.user_type == 'barber':
            serializer.save(user=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def approve(self, request, pk=None):
        """Approve a barber profile (admin only)"""
        profile = self.get_object()
        profile.is_approved = True
        profile.save(update_fields=['is_approved'])
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """Get current barber's profile"""
        if request.user.user_type != 'barber':
            return Response(
                {"error": "Only barbers can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            profile = BarberProfile.objects.get(user=request.user)
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except BarberProfile.DoesNotExist:
            return Response(
                {"error": "Profile not found", "has_profile": False},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Get barber availability for a specific date"""
        barber_profile = self.get_object()
        date_str = request.query_params.get('date')
        
        if not date_str:
            return Response(
                {"error": "Parameter 'date' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get barber's operating hours for the day
        weekday = appointment_date.weekday()
        time_fields = {
            0: ('monday_start', 'monday_end'),
            1: ('tuesday_start', 'tuesday_end'),
            2: ('wednesday_start', 'wednesday_end'),
            3: ('thursday_start', 'thursday_end'),
            4: ('friday_start', 'friday_end'),
            5: ('saturday_start', 'saturday_end'),
            6: ('sunday_start', 'sunday_end'),
        }
        
        start_field, end_field = time_fields[weekday]
        start_time = getattr(barber_profile, start_field)
        end_time = getattr(barber_profile, end_field)
        
        if not start_time or not end_time:
            return Response(
                {"available": False, "reason": "Barber doesn't work on this day"}
            )
        
        # Get existing appointments for the day
        appointments = Appointment.objects.filter(
            barber=barber_profile.user,
            appointment_date=appointment_date,
            status__in=['scheduled', 'confirmed', 'in_progress']
        )
        
        # Generate available time slots
        available_slots = []
        current_time = start_time
        service_duration = 30  # Default 30 minutes slots
        
        while current_time < end_time:
            slot_end = (datetime.combine(appointment_date, current_time) + 
                       timedelta(minutes=service_duration)).time()
            
            # Check if slot is available
            is_available = not appointments.filter(
                appointment_time__lt=slot_end,
                appointment_time__gte=current_time
            ).exists()
            
            available_slots.append({
                'time': current_time.strftime('%H:%M'),
                'available': is_available
            })
            
            # Move to next slot
            current_time = slot_end
        
        return Response({
            'date': date_str,
            'barber': barber_profile.user.username,
            'available_slots': available_slots
        })


class ServiceViewSet(viewsets.ModelViewSet):
    """ViewSet for services"""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.user_type == 'admin':
            return Service.objects.all()
        else:
            # Public can only see active services
            return Service.objects.filter(is_active=True)


class AppointmentViewSet(viewsets.ModelViewSet):
    """ViewSet for appointments"""
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    
    def get_permissions(self):
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return Appointment.objects.all()
        elif user.user_type == 'barber':
            return Appointment.objects.filter(barber=user)
        else:
            return Appointment.objects.filter(client=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AppointmentCreateSerializer
        return AppointmentSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        # Return full appointment data using AppointmentSerializer
        appointment = Appointment.objects.get(id=serializer.instance.id)
        appointment_serializer = AppointmentSerializer(appointment)
        return Response(appointment_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an appointment"""
        appointment = self.get_object()
        
        if appointment.status in ['cancelled', 'completed']:
            return Response(
                {"error": "Appointment cannot be cancelled"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = 'cancelled'
        appointment.save()
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm an appointment (barbers only)"""
        if request.user.user_type != 'barber':
            return Response(
                {"error": "Only barbers can confirm appointments"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        appointment = self.get_object()
        
        if appointment.barber != request.user:
            return Response(
                {"error": "You can only confirm your own appointments"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        appointment.status = 'confirmed'
        appointment.save()
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark an appointment as completed (barbers only)"""
        if request.user.user_type != 'barber':
            return Response(
                {"error": "Only barbers can complete appointments"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        appointment = self.get_object()
        
        if appointment.barber != request.user:
            return Response(
                {"error": "You can only complete your own appointments"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if appointment.status in ['cancelled', 'completed']:
            return Response(
                {"error": "Appointment cannot be marked as completed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = 'completed'
        appointment.save()
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """User registration endpoint"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """User login endpoint"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        })
    
    # Tratar erros de forma mais amigável
    errors = serializer.errors
    if 'non_field_errors' in errors:
        # Extrair a mensagem do non_field_errors
        error_message = errors['non_field_errors'][0] if isinstance(errors['non_field_errors'], list) else str(errors['non_field_errors'])
        return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout endpoint"""
    try:
        token = request.user.auth_token
        token.delete()
    except:
        pass
    return Response({"message": "Logout successful"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics based on user type"""
    user = request.user
    
    if user.user_type == 'admin':
        stats = {
            'total_users': CustomUser.objects.count(),
            'total_clients': CustomUser.objects.filter(user_type='client').count(),
            'total_barbers': CustomUser.objects.filter(user_type='barber').count(),
            'total_appointments': Appointment.objects.count(),
            'pending_appointments': Appointment.objects.filter(status='scheduled').count(),
        }
    elif user.user_type == 'barber':
        appointments = Appointment.objects.filter(barber=user)
        stats = {
            'total_appointments': appointments.count(),
            'today_appointments': appointments.filter(
                appointment_date=timezone.now().date()
            ).count(),
            'pending_appointments': appointments.filter(status='scheduled').count(),
            'completed_appointments': appointments.filter(status='completed').count(),
        }
    else:  # client
        appointments = Appointment.objects.filter(client=user)
        stats = {
            'total_appointments': appointments.count(),
            'upcoming_appointments': appointments.filter(
                appointment_date__gte=timezone.now().date(),
                status__in=['scheduled', 'confirmed']
            ).count(),
            'past_appointments': appointments.filter(
                appointment_date__lt=timezone.now().date()
            ).count(),
        }
    
    return Response(stats)

