from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, BarberProfile, Service, Appointment


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'user_type', 'phone', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_active', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('user_type', 'phone', 'birth_date')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': ('user_type', 'phone', 'birth_date', 'email', 'first_name', 'last_name')
        }),
    )


@admin.register(BarberProfile)
class BarberProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'is_available', 'created_at']
    list_filter = ['is_available', 'specialization']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'duration', 'price', 'is_active', 'created_at']
    list_filter = ['is_active']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['client', 'barber', 'service', 'appointment_date', 'appointment_time', 'status']
    list_filter = ['status', 'appointment_date', 'service']
    search_fields = ['client__username', 'barber__username']

