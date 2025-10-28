from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, BarberProfileViewSet, ServiceViewSet, 
    AppointmentViewSet, register_view, login_view, logout, dashboard_stats
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'barbers', BarberProfileViewSet, basename='barber-profile')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'appointments', AppointmentViewSet, basename='appointment')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout, name='logout'),
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),
]

