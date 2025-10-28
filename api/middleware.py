"""
Custom middleware to exempt API endpoints from CSRF verification
"""
from django.utils.deprecation import MiddlewareMixin


class DisableCSRFForAPI(MiddlewareMixin):
    """
    Middleware to disable CSRF for API endpoints
    APIs use token authentication instead of CSRF tokens
    """
    
    def process_request(self, request):
        """
        Process the request and exempt API routes from CSRF
        """
        # Check if the request is to an API endpoint
        if request.path.startswith('/api/'):
            # Disable CSRF for API requests
            setattr(request, '_dont_enforce_csrf_checks', True)
        
        return None

