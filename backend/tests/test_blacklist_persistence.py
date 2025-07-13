#!/usr/bin/env python3
"""Test blacklist persistence across API calls."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.auth import create_access_token, verify_token, revoke_all_user_tokens, token_blacklist
import time

def test_blacklist_persistence():
    """Test if blacklist persists across function calls."""
    print("=== Testing Blacklist Persistence ===")

    # Create a token
    token_data = {"sub": "persistence@example.com", "user_id": 999}
    token = create_access_token(token_data)
    print(f"Created token for user 999: {token[:50]}...")

    # Verify it works
    try:
        verify_token(token)
        print("✅ Token works initially")
    except Exception as e:
        print(f"❌ Token failed initially: {e}")
        return

    # Add to blacklist
    revoke_all_user_tokens(999)
    print("Revoked all tokens for user 999")

    # Check multiple times
    for i in range(3):
        time.sleep(0.1)  # Small delay
        is_blacklisted = token_blacklist.is_blacklisted(token)
        print(f"Check {i+1}: Token blacklisted = {is_blacklisted}")

        try:
            verify_token(token)
            print(f"❌ Check {i+1}: Token still works (should fail)")
        except Exception as e:
            print(f"✅ Check {i+1}: Token correctly failed: {e}")

    # Print internal state
    print(f"\nInternal state:")
    print(f"Blacklist size: {len(token_blacklist._blacklist)}")
    print(f"User tokens: {len(token_blacklist._user_tokens)}")
    print(f"Blacklist ID: {id(token_blacklist)}")

def test_multiple_blacklist_instances():
    """Test if we might have multiple blacklist instances."""
    print("\n=== Testing Multiple Blacklist Instances ===")

    from app.core.auth import token_blacklist as blacklist1
    from app.core.auth import token_blacklist as blacklist2

    print(f"Blacklist 1 ID: {id(blacklist1)}")
    print(f"Blacklist 2 ID: {id(blacklist2)}")
    print(f"Are they the same object? {blacklist1 is blacklist2}")

    # Test importing from different modules
    from app.core import auth
    print(f"auth.token_blacklist ID: {id(auth.token_blacklist)}")
    print(f"Same as original? {auth.token_blacklist is token_blacklist}")

if __name__ == "__main__":
    test_blacklist_persistence()
    test_multiple_blacklist_instances()
