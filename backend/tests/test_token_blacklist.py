#!/usr/bin/env python3
"""Test script to verify token blacklisting functionality."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.auth import create_access_token, token_blacklist, verify_token, revoke_all_user_tokens
from datetime import timedelta

def test_token_blacklist():
    print("Testing token blacklist functionality...")

    # Create a token for user 1
    token_data = {"sub": "test@example.com", "user_id": 1}
    token = create_access_token(token_data)

    print(f"Created token: {token[:50]}...")

    # Verify token works initially
    try:
        decoded = verify_token(token)
        print(f"✅ Token verification successful: {decoded.email}")
    except Exception as e:
        print(f"❌ Token verification failed: {e}")
        return

    # Check blacklist status
    print(f"Token blacklisted before logout: {token_blacklist.is_blacklisted(token)}")
    print(f"User tokens tracked: {len(token_blacklist._user_tokens.get(1, set()))}")

    # Revoke all user tokens
    print("\nRevoking all user tokens...")
    revoke_all_user_tokens(1)

    # Check blacklist status after revocation
    print(f"Token blacklisted after logout: {token_blacklist.is_blacklisted(token)}")
    print(f"Tokens in blacklist: {len(token_blacklist._blacklist)}")

    # Try to verify token again
    try:
        decoded = verify_token(token)
        print(f"❌ Token verification should have failed but succeeded: {decoded.email}")
    except Exception as e:
        print(f"✅ Token verification correctly failed: {e}")

if __name__ == "__main__":
    test_token_blacklist()
