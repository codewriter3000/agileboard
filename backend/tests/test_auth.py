"""
Unit tests for authentication and authorization business rules.

Tests cover:
- User login/logout
- Token generation and validation
- Token blacklisting
- Role-based access control
- Password hashing and verification
"""

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
    """Test authentication core functionality."""

    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "test_password_123"
        hashed = get_password_hash(password)

        # Password should be hashed
        assert hashed != password
        assert len(hashed) > 0

        # Verification should work
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False

    def test_token_creation(self):
        """Test JWT token creation."""
        email = "test@example.com"
        token = create_access_token(data={"sub": email})

        assert token is not None
        assert len(token) > 0
        assert isinstance(token, str)

    def test_token_verification(self):
        """Test JWT token verification."""
        email = "test@example.com"
        user_id = 1
        token = create_access_token(data={"sub": email, "user_id": user_id})

        # Valid token should verify
        token_data = verify_token(token)
        assert token_data.email == email
        assert token_data.user_id == user_id

        # Invalid token should raise exception
        with pytest.raises(HTTPException) as exc_info:
            verify_token("invalid_token")
        assert exc_info.value.status_code == 401

    def test_token_blacklisting(self):
        """Test token blacklisting functionality."""
        email = "test@example.com"
        user_id = 1
        token = create_access_token(data={"sub": email, "user_id": user_id})

        # Token should be valid initially
        assert not token_blacklist.is_blacklisted(token)
        token_data = verify_token(token)
        assert token_data.email == email

        # Add token to blacklist using a future expiration time
        import time
        future_expiration = time.time() + 3600  # 1 hour from now
        token_blacklist.add_token(token, future_expiration, user_id)
        assert token_blacklist.is_blacklisted(token)

        # Blacklisted token should not verify
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        assert exc_info.value.status_code == 401
        assert "Token has been revoked" in str(exc_info.value.detail)
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        assert exc_info.value.status_code == 401
        assert "Token has been revoked" in str(exc_info.value.detail)

    def test_user_token_tracking(self):
        """Test user token tracking and revocation."""
        email = "test@example.com"
        user_id = 1
        token1 = create_access_token(data={"sub": email, "user_id": user_id})
        token2 = create_access_token(data={"sub": email, "user_id": user_id})

        # Track tokens for user
        import time
        future_expiration = time.time() + 3600  # 1 hour from now
        token_blacklist.add_token(token1, future_expiration, user_id)
        token_blacklist.add_token(token2, future_expiration, user_id)

        # Both tokens should be tracked
        assert len(token_blacklist._user_tokens[user_id]) == 2

        # Revoke all user tokens
        revoke_all_user_tokens(user_id)

        # All tokens should be blacklisted
        assert token_blacklist.is_blacklisted(token1)
        assert token_blacklist.is_blacklisted(token2)

        # Tokens should not verify
        with pytest.raises(HTTPException):
            verify_token(token1)
        with pytest.raises(HTTPException):
            verify_token(token2)

    def test_blacklist_cleanup(self):
        """Test automatic cleanup of expired tokens."""
        email = "test@example.com"
        user_id = 1

        # Create token and add to blacklist with past expiration time
        token = create_access_token(data={"sub": email, "user_id": user_id})
        import time
        past_expiration = time.time() - 3600  # 1 hour ago
        token_blacklist.add_token(token, past_expiration, user_id)

        # Token should initially be in blacklist structure
        assert token in token_blacklist._blacklist

        # But checking if blacklisted should trigger cleanup and return False
        assert not token_blacklist.is_blacklisted(token)

        # Token should be removed from blacklist after cleanup
        assert token not in token_blacklist._blacklist

        # Cleanup should remove expired token
        token_blacklist._cleanup_expired()

        # Token should be removed from blacklist
        assert not token_blacklist.is_blacklisted(token)


