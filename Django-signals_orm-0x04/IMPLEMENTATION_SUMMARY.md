# Django Signals, ORM & Caching Implementation Summary

## Overview
This project implements a comprehensive Django messaging application with advanced features including Django signals for event handling, ORM optimization techniques, and caching for improved performance.

## Implemented Features

### 1. Django Signals Implementation ✅

#### Task 0: User Notifications
- **Signal**: `post_save` on `Message` model
- **Function**: `create_message_notification()`
- **Purpose**: Automatically creates notifications for all conversation participants when a new message is sent
- **Models Added**:
  - `Notification` model with fields: `user`, `message`, `notification_type`, `is_read`, `created_at`
  - Supports notification types: `new_message`, `message_edit`, `mention`

#### Task 1: Message Edit History Logging
- **Signal**: `pre_save` on `Message` model
- **Function**: `log_message_edit()`
- **Purpose**: Logs old content before message updates and marks message as edited
- **Models Added**:
  - `MessageHistory` model with fields: `message`, `old_content`, `edited_at`
  - `edited` boolean field added to `Message` model

#### Task 2: User Data Cleanup
- **Signal**: `post_delete` on `User` model
- **Function**: `cleanup_user_data()`
- **Purpose**: Cleans up related data when a user account is deleted
- **Features**:
  - Removes empty conversations
  - Cascading deletion handled by foreign key constraints
  - Audit logging for deletion events

### 2. Advanced ORM Techniques ✅

#### Task 3: Threaded Conversations
- **Model Enhancement**: Added `parent_message` self-referential foreign key to `Message`
- **ORM Optimization**: 
  - `select_related()` for foreign key relationships
  - `prefetch_related()` for reverse foreign keys and many-to-many
  - Recursive query implementation for threaded replies
- **API Endpoint**: `/api/messages/{id}/threaded_replies/`

#### Task 4: Custom ORM Manager for Unread Messages
- **Manager**: `UnreadMessagesManager`
- **Methods**:
  - `for_user(user)`: Get unread messages for a specific user
  - `mark_as_read(user, conversation=None)`: Mark messages as read
- **Features**:
  - Uses `only()` to limit field loading for performance
  - Excludes sender's own messages from unread count
  - Supports conversation-specific filtering

### 3. Caching Implementation ✅

#### Task 5: View-Level Caching
- **Configuration**: Added `CACHES` setting with `LocMemCache` backend
- **Cache Timeout**: 60 seconds
- **Cached Endpoint**: `/api/messages/by_conversation/`
- **Implementation**: `@cache_page(60)` decorator

### Task 3: Testing the API Endpoints ✅
- **Postman Collection**: Comprehensive collection with all API endpoints
- **Environment Variables**: Postman environment with auto-variable setting
- **Test Documentation**: Detailed README for testing procedures
- **API Test Script**: Python script for automated API testing

**Files Created:**
- `post_man-Collections/messaging-app-api.postman_collection.json` - Complete API collection
- `post_man-Collections/messaging-app-environment.postman_environment.json` - Environment variables
- `post_man-Collections/README.md` - Testing documentation
- `test_api.py` - Automated test script

## 🔐 Security Features Implemented

### Authentication
- **JWT Token Authentication** with 60-minute access tokens
- **Refresh Token Rotation** with 7-day expiry
- **Token Blacklisting** on logout
- **Custom User Model** with UUID primary keys
- **Email-based Authentication** instead of username

### Authorization
- **Object-Level Permissions** - Users can only access their own data
- **Conversation Participant Validation** - Only participants can view/send messages
- **Global Authentication Requirement** - All API endpoints require authentication
- **Custom Permission Classes** for fine-grained control

### API Security
- **CORS Protection** through Django middleware
- **CSRF Protection** for session-based requests
- **Rate Limiting** capability through DRF throttling
- **Input Validation** through DRF serializers

## 📊 API Endpoints

### Authentication Endpoints
```
POST /api/auth/register/        - Register new user
POST /api/auth/login/           - User login
POST /api/auth/logout/          - User logout
POST /api/auth/token/refresh/   - Refresh JWT token
GET  /api/auth/profile/         - Get user profile
```

