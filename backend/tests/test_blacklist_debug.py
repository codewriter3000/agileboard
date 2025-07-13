#!/usr/bin/env python3
"""Direct test of token blacklisting without external dependencies."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.auth import create_access_token, verify_token, revoke_all_user_tokens, token_blacklist
from app.core.deps import get_current_user
from app.db.session import SessionLocal
from app.crud import user as user_crud
from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import Mock

def test_token_blacklisting_with_deps():
    """Test token blacklisting with the actual dependency system."""
    print("=== Testing Token Blacklisting with Dependencies ===")

    # Create a test token
    token_data = {"sub": "test@example.com", "user_id": 1}
    token = create_access_token(token_data)
    print(f"Created token: {token[:50]}...")

    # Test 1: Verify token works initially
    print("\n1. Testing initial token verification...")
    try:
        decoded = verify_token(token)
        print(f"✅ Token verification successful: {decoded.email}")
    except Exception as e:
        print(f"❌ Token verification failed: {e}")
        return

    # Test 2: Check if token is tracked
    print(f"\n2. Token tracking status:")
    print(f"   User tokens tracked: {len(token_blacklist._user_tokens.get(1, set()))}")
    print(f"   Token in user tokens: {token in token_blacklist._user_tokens.get(1, set())}")
    print(f"   Token blacklisted: {token_blacklist.is_blacklisted(token)}")

    # Test 3: Revoke all user tokens
    print(f"\n3. Revoking all user tokens...")
    revoke_all_user_tokens(1)

    # Test 4: Check blacklist status after revocation
    print(f"\n4. Post-revocation status:")
    print(f"   Token blacklisted: {token_blacklist.is_blacklisted(token)}")
    print(f"   Blacklist size: {len(token_blacklist._blacklist)}")
    print(f"   User tokens remaining: {len(token_blacklist._user_tokens.get(1, set()))}")

    # Test 5: Try to verify token again
    print(f"\n5. Testing token verification after revocation...")
    try:
        decoded = verify_token(token)
        print(f"❌ Token verification should have failed but succeeded: {decoded.email}")
    except Exception as e:
        print(f"✅ Token verification correctly failed: {e}")

    # Test 6: Test with mock credentials (simulating FastAPI dependency)
    print(f"\n6. Testing with mock HTTPAuthorizationCredentials...")
    try:
        # Create mock credentials
        mock_credentials = Mock(spec=HTTPAuthorizationCredentials)
        mock_credentials.credentials = token

        # Test the get_current_user dependency directly
        db = SessionLocal()
        try:
            from app.core.deps import get_current_user
            # This should fail since we can't easily mock the database user
            print("   Cannot test get_current_user without proper database setup")
        except Exception as e:
            print(f"   Database dependency test skipped: {e}")
        finally:
            db.close()

    except Exception as e:
        print(f"❌ Mock credentials test failed: {e}")

def test_blacklist_internal_state():
    """Test the internal state of the blacklist."""
    print("\n=== Testing Blacklist Internal State ===")

    # Create multiple tokens for the same user
    user_id = 123
    tokens = []
    for i in range(3):
        token_data = {"sub": f"user{i}@example.com", "user_id": user_id}
        token = create_access_token(token_data)
        tokens.append(token)

    print(f"Created {len(tokens)} tokens for user {user_id}")
    print(f"User tokens tracked: {len(token_blacklist._user_tokens.get(user_id, set()))}")

    # Verify all tokens work
    for i, token in enumerate(tokens):
        try:
            verify_token(token)
            print(f"✅ Token {i+1} verified successfully")
        except Exception as e:
            print(f"❌ Token {i+1} verification failed: {e}")

    # Revoke all tokens for this user
    print(f"\nRevoking all tokens for user {user_id}...")
    revoke_all_user_tokens(user_id)

    print(f"Blacklist size after revocation: {len(token_blacklist._blacklist)}")

    # Test all tokens are blacklisted
    for i, token in enumerate(tokens):
        try:
            verify_token(token)
            print(f"❌ Token {i+1} should be blacklisted but still works")
        except Exception as e:
            print(f"✅ Token {i+1} correctly blacklisted: {e}")

if __name__ == "__main__":
    test_token_blacklisting_with_deps()
    test_blacklist_internal_state()
