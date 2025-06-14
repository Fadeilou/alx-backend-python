#!/usr/bin/env python3
"""
Test script to demonstrate Django middleware functionality.
This script tests all the implemented middleware components.
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_middleware():
    print("🧪 Testing Django Middleware Components...")
    print("=" * 60)
    
    # Test 1: Request Logging Middleware
    print("\n1. Testing Request Logging Middleware...")
    print("   Making a request to test logging...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/users/")
        print(f"   Status: {response.status_code}")
        print("   ✅ Check requests.log file for logged request")
    except requests.exceptions.ConnectionError:
        print("   ❌ Server not running. Start with: python manage.py runserver")
        return
    
    # Test 2: Time Restriction Middleware
    print("\n2. Testing Time Restriction Middleware...")
    current_hour = datetime.now().hour
    print(f"   Current time: {datetime.now().strftime('%H:%M')} (Hour: {current_hour})")
    
    if 6 <= current_hour < 21:
        print("   ✅ Currently within allowed hours (6AM-9PM)")
        print("   Chat access should be allowed")
    else:
        print("   ⏰ Currently outside allowed hours (6AM-9PM)")
        print("   Chat access should be restricted with 403 error")
    
    # Test 3: Rate Limiting Middleware
    print("\n3. Testing Rate Limiting Middleware...")
    print("   Sending 6 POST requests rapidly to test rate limiting...")
    
    # First, try to register/login to get a token
    test_user = {
        "username": "testuser_middleware",
        "email": "test_middleware@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "Middleware"
    }
    
    try:
        # Register user
        response = requests.post(f"{BASE_URL}/api/auth/register/", json=test_user)
        if response.status_code == 201:
            data = response.json()
            token = data['access']
            headers = {"Authorization": f"Bearer {token}"}
            print(f"   ✅ User registered, token obtained")
            
            # Create a conversation first
            conv_response = requests.post(
                f"{BASE_URL}/api/conversations/", 
                json={"participant_ids": [data['user']['user_id']]},
                headers=headers
            )
            
            if conv_response.status_code in [200, 201]:
                conversation_id = conv_response.json()['conversation_id']
                print(f"   ✅ Conversation created: {conversation_id}")
                
                # Test rate limiting with multiple message posts
                for i in range(6):
                    message_data = {
                        "conversation": conversation_id,
                        "message_body": f"Test message {i+1} for rate limiting"
                    }
                    response = requests.post(f"{BASE_URL}/api/messages/", json=message_data, headers=headers)
                    print(f"   Message {i+1}: Status {response.status_code}")
                    
                    if response.status_code == 429:
                        print(f"   ✅ Rate limit triggered at message {i+1}")
                        break
                    
                    time.sleep(0.1)  # Small delay between requests
        
        elif response.status_code == 400 and "already exists" in response.text:
            print("   ℹ️  User already exists, trying to login...")
            # Try to login
            login_response = requests.post(f"{BASE_URL}/api/auth/login/", json={
                "email": test_user["email"],
                "password": test_user["password"]
            })
            if login_response.status_code == 200:
                print("   ✅ Login successful")
    
    except Exception as e:
        print(f"   ❌ Error testing rate limiting: {e}")
    
    # Test 4: Role Permission Middleware
    print("\n4. Testing Role Permission Middleware...")
    print("   Testing access without admin/moderator role...")
    
    try:
        # Test without token (should get 401)
        response = requests.get(f"{BASE_URL}/api/conversations/")
        print(f"   No auth - Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Correctly blocked unauthenticated user")
        
        # Test with regular user token (should get 403 if role middleware is working)
        if 'headers' in locals():
            response = requests.get(f"{BASE_URL}/api/conversations/", headers=headers)
            print(f"   Regular user - Status: {response.status_code}")
            if response.status_code == 403:
                print("   ✅ Correctly blocked non-admin/moderator user")
            elif response.status_code == 200:
                print("   ⚠️  User has admin/moderator access OR middleware not active")
    
    except Exception as e:
        print(f"   ❌ Error testing role permissions: {e}")
    
    # Test 5: Check logs
    print("\n5. Checking Request Logs...")
    try:
        with open('requests.log', 'r') as f:
            lines = f.readlines()
            print(f"   📝 Found {len(lines)} log entries")
            if lines:
                print("   Latest entries:")
                for line in lines[-3:]:  # Show last 3 entries
                    print(f"   {line.strip()}")
                print("   ✅ Request logging is working")
            else:
                print("   ⚠️  No log entries found")
    except FileNotFoundError:
        print("   ❌ requests.log file not found")
    
    print("\n" + "=" * 60)
    print("🎉 Middleware testing completed!")
    print("\nMiddleware Order in MIDDLEWARE setting:")
    print("1. RequestLoggingMiddleware - Logs all requests")
    print("2. RestrictAccessByTimeMiddleware - Time-based access control")
    print("3. OffensiveLanguageMiddleware - Rate limiting")
    print("4. RolePermissionMiddleware - Role-based access control")

if __name__ == "__main__":
    test_middleware()