### Core API Endpoints
```
GET    /api/users/              - List users (paginated, searchable)
GET    /api/users/{id}/         - Get specific user

GET    /api/conversations/      - List user's conversations
POST   /api/conversations/      - Create conversation
GET    /api/conversations/{id}/ - Get conversation details
POST   /api/conversations/{id}/add_participant/ - Add participant

GET    /api/messages/           - List messages (filtered, paginated)
POST   /api/messages/           - Create message
GET    /api/messages/{id}/      - Get specific message
PATCH  /api/messages/{id}/      - Update message
DELETE /api/messages/{id}/      - Delete message
GET    /api/messages/by_conversation/ - Get messages by conversation
```

## 🔍 Filtering and Pagination

### Message Filtering
- By conversation ID
- By sender (user ID or username)
- By message content (contains search)
- By date range (sent_at_after, sent_at_before)

### Pagination
- **Default**: 20 items per page
- **Customizable**: `page_size` parameter (max 100)
- **Navigation**: `page` parameter with next/previous links
- **Response Format**: Includes count, total pages, current page info

### Example Requests
```bash
# Paginated messages
GET /api/messages/?page=1&page_size=10

# Filtered messages
GET /api/messages/?sender=user123&message_body=hello&sent_at_after=2024-01-01

# Search users
GET /api/users/?search=john&page=1
```

## 🧪 Testing Instructions

### 1. Start the Server
```bash
cd messaging_app
python manage.py runserver
```

### 2. Run Automated Tests
```bash
python test_api.py
```

### 3. Use Postman Collection
1. Import both JSON files from `post_man-Collections/`
2. Select "Messaging App Environment"
3. Run requests in sequence starting with "Register User"

### 4. Manual Testing Examples
```bash
# Register user
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123","first_name":"Test","last_name":"User"}'

# Login user
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Access protected endpoint
curl -X GET http://127.0.0.1:8000/api/conversations/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📁 File Structure

```
messaging_app/
├── messaging_app/
│   ├── settings.py          # JWT and DRF configuration
│   └── urls.py              # Main URL routing
├── chats/
│   ├── models.py            # User, Conversation, Message models
│   ├── auth.py              # Authentication views
│   ├── permissions.py       # Custom permission classes
│   ├── filters.py           # Django-filter classes
│   ├── pagination.py        # Custom pagination classes
│   ├── views.py             # API viewsets
│   ├── serializers.py       # DRF serializers
│   └── urls.py              # App URL patterns
├── post_man-Collections/
│   ├── messaging-app-api.postman_collection.json
│   ├── messaging-app-environment.postman_environment.json
│   └── README.md            # Testing documentation
└── test_api.py              # Automated test script
```

## 🔧 Configuration Details

### JWT Settings
- **Access Token Lifetime**: 60 minutes
- **Refresh Token Lifetime**: 7 days
- **Token Rotation**: Enabled
- **Blacklisting**: Enabled after rotation

### DRF Settings
- **Authentication**: JWT + Session
- **Permissions**: Authenticated users required
- **Pagination**: 20 items per page
- **Filtering**: Django-filter backend enabled

### Custom User Model
- **Primary Key**: UUID field
- **Authentication Field**: Email
- **Required Fields**: username, first_name, last_name

## 🎯 Key Features

1. **Secure Authentication**: JWT-based with proper token lifecycle management
2. **Granular Permissions**: Object-level access control for conversations and messages
3. **Comprehensive Filtering**: Search and filter across all major fields
4. **Pagination**: Efficient data loading with customizable page sizes
5. **API Documentation**: Postman collection with automated variable management
6. **Testing Suite**: Both automated Python tests and manual Postman tests
7. **Production Ready**: Proper error handling, validation, and security measures

## 🚀 Next Steps

The messaging app now has a complete authentication and permission system ready for production use. Key capabilities include:

- Secure user registration and login
- JWT token-based authentication
- Object-level permissions ensuring data privacy
- Comprehensive API filtering and pagination
- Full test suite for quality assurance

The system is now ready for frontend integration and deployment to production environments.
