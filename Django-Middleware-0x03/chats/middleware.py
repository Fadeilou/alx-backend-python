import logging
from datetime import datetime, timedelta
from django.http import HttpResponseForbidden


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Configure logging
        logging.basicConfig(
            filename='requests.log',
            level=logging.INFO,
            format='%(message)s',
        )

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logging.info(log_message)
        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the current server time
        current_hour = datetime.now().hour

        # Define restricted hours (outise 9AM - 6AM)
        if current_hour < 9 or current_hour > 18:
            return HttpResponseForbidden("Access to the chat is restricted outside of 9AM to 6PM.")

        # Proceed with the request if within allowed hours
        return self.get_response(request)


class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Dictionary to track requests from IP addresses
        self.request_logs = {}

    def __call__(self, request):
        # Only apply the middleware to POST requests to the chat endpoint
        if request.method == "POST" and request.path.startswith("/chat/"):
            ip = self.get_client_ip(request)
            current_time = datetime.now()

            # Initialize or update the log for this IP address
            if ip not in self.request_logs:
                self.request_logs[ip] = []

            # Remove requests older than 1 minute from the log
            self.request_logs[ip] = [
                timestamp for timestamp in self.request_logs[ip]
                if timestamp > current_time - timedelta(minutes=1)
            ]

            # Check if the limit of 5 messages per minute is exceeded
            if len(self.request_logs[ip]) >= 5:
                return HttpResponseForbidden("Message limit exceeded. Try again later.")

            # Log the current request
            self.request_logs[ip].append(current_time)

        return self.get_response(request)

    def get_client_ip(self, request):
        """Get the IP address of the client."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR")


class RolePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define restricted paths (e.g., admin-only actions)
        restricted_paths = ["/chat/manage/", "/chat/delete/"]

        # Check if the path requires a role check
        if any(request.path.startswith(path) for path in restricted_paths):
            # Ensure the user is authenticated
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Access denied: Login required.")

            # Check the user's role
            user_role = getattr(request.user, "role", None)  # Assume 'role' is a field on the User model
            if user_role not in ["admin", "moderator"]:
                return HttpResponseForbidden("Access denied: Insufficient permissions.")

        # Proceed with the request if no restrictions apply
        return self.get_response(request)
