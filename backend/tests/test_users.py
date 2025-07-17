"""
Unit tests for user management business rules.

Tests cover:
- User CRUD operations
- Role-based permissions
- User validation
- Active/inactive status
- Email uniqueness
"""

import pytest
from app.schemas.user import Role


class TestUserCRUD:
    """Test user CRUD operations."""

    def test_get_all_users(self, client, test_users, auth_headers):
        """Test getting all users."""
        response = client.get("/users/", headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3  # admin, scrum, dev (inactive not included)

        # Verify user data structure
        user = data[0]
        assert "id" in user
        assert "email" in user
        assert "full_name" in user
        assert "role" in user
        assert "is_active" in user
        assert "hashed_password" not in user  # Password should not be exposed

    def test_get_user_by_id(self, client, test_users, auth_headers):
        """Test getting user by ID."""
        user_id = test_users["dev"].id
        response = client.get(f"/users/{user_id}", headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == "dev@test.com"
        assert data["full_name"] == "Developer User"
        assert data["role"] == "Developer"

    def test_get_nonexistent_user(self, client, auth_headers):
        """Test getting non-existent user."""
        response = client.get("/users/99999", headers=auth_headers["admin"])

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_create_user_admin(self, client, auth_headers):
        """Test admin can create users."""
        new_user = {
            "email": "newuser@test.com",
            "full_name": "New Test User",
            "password": "Password123!",
            "role": "Developer"
        }

        response = client.post("/users/", json=new_user, headers=auth_headers["admin"])

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == new_user["email"]
        assert data["full_name"] == new_user["full_name"]
        assert data["role"] == new_user["role"]
        assert data["is_active"] is True
        assert "hashed_password" not in data

    def test_create_user_scrum_master_forbidden(self, client, auth_headers):
        """Test scrum master cannot create users."""
        new_user = {
            "email": "scrumcreated@test.com",
            "full_name": "Scrum Created User",
            "password": "Password123!",
            "role": "Developer"
        }

        response = client.post("/users/", json=new_user, headers=auth_headers["scrum"])

        assert response.status_code == 403

    def test_create_user_developer_forbidden(self, client, auth_headers):
        """Test developer cannot create users."""
        new_user = {
            "email": "forbidden@test.com",
            "full_name": "Forbidden User",
            "password": "Password123!",
            "role": "Developer"
        }

        response = client.post("/users/", json=new_user, headers=auth_headers["dev"])

        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

    def test_create_user_duplicate_email(self, client, test_users, auth_headers):
        """Test cannot create user with duplicate email."""
        duplicate_user = {
            "email": "admin@test.com",  # Already exists
            "full_name": "Duplicate User",
            "password": "Password123!",
            "role": "Developer"
        }

        response = client.post("/users/", json=duplicate_user, headers=auth_headers["admin"])

        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_create_user_invalid_role(self, client, auth_headers):
        """Test cannot create user with invalid role."""
        invalid_user = {
            "email": "invalid@test.com",
            "full_name": "Invalid User",
            "password": "Password123!",
            "role": "InvalidRole"
        }

        response = client.post("/users/", json=invalid_user, headers=auth_headers["admin"])

        assert response.status_code == 422  # Validation error

    def test_create_user_invalid_email(self, client, auth_headers):
        """Test cannot create user with invalid email."""
        invalid_user = {
            "email": "not-an-email",
            "full_name": "Invalid User",
            "password": "Password123!",
            "role": "Developer"
        }

        response = client.post("/users/", json=invalid_user, headers=auth_headers["admin"])

        assert response.status_code == 422  # Validation error

    def test_create_user_missing_fields(self, client, auth_headers):
        """Test cannot create user with missing required fields."""
        incomplete_user = {
            "email": "incomplete@test.com",
            # Missing full_name, password, role
        }

        response = client.post("/users/", json=incomplete_user, headers=auth_headers["admin"])

        assert response.status_code == 422  # Validation error

    def test_update_user_admin(self, client, test_users, auth_headers):
        """Test admin can update users."""
        user_id = test_users["dev"].id
        update_data = {
            "full_name": "Updated Developer",
            "role": "ScrumMaster"
        }

        response = client.put(f"/users/{user_id}", json=update_data, headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Developer"
        assert data["role"] == "ScrumMaster"

    def test_update_user_scrum_master(self, client, test_users, auth_headers):
        """Test scrum master can update users but not change roles."""
        user_id = test_users["dev"].id
        update_data = {
            "full_name": "Scrum Updated Developer"
        }

        response = client.put(f"/users/{user_id}", json=update_data, headers=auth_headers["scrum"])

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Scrum Updated Developer"

        # Scrum master cannot change user roles
        update_data_with_role = {
            "full_name": "Role Change Attempt",
            "role": "Admin"
        }
        response = client.put(f"/users/{user_id}", json=update_data_with_role, headers=auth_headers["scrum"])
        assert response.status_code == 403

    def test_update_user_developer_forbidden(self, client, test_users, auth_headers):
        """Test developer cannot update other users but can update themselves."""
        # Developer cannot update other users
        user_id = test_users["admin"].id
        update_data = {
            "full_name": "Forbidden Update"
        }

        response = client.put(f"/users/{user_id}", json=update_data, headers=auth_headers["dev"])
        assert response.status_code == 403
        assert "Developers can only update their own account" in response.json()["detail"]

        # Developer can update their own account (email and password only)
        dev_user_id = test_users["dev"].id
        update_data = {
            "email": "newemail@test.com",
            "password": "newpassword123"
        }

        response = client.put(f"/users/{dev_user_id}", json=update_data, headers=auth_headers["dev"])
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newemail@test.com"

        # After email update, create a new token since old tokens are revoked for security
        from app.core.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, token_blacklist
        import time

        # Update the user object with new email for token creation
        test_users['dev'].email = "newemail@test.com"
        new_token = create_access_token(data={"sub": str(test_users['dev'].id), "email": test_users['dev'].email})
        expires_at = time.time() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        token_blacklist.track_token(new_token, test_users['dev'].id, expires_at)
        new_dev_headers = {"Authorization": f"Bearer {new_token}"}

        # Developer cannot update other fields like full_name
        update_data_forbidden = {
            "full_name": "New Full Name"
        }
        response = client.put(f"/users/{dev_user_id}", json=update_data_forbidden, headers=new_dev_headers)
        print(f"### Response: {response.json()}")
        assert response.status_code == 403
        assert "Developers can only update email and password" in response.json()["detail"]

    def test_update_user_nonexistent(self, client, auth_headers):
        """Test updating non-existent user."""
        update_data = {
            "full_name": "Non-existent User"
        }

        response = client.put("/users/99999", json=update_data, headers=auth_headers["admin"])

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_update_user_duplicate_email(self, client, test_users, auth_headers):
        """Test cannot update user with duplicate email."""
        user_id = test_users["dev"].id
        update_data = {
            "email": "admin@test.com"  # Already exists
        }

        response = client.put(f"/users/{user_id}", json=update_data, headers=auth_headers["admin"])

        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_delete_user_admin(self, client, test_users, auth_headers):
        """Test admin can delete users."""
        user_id = test_users["dev"].id

        response = client.delete(f"/users/{user_id}", headers=auth_headers["admin"])

        assert response.status_code == 204

        # Verify user is deleted
        response = client.get(f"/users/{user_id}", headers=auth_headers["admin"])
        assert response.status_code == 404

    def test_delete_user_scrum_master_forbidden(self, client, test_users, auth_headers):
        """Test scrum master cannot delete users."""
        user_id = test_users["dev"].id

        response = client.delete(f"/users/{user_id}", headers=auth_headers["scrum"])

        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

    def test_delete_user_developer_forbidden(self, client, test_users, auth_headers):
        """Test developer cannot delete users."""
        user_id = test_users["admin"].id

        response = client.delete(f"/users/{user_id}", headers=auth_headers["dev"])

        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

    def test_delete_nonexistent_user(self, client, auth_headers):
        """Test deleting non-existent user."""
        response = client.delete("/users/99999", headers=auth_headers["admin"])

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]


class TestUserValidation:
    """Test user validation rules."""

    def test_valid_user_roles(self, client, auth_headers):
        """Test all valid user roles."""
        for role in ["Admin", "ScrumMaster", "Developer"]:
            user_data = {
                "email": f"new_{role.lower()}@test.com",  # Use unique email addresses
                "full_name": f"Test {role}",
                "password": "Password123!",
                "role": role
            }

            response = client.post("/users/", json=user_data, headers=auth_headers["admin"])
            assert response.status_code == 201
            assert response.json()["role"] == role

    def test_password_requirements(self, client, auth_headers):
        """Test password requirements are enforced."""
        # Test empty password
        user_data = {
            "email": "test@test.com",
            "full_name": "Test User",
            "password": "",
            "role": "Developer"
        }

        response = client.post("/users/", json=user_data, headers=auth_headers["admin"])
        assert response.status_code == 422  # Validation error

        # Test short password
        user_data["password"] = "123"
        response = client.post("/users/", json=user_data, headers=auth_headers["admin"])
        assert response.status_code == 422  # Validation error

    def test_email_format_validation(self, client, auth_headers):
        """Test email format validation."""
        invalid_emails = [
            "not-an-email",
            "@test.com",
            "test@",
            "test.com",
            "test@.com",
            "test@com.",
        ]

        for email in invalid_emails:
            user_data = {
                "email": email,
                "full_name": "Test User",
                "password": "Password123!",
                "role": "Developer"
            }

            response = client.post("/users/", json=user_data, headers=auth_headers["admin"])
            assert response.status_code == 422  # Validation error

    def test_full_name_requirements(self, client, auth_headers):
        """Test full name requirements."""
        # Test empty full name
        user_data = {
            "email": "test@test.com",
            "full_name": "",
            "password": "Password123!",
            "role": "Developer"
        }

        response = client.post("/users/", json=user_data, headers=auth_headers["admin"])
        assert response.status_code == 422  # Validation error

        # Test very long full name
        user_data["full_name"] = "A" * 256
        response = client.post("/users/", json=user_data, headers=auth_headers["admin"])
        assert response.status_code == 422  # Validation error


class TestUserFiltering:
    """Test user filtering and querying."""

    def test_active_users_only(self, client, test_users, auth_headers):
        """Test that only active users are returned by default."""
        response = client.get("/users/", headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()

        # Should return only active users (admin, scrum, dev)
        assert len(data) == 3
        for user in data:
            assert user["is_active"] is True

    def test_user_by_role(self, client, test_users, auth_headers):
        """Test filtering users by role."""
        response = client.get("/users/", headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()

        # Count users by role
        admin_users = [u for u in data if u["role"] == "Admin"]
        scrum_users = [u for u in data if u["role"] == "ScrumMaster"]
        dev_users = [u for u in data if u["role"] == "Developer"]

        assert len(admin_users) == 1
        assert len(scrum_users) == 1
        assert len(dev_users) == 1
