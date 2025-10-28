from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    to support different user types: clients, barbers, and admins
    """
    
    USER_TYPES = [
        ('client', 'Client'),
        ('barber', 'Barber'),
        ('admin', 'Administrator'),
    ]
    
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPES,
        default='client'
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be in the format: '+999999999'. Up to 15 digits."
    )
    
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True
    )
    
    birth_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
    
    def is_client(self):
        return self.user_type == 'client'
    
    def is_barber(self):
        return self.user_type == 'barber'
    
    def is_admin(self):
        return self.user_type == 'admin' or self.is_staff


class BarberProfile(models.Model):
    """
    Extended profile for barber users with availability and specialties
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='barber_profile',
        limit_choices_to={'user_type': 'barber'}
    )
    
    bio = models.TextField(blank=True)
    specialization = models.CharField(max_length=200, blank=True)
    
    # Operating hours (24-hour format)
    monday_start = models.TimeField(null=True, blank=True)
    monday_end = models.TimeField(null=True, blank=True)
    
    tuesday_start = models.TimeField(null=True, blank=True)
    tuesday_end = models.TimeField(null=True, blank=True)
    
    wednesday_start = models.TimeField(null=True, blank=True)
    wednesday_end = models.TimeField(null=True, blank=True)
    
    thursday_start = models.TimeField(null=True, blank=True)
    thursday_end = models.TimeField(null=True, blank=True)
    
    friday_start = models.TimeField(null=True, blank=True)
    friday_end = models.TimeField(null=True, blank=True)
    
    saturday_start = models.TimeField(null=True, blank=True)
    saturday_end = models.TimeField(null=True, blank=True)
    
    sunday_start = models.TimeField(null=True, blank=True)
    sunday_end = models.TimeField(null=True, blank=True)
    
    is_available = models.BooleanField(default=True)
    # Requires administrator approval before being publicly listed/used for booking
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"


class Service(models.Model):
    """
    Services offered by the barbershop (haircut, beard, etc.)
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class Appointment(models.Model):
    """
    Appointment booking system for barbershop
    """
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    client = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='client_appointments',
        limit_choices_to={'user_type': 'client'}
    )
    
    barber = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='barber_appointments',
        limit_choices_to={'user_type': 'barber'}
    )
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )
    
    notes = models.TextField(blank=True, help_text="Additional notes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
    
    def __str__(self):
        return f"{self.client.username} - {self.barber.username} - {self.appointment_date} {self.appointment_time}"

