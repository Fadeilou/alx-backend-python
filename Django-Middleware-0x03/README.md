# Django Middleware Implementation

## Project Overview

This project demonstrates the implementation of custom Django middleware components for a messaging application. The middleware components provide logging, access control, rate limiting, and role-based permissions.

## 📁 Project Structure

```
Django-Middleware-0x03/
├── chats/
│   ├── middleware.py          # Custom middleware implementations
│   ├── models.py              # Updated User model with roles
│   └── ...
├── messaging_app/
│   ├── settings.py            # Middleware configuration
│   └── ...
├── requests.log               # Request logging output
├── test_middleware.py         # Testing script
└── README.md                  # This file
```

## 🔧 Implemented Middleware Components

### 1. RequestLoggingMiddleware

**Purpose**: Logs each user's requests with timestamp, user, and request path.

**Features**:
- Logs to both file (`requests.log`) and console
- Handles both authenticated and anonymous users
- Records timestamp, username, and request path

**Log Format**:
```
2024-06-14 10:30:15.123456 - User: john_doe - Path: /api/conversations/
2024-06-14 10:30:20.789012 - User: Anonymous - Path: /api/auth/login/
```

### 2. RestrictAccessByTimeMiddleware

**Purpose**: Restricts access to the messaging app during certain hours (outside 6AM-9PM).

**Features**:
- Checks current server time
- Blocks access outside 6AM to 9PM hours
- Returns 403 Forbidden with descriptive message
- Applies to all requests

**Behavior**:
- **Allowed**: 6:00 AM - 8:59 PM
- **Blocked**: 9:00 PM - 5:59 AM

### 3. OffensiveLanguageMiddleware

**Purpose**: Implements rate limiting based on IP address (5 messages per minute).

**Features**:
- Tracks POST requests per IP address
- Implements sliding window rate limiting
- Limits to 5 requests per 60-second window
- Returns 429 Too Many Requests when limit exceeded
- Only applies to POST requests (message creation)

**Rate Limiting Logic**:
- Maintains a dictionary of IP addresses and request timestamps
- Removes old timestamps outside the 60-second window
- Blocks new requests when limit is reached

### 4. RolePermissionMiddleware

**Purpose**: Enforces role-based access control for protected endpoints.

**Features**:
- Checks user authentication status
- Validates user roles (admin, moderator, user)
- Protects specific API endpoints
- Returns 401 for unauthenticated users
- Returns 403 for users without proper roles

**Protected Endpoints**:
- `/api/conversations/`
- `/api/messages/`
- `/api/users/`

**Allowed Roles**:
- `admin` (superuser or role='admin')
- `moderator` (role='moderator' or in moderator group)

## ⚙️ Configuration

### Middleware Order in settings.py

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'chats.middleware.RequestLoggingMiddleware',           # 1. Log all requests
    'chats.middleware.RestrictAccessByTimeMiddleware',     # 2. Time-based access
    'chats.middleware.OffensiveLanguageMiddleware',        # 3. Rate limiting
    'chats.middleware.RolePermissionMiddleware',           # 4. Role permissions
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

**Order Explanation**:
1. **RequestLoggingMiddleware**: First to log all incoming requests
2. **RestrictAccessByTimeMiddleware**: Early blocking for time restrictions
3. **OffensiveLanguageMiddleware**: Rate limiting before business logic
4. **RolePermissionMiddleware**: Final access control before views

### User Model Updates

Added role field to User model:

```python
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('user', 'User'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    # ... other fields
```

## 🧪 Testing

### Running the Test Script

```bash
# Start the Django server
python manage.py runserver

# In another terminal, run the test script
python test_middleware.py
```

### Manual Testing with curl

```bash
# Test logging (check requests.log after)
curl http://127.0.0.1:8000/api/users/

# Test time restriction (outside 6AM-9PM)
curl http://127.0.0.1:8000/api/conversations/

# Test rate limiting (run multiple times quickly)
curl -X POST http://127.0.0.1:8000/api/messages/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"conversation":"CONV_ID","message_body":"Test"}'

# Test role permissions (without proper role)
curl http://127.0.0.1:8000/api/conversations/ \
  -H "Authorization: Bearer USER_TOKEN"
```

### Expected Responses

1. **RequestLoggingMiddleware**: Check `requests.log` for entries
2. **RestrictAccessByTimeMiddleware**: 403 during off-hours
3. **OffensiveLanguageMiddleware**: 429 after 5 POST requests/minute
4. **RolePermissionMiddleware**: 403 for non-admin/moderator users

## 📝 Logging Output

The `requests.log` file contains entries like:
```
2024-06-14 10:30:15.123456 - User: testuser - Path: /api/conversations/
2024-06-14 10:30:16.234567 - User: Anonymous - Path: /api/auth/login/
2024-06-14 10:30:17.345678 - User: admin_user - Path: /api/messages/
```

## 🔒 Security Features

1. **Request Monitoring**: All requests are logged for audit trails
2. **Time-based Access**: Prevents access during off-hours
3. **Rate Limiting**: Prevents spam and abuse
4. **Role-based Access**: Ensures only authorized users access protected resources

## 🚀 Best Practices Implemented

1. **Separation of Concerns**: Each middleware has a single responsibility
2. **Performance**: Minimal database queries in middleware
3. **Error Handling**: Graceful handling of edge cases
4. **Logging**: Comprehensive request logging for debugging
5. **Documentation**: Clear inline comments and documentation

## 🔧 Customization Options

### Adjusting Time Restrictions

Modify the hours in `RestrictAccessByTimeMiddleware`:
```python
# Change allowed hours (currently 6AM-9PM)
if current_hour < 6 or current_hour >= 21:
```

### Changing Rate Limits

Modify limits in `OffensiveLanguageMiddleware`:
```python
self.max_requests = 5      # requests per window
self.time_window = 60      # window in seconds
```

### Adding Protected Paths

Update protected paths in `RolePermissionMiddleware`:
```python
self.protected_paths = [
    '/api/conversations/',
    '/api/messages/',
    '/api/users/',
    '/api/admin/',  # Add new protected path
]
```

## 🐛 Troubleshooting

### Common Issues

1. **Middleware not working**: Check MIDDLEWARE order in settings.py
2. **Logging not appearing**: Ensure write permissions for requests.log
3. **Role permissions too strict**: Check user role assignment
4. **Rate limiting too aggressive**: Adjust time_window and max_requests

### Debug Tips

1. Add print statements in middleware `__call__` methods
2. Check Django logs for middleware errors
3. Verify middleware order in settings.py
4. Test each middleware individually

## 📚 Additional Resources

- [Django Middleware Documentation](https://docs.djangoproject.com/en/stable/topics/http/middleware/)
- [Custom Middleware Best Practices](https://docs.djangoproject.com/en/stable/ref/middleware/)
- [Django Request/Response Cycle](https://docs.djangoproject.com/en/stable/topics/http/middleware/#activating-middleware)

This implementation demonstrates enterprise-grade middleware patterns suitable for production Django applications with proper logging, security, and access control mechanisms.
