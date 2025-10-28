from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from users.models import CustomUser, BarberProfile, Service, Appointment


class UserSerializer(serializers.ModelSerializer):
    """Serializer for custom user model"""
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'user_type', 'phone', 'birth_date', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 
                  'first_name', 'last_name', 'user_type', 'phone', 'birth_date']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError(
                    "Invalid credentials."
                )
            if not user.is_active:
                raise serializers.ValidationError(
                    "Account is disabled."
                )
        else:
            raise serializers.ValidationError(
                "Must include 'username' and 'password'."
            )
        
        attrs['user'] = user
        return attrs


class BarberProfileSerializer(serializers.ModelSerializer):
    """Serializer for barber profile"""
    user = UserSerializer(read_only=True)
    # Barbers cannot set approval themselves
    is_approved = serializers.BooleanField(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(user_type='barber'),
        source='user',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = BarberProfile
        fields = '__all__'
        extra_kwargs = {
            'monday_start': {'allow_null': True, 'required': False},
            'monday_end': {'allow_null': True, 'required': False},
            'tuesday_start': {'allow_null': True, 'required': False},
            'tuesday_end': {'allow_null': True, 'required': False},
            'wednesday_start': {'allow_null': True, 'required': False},
            'wednesday_end': {'allow_null': True, 'required': False},
            'thursday_start': {'allow_null': True, 'required': False},
            'thursday_end': {'allow_null': True, 'required': False},
            'friday_start': {'allow_null': True, 'required': False},
            'friday_end': {'allow_null': True, 'required': False},
            'saturday_start': {'allow_null': True, 'required': False},
            'saturday_end': {'allow_null': True, 'required': False},
            'sunday_start': {'allow_null': True, 'required': False},
            'sunday_end': {'allow_null': True, 'required': False},
        }
    
    def create(self, validated_data):
        # If user_id is provided, use it; otherwise use the authenticated user
        if 'user' not in validated_data:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate(self, attrs):
        """Validate time fields - if start time is provided, end time must be provided too"""
        time_fields = [
            ('monday_start', 'monday_end'),
            ('tuesday_start', 'tuesday_end'),
            ('wednesday_start', 'wednesday_end'),
            ('thursday_start', 'thursday_end'),
            ('friday_start', 'friday_end'),
            ('saturday_start', 'saturday_end'),
            ('sunday_start', 'sunday_end'),
        ]
        
        for start_field, end_field in time_fields:
            start_time = attrs.get(start_field)
            end_time = attrs.get(end_field)
            
            # If start time is provided, end time must also be provided
            if start_time and not end_time:
                raise serializers.ValidationError({
                    end_field: f"If {start_field} is provided, {end_field} must also be provided."
                })
            
            # If end time is provided, start time must also be provided
            if end_time and not start_time:
                raise serializers.ValidationError({
                    start_field: f"If {end_field} is provided, {start_field} must also be provided."
                })
            
            # If both times are provided, start time must be before end time
            if start_time and end_time and start_time >= end_time:
                raise serializers.ValidationError({
                    end_field: f"{end_field} must be after {start_field}."
                })
        
        return attrs


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for services"""
    
    class Meta:
        model = Service
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for appointments"""
    client = UserSerializer(read_only=True)
    barber = UserSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)
    
    client_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(user_type='client'),
        source='client',
        write_only=True,
        required=False
    )
    barber_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(user_type='barber'),
        source='barber',
        write_only=True,
        required=False
    )
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        source='service',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Appointment
        fields = ['id', 'client', 'barber', 'service', 'appointment_date',
                  'appointment_time', 'status', 'notes', 'created_at', 
                  'updated_at', 'client_id', 'barber_id', 'service_id']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appointments"""
    barber_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(user_type='barber'),
        source='barber',
        write_only=True
    )
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        source='service',
        write_only=True
    )
    
    class Meta:
        model = Appointment
        fields = ['barber_id', 'service_id', 'appointment_date', 
                  'appointment_time', 'notes']
    
    def validate_appointment_date(self, value):
        """Validate that the appointment date is not in the past"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if value < today:
            raise serializers.ValidationError("Cannot book appointments for past dates.")
        
        return value
    
    def validate(self, attrs):
        """Custom validations"""
        # Check if user is trying to book themselves
        client = self.context['request'].user
        barber = attrs.get('barber')
        
        # If the barber is the same as the logged-in user and is a barber
        if barber == client and client.user_type == 'barber':
            raise serializers.ValidationError({
                'barber_id': "You cannot book an appointment with yourself as a barber."
            })
        
        # Ensure the selected barber is approved
        try:
            profile = getattr(barber, 'barber_profile', None)
            if not profile or not profile.is_approved:
                raise serializers.ValidationError({
                    'barber_id': "Selected barber is not authorized yet. Please choose another barber."
                })
        except Exception:
            raise serializers.ValidationError({
                'barber_id': "Selected barber is not authorized yet. Please choose another barber."
            })
        
        return attrs
    
    def create(self, validated_data):
        client = self.context['request'].user
        validated_data['client'] = client
        return super().create(validated_data)

