#!/usr/bin/env python3
"""Comprehensive test to debug token blacklisting with actual API calls."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User",
    "role": "Admin"
}

def test_full_authentication_flow():
    """Test the complete authentication flow with API calls."""
    print("=== Testing Full Authentication Flow ===")

    # Step 1: Try to create a test user (might fail if exists)
    print("\n1. Creating test user...")
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
        if response.status_code == 200:
            print("✅ Test user created successfully")
        elif response.status_code == 403:
            print("ℹ️  Registration disabled, user should already exist")
        else:
            print(f"⚠️  User creation response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error creating user: {e}")

    # Step 2: Login to get token
    print("\n2. Logging in...")
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        })

        if login_response.status_code == 200:
            login_data = login_response.json()
            token = login_data["access_token"]
            print(f"✅ Login successful, token: {token[:50]}...")

            # Step 3: Test protected endpoint
            print("\n3. Testing protected endpoint...")
            headers = {"Authorization": f"Bearer {token}"}
            users_response = requests.get(f"{BASE_URL}/users/", headers=headers)

            if users_response.status_code == 200:
                print("✅ Protected endpoint accessible before logout")
            else:
                print(f"❌ Protected endpoint failed: {users_response.status_code} - {users_response.text}")
                return

            # Step 4: Logout
            print("\n4. Logging out...")
            logout_response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)

            if logout_response.status_code == 200:
                print("✅ Logout successful")
            else:
                print(f"❌ Logout failed: {logout_response.status_code} - {logout_response.text}")
                return

            # Step 5: Test protected endpoint after logout
            print("\n5. Testing protected endpoint after logout...")
            users_response_after = requests.get(f"{BASE_URL}/users/", headers=headers)

            if users_response_after.status_code == 401:
                print("✅ Protected endpoint correctly blocked after logout")
                print(f"Response: {users_response_after.text}")
            else:
                print(f"❌ Protected endpoint still accessible after logout!")
                print(f"Status: {users_response_after.status_code}")
                print(f"Response: {users_response_after.text}")

                # Debug: Test token verification directly
                print("\n6. Debug: Testing token verification...")
                from app.core.auth import verify_token, token_blacklist

                try:
                    token_data = verify_token(token)
                    print(f"❌ Token verification should have failed but succeeded: {token_data}")
                except Exception as e:
                    print(f"✅ Token verification correctly failed: {e}")

                print(f"Token in blacklist: {token_blacklist.is_blacklisted(token)}")
                print(f"Blacklist size: {len(token_blacklist._blacklist)}")
                print(f"User tokens: {len(token_blacklist._user_tokens)}")

        else:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")

    except Exception as e:
        print(f"❌ Error during authentication flow: {e}")

if __name__ == "__main__":
    test_full_authentication_flow()
