import pytest
from fastapi import HTTPException
from unittest.mock import patch

from app.core.auth import (
    create_access_token,
    verify_token,
    get_password_hash,
    verify_password,
    token_blacklist,
    revoke_all_user_tokens
)
from app.schemas.user import Role

class TestAuthentication:
    def test_token_verification(self):
        # Create a token for a user
        user_data = {"sub": "testuser", "role": Role.USER}
        token = create_access_token(user_data)

        # Token should not be blacklisted initially
        assert token not in token_blacklist

        # Verify the token
        payload = verify_token(token)
        assert payload["sub"] == "testuser"
        assert payload["role"] == Role.USER

        # Blacklist the token
        token_blacklist.add(token)

        # Now verification should fail
        with pytest.raises(HTTPException):
            verify_token(token)
