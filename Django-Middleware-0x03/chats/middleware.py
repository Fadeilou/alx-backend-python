import logging
import os
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from django.contrib.auth.models import AnonymousUser
from collections import defaultdict
import time
from django.conf import settings

# Configure logging for request logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler('requests.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware that logs each user's requests to a file, including timestamp, user, and request path.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Get user information
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user.username if hasattr(request.user, 'username') else str(request.user)
        else:
            user = "Anonymous"
        
        # Log the request
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)
        
        # Process the request
        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware(MiddlewareMixin):
    """
    Middleware that restricts access to the messaging app during certain hours (outside 6AM-9PM).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        # Get current hour (24-hour format)
        current_hour = datetime.now().hour
        
        # Check if current time is outside allowed hours (6AM to 9PM)
        # Allowed hours: 6 (6AM) to 21 (9PM)
        if current_hour < 6 or current_hour >= 21:
            return HttpResponse(
                "Access denied. Chat is only available between 6AM and 9PM.",
                status=403,
                content_type="text/plain"
            )
        
        # Process the request if within allowed hours
        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware(MiddlewareMixin):
    """
    Middleware that limits the number of chat messages a user can send within a certain time window
    based on their IP address (5 messages per minute).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Dictionary to store IP address request counts and timestamps
        self.ip_requests = defaultdict(list)
        self.max_requests = 5  # Maximum requests per minute
        self.time_window = 60  # Time window in seconds (1 minute)
        super().__init__(get_response)
    
    def __call__(self, request):
        # Only apply rate limiting to POST requests (messages)
        if request.method == 'POST':
            # Get client IP address
            ip_address = self.get_client_ip(request)
            current_time = time.time()
            
            # Clean old requests outside the time window
            self.ip_requests[ip_address] = [
                req_time for req_time in self.ip_requests[ip_address]
                if current_time - req_time < self.time_window
            ]
            
            # Check if user has exceeded the limit
            if len(self.ip_requests[ip_address]) >= self.max_requests:
                return HttpResponse(
                    "Rate limit exceeded. You can only send 5 messages per minute.",
                    status=429,  # Too Many Requests
                    content_type="text/plain"
                )
            
            # Add current request timestamp
            self.ip_requests[ip_address].append(current_time)
        
        # Process the request
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RolepermissionMiddleware(MiddlewareMixin):
    """
    Middleware that checks the user's role before allowing access to specific actions.
    Only admin and moderator users are allowed access.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Define paths that require admin/moderator access
        self.protected_paths = [
            '/api/conversations/',
            '/api/messages/',
            '/api/users/',
        ]
        super().__init__(get_response)
    
    def __call__(self, request):
        # Check if the request path requires role-based access
        if any(request.path.startswith(path) for path in self.protected_paths):
            # Check if user is authenticated
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                return HttpResponse(
                    "Authentication required.",
                    status=401,
                    content_type="text/plain"
                )
            
            # Check user role
            user = request.user
            
            # Check if user is admin (superuser) or has moderator role
            if not (user.is_superuser or self.is_moderator(user)):
                return HttpResponse(
                    "Access denied. Admin or moderator role required.",
                    status=403,
                    content_type="text/plain"
                )
        
        # Process the request
        response = self.get_response(request)
        return response
    
    def is_moderator(self, user):
        """Check if user has moderator role."""
        # Check if user has a 'role' attribute or is in a moderator group
        if hasattr(user, 'role'):
            return user.role in ['admin', 'moderator']
        
        # Check if user is in a moderator group
        if user.groups.filter(name__in=['admin', 'moderator']).exists():
            return True
        
        # Check if user has specific permissions
        if user.has_perm('chats.moderate_conversations') or user.has_perm('chats.moderate_messages'):
            return True
        
        return False
