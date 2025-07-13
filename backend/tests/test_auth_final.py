#!/usr/bin/env python3
"""
Final test of authentication and token blacklisting functionality.
Tests the complete auth flow with stable server (no auto-reload).
"""

import requests
import json
import time
from datetime import datetime


def test_auth_flow():
    """Test complete authentication flow with token blacklisting"""
    base_url = "http://localhost:8000"
    
    # Test data
    test_user = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    print("=== Authentication Flow Test ===")
    print(f"Starting test at {datetime.now()}")
    
    # Step 1: Login
    print("\n1. Logging in...")
    login_response = requests.post(
        f"{base_url}/login",
        json=test_user
    )
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        token = login_data["access_token"]
        print(f"Token received: {token[:50]}...")
        
        # Step 2: Access protected endpoint
        print("\n2. Accessing protected endpoint...")
        headers = {"Authorization": f"Bearer {token}"}
        protected_response = requests.get(
            f"{base_url}/users/",
            headers=headers
        )
        print(f"Protected endpoint status: {protected_response.status_code}")
        
        if protected_response.status_code == 200:
            print("✓ Successfully accessed protected endpoint")
            
            # Step 3: Logout
            print("\n3. Logging out...")
            logout_response = requests.post(
                f"{base_url}/logout",
                headers=headers
            )
            print(f"Logout status: {logout_response.status_code}")
            
            if logout_response.status_code == 200:
                print("✓ Successfully logged out")
                
                # Step 4: Try to access protected endpoint again (should fail)
                print("\n4. Trying to access protected endpoint after logout...")
                protected_response_after_logout = requests.get(
                    f"{base_url}/users/",
                    headers=headers
                )
                print(f"Protected endpoint after logout status: {protected_response_after_logout.status_code}")
                
                if protected_response_after_logout.status_code == 401:
                    print("✓ Token successfully blacklisted - access denied")
                    print("🎉 AUTHENTICATION FLOW TEST PASSED!")
                else:
                    print("❌ Token not blacklisted - access still allowed")
                    print("🔥 AUTHENTICATION FLOW TEST FAILED!")
                    
            else:
                print("❌ Logout failed")
                
        else:
            print("❌ Could not access protected endpoint")
            
    else:
        print(f"❌ Login failed: {login_response.text}")
        
    print(f"\nTest completed at {datetime.now()}")


if __name__ == "__main__":
    test_auth_flow()
