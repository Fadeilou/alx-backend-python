#!/usr/bin/env python3
"""
Simple demonstration of middleware functionality.
Run this after starting the Django server.
"""

import os
import sys
from datetime import datetime

def demonstrate_middleware():
    print("🔧 Django Middleware Demonstration")
    print("=" * 50)
    
    print("\n📁 Project Structure:")
    print("Django-Middleware-0x03/")
    print("├── chats/middleware.py        # All middleware implementations")
    print("├── requests.log               # Request logging output")
    print("├── messaging_app/settings.py  # Middleware configuration")
    print("└── test_middleware.py         # Test script")
    
    print("\n🔧 Implemented Middleware:")
    print("1. RequestLoggingMiddleware    - Logs all requests with timestamp and user")
    print("2. RestrictAccessByTimeMiddleware - Blocks access outside 6AM-9PM")
    print("3. OffensiveLanguageMiddleware - Rate limiting (5 requests/minute)")
    print("4. RolePermissionMiddleware    - Role-based access control")
    
    print("\n⚙️ Middleware Order (settings.py):")
    middleware_order = [
        "SecurityMiddleware",
        "SessionMiddleware", 
        "CommonMiddleware",
        "CsrfViewMiddleware",
        "AuthenticationMiddleware",
        "→ RequestLoggingMiddleware",
        "→ RestrictAccessByTimeMiddleware", 
        "→ OffensiveLanguageMiddleware",
        "→ RolePermissionMiddleware",
        "MessageMiddleware",
        "ClickjackingMiddleware"
    ]
    
    for i, middleware in enumerate(middleware_order, 1):
        if middleware.startswith("→"):
            print(f"   {i:2d}. {middleware[2:]} (CUSTOM)")
        else:
            print(f"   {i:2d}. {middleware}")
    
    print("\n🕐 Current Time Check:")
    current_time = datetime.now()
    current_hour = current_time.hour
    print(f"   Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Hour: {current_hour}")
    
    if 6 <= current_hour < 21:
        print("   ✅ Within allowed hours (6AM-9PM) - Access permitted")
    else:
        print("   ❌ Outside allowed hours (6AM-9PM) - Access will be blocked")
    
    print("\n🧪 To test the middleware:")
    print("1. Start Django server: python manage.py runserver")
    print("2. Run test script: python test_middleware.py")
    print("3. Check requests.log for logging output")
    print("4. Try API calls at different times to test time restrictions")
    print("5. Make rapid API calls to test rate limiting")
    
    print("\n📝 Expected Middleware Behavior:")
    print("• All requests logged to requests.log file")
    print("• Access blocked outside 6AM-9PM with 403 error")
    print("• POST requests limited to 5 per minute per IP")
    print("• Protected endpoints require admin/moderator role")
    
    print("\n🔍 Log File Check:")
    try:
        if os.path.exists('requests.log'):
            with open('requests.log', 'r') as f:
                lines = f.readlines()
                if lines:
                    print(f"   📄 Found {len(lines)} log entries in requests.log")
                    print("   Latest entry:", lines[-1].strip() if lines else "None")
                else:
                    print("   📄 requests.log exists but is empty")
        else:
            print("   📄 requests.log not found (will be created on first request)")
    except Exception as e:
        print(f"   ❌ Error reading log file: {e}")
    
    print("\n" + "=" * 50)
    print("✨ Middleware setup complete and ready for testing!")

if __name__ == "__main__":
    demonstrate_middleware()