class TestAuthenticationAPI:
    """Test authentication API endpoints."""

    def test_login_success(self, client, test_users):
        """Test successful login."""
        response = client.post("/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "admin@test.com"
        assert data["user"]["role"] == "Admin"

    def test_login_invalid_credentials(self, client, test_users):
        """Test login with invalid credentials."""
        response = client.post("/auth/login", json={
            "email": "admin@test.com",
            "password": "wrong_password"
        })
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_inactive_user(self, client, test_users):
        """Test login with inactive user."""
        response = client.post("/auth/login", json={
            "email": "inactive@test.com",
            "password": "inactive123"
        })

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client, test_users):
        """Test login with non-existent user."""
        response = client.post("/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "password"
        })

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_oauth2_token_endpoint(self, client, test_users):
        """Test OAuth2 token endpoint."""
        response = client.post("/auth/token", data={
            "username": "admin@test.com",
            "password": "admin123"
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_logout_success(self, client, test_users, auth_headers):
        """Test successful logout."""
        response = client.post("/auth/logout", headers=auth_headers["admin"])

        assert response.status_code == 200
        assert "Successfully logged out from all devices" in response.json()["message"]

    def test_logout_invalid_token(self, client):
        """Test logout with invalid token."""
        response = client.post("/auth/logout", headers={
            "Authorization": "Bearer invalid_token"
        })

        assert response.status_code == 401

    def test_logout_current_success(self, client, test_users, auth_headers):
        """Test logout current session."""
        response = client.post("/auth/logout-current", headers=auth_headers["admin"])

        assert response.status_code == 200
        assert "Successfully logged out from current device" in response.json()["message"]

    def test_token_revocation_after_logout(self, client, test_users, auth_headers):
        """Test that tokens are revoked after logout."""
        # Make authenticated request
        response = client.get("/users/", headers=auth_headers["admin"])
        assert response.status_code == 200

        # Logout
        client.post("/auth/logout", headers=auth_headers["admin"])

        # Try to use same token - should fail
        response = client.get("/users/", headers=auth_headers["admin"])
        assert response.status_code == 401


class TestRoleBasedAccess:
    """Test role-based access control."""

    def test_admin_access(self, client, test_users, auth_headers):
        """Test admin can access all endpoints."""
        # Admin can access users
        response = client.get("/users/", headers=auth_headers["admin"])
        assert response.status_code == 200

        # Admin can create users
        response = client.post("/users/", json={
            "email": "new@test.com",
            "full_name": "New User",
            "password": "password123",
            "role": "Developer"
        }, headers=auth_headers["admin"])
        assert response.status_code == 200

        # Admin can delete users
        response = client.delete(f"/users/{test_users['dev'].id}", headers=auth_headers["admin"])
        assert response.status_code == 204  # DELETE typically returns 204 No Content

    def test_scrum_master_access(self, client, test_users, auth_headers):
        """Test scrum master can manage tasks and users but not create users."""
        # Scrum master can access users
        response = client.get("/users/", headers=auth_headers["scrum"])
        assert response.status_code == 200

        # Scrum master cannot create users (only admins can)
        response = client.post("/users/", json={
            "email": "new2@test.com",
            "full_name": "New User 2",
            "password": "password123",
            "role": "Developer"
        }, headers=auth_headers["scrum"])
        assert response.status_code == 403  # Scrum master can't create users

        # Scrum master can create tasks
        response = client.post("/tasks/", json={
            "title": "Scrum Master Task",
            "description": "Task created by scrum master",
            "project_id": 1
        }, headers=auth_headers["scrum"])
        assert response.status_code == 200

        # Scrum master can update tasks (assign, change status, etc.)
        response = client.put("/tasks/1", json={
            "title": "Updated Task",
            "status": "In Progress"
        }, headers=auth_headers["scrum"])
        assert response.status_code == 400  # Status validation error - need assignee for In Progress

        # Scrum master can delete tasks
        response = client.delete("/tasks/1", headers=auth_headers["scrum"])
        assert response.status_code == 204

        # Scrum master can update users but not change roles
        response = client.put(f"/users/{test_users['dev'].id}", json={
            "email": "updated@test.com",
            "full_name": "Updated Name"
        }, headers=auth_headers["scrum"])
        assert response.status_code == 200

        # Scrum master cannot change user roles
        response = client.put(f"/users/{test_users['dev'].id}", json={
            "role": "Admin"
        }, headers=auth_headers["scrum"])
        assert response.status_code == 403

        # Scrum master cannot delete users (admin only)
        response = client.delete(f"/users/{test_users['dev'].id}", headers=auth_headers["scrum"])
        assert response.status_code == 403

    def test_developer_access(self, client, test_users, auth_headers):
        """Test developer has read-only access to tasks and can only change their own profile."""
        # Developer can view users
        response = client.get("/users/", headers=auth_headers["dev"])
        assert response.status_code == 200

        # Developer cannot create users
        response = client.post("/users/", json={
            "email": "new3@test.com",
            "full_name": "New User 3",
            "password": "password123",
            "role": "Developer"
        }, headers=auth_headers["dev"])
        assert response.status_code == 403

        # Developer can view tasks (read-only)
        response = client.get("/tasks/", headers=auth_headers["dev"])
        assert response.status_code == 200

        # Developer cannot create tasks
        response = client.post("/tasks/", json={
            "title": "New Task",
            "description": "Task description",
            "project_id": 1
        }, headers=auth_headers["dev"])
        assert response.status_code == 403

        # Developer can update their own profile (email and password only)
        response = client.put(f"/users/{test_users['dev'].id}", json={
            "email": "newemail@test.com",
            "password": "newpassword123"
        }, headers=auth_headers["dev"])
        assert response.status_code == 200

        # Developer cannot update other users' profiles
        response = client.put(f"/users/{test_users['admin'].id}", json={
            "email": "hackeremail@test.com"
        }, headers=auth_headers["dev"])
        assert response.status_code == 403

        # Developer cannot delete users
        response = client.delete(f"/users/{test_users['admin'].id}", headers=auth_headers["dev"])
        assert response.status_code == 403

    def test_unauthenticated_access(self, client, test_users):
        """Test unauthenticated requests are denied."""
        response = client.get("/users/")
        assert response.status_code == 403  # Unauthenticated requests get 403

        response = client.get("/projects/")
        assert response.status_code == 403  # Unauthenticated requests get 403

        response = client.get("/tasks/")
        assert response.status_code == 403  # Unauthenticated requests get 403
