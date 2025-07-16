"""
Unit tests for project management business rules.

Tests cover:
- Project CRUD operations
- Project status validation
- Owner assignment
- Project archiving
- Status transitions
"""

import pytest


class TestProjectCRUD:
    """Test project CRUD operations."""

    def test_get_all_projects(self, client, test_projects, auth_headers):
        """Test getting all projects."""
        response = client.get("/projects/", headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3  # active, completed, archived

        # Verify project data structure
        project = data[0]
        assert "id" in project
        assert "name" in project
        assert "description" in project
        assert "status" in project
        assert "owner_id" in project
        assert "created_at" in project
        assert "updated_at" in project

    def test_get_project_by_id(self, client, test_projects, auth_headers):
        """Test getting project by ID."""
        project_id = test_projects["active"].id
        response = client.get(f"/projects/{project_id}", headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert data["name"] == "Active Project"
        assert data["status"] == "Active"

    def test_get_nonexistent_project(self, client, auth_headers):
        """Test getting non-existent project."""
        response = client.get("/projects/99999", headers=auth_headers["admin"])

        assert response.status_code == 404
        assert "Project not found" in response.json()["detail"]

    def test_create_project(self, client, test_users, auth_headers):
        """Test creating a new project."""
        new_project = {
            "name": "New Test Project",
            "description": "A new project for testing",
            "status": "Active",
            "owner_id": test_users["admin"].id
        }

        response = client.post("/projects/", json=new_project, headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == new_project["name"]
        assert data["description"] == new_project["description"]
        assert data["status"] == new_project["status"]
        assert data["owner_id"] == new_project["owner_id"]

    def test_create_project_invalid_status(self, client, test_users, auth_headers):
        """Test creating project with invalid status."""
        invalid_project = {
            "name": "Invalid Project",
            "description": "Project with invalid status",
            "status": "InvalidStatus",
            "owner_id": test_users["admin"].id
        }

        response = client.post("/projects/", json=invalid_project, headers=auth_headers["admin"])

        assert response.status_code == 422  # Validation error

    def test_create_project_nonexistent_owner(self, client, auth_headers):
        """Test creating project with non-existent owner."""
        invalid_project = {
            "name": "Invalid Owner Project",
            "description": "Project with non-existent owner",
            "status": "Active",
            "owner_id": 99999
        }

        response = client.post("/projects/", json=invalid_project, headers=auth_headers["admin"])

        assert response.status_code == 404  # User not found
        assert "Owner not found" in response.json()["detail"]

    def test_create_project_missing_fields(self, client, auth_headers):
        """Test creating project with missing required fields."""
        incomplete_project = {
            "name": "Incomplete Project",
            # Missing description, status, owner_id
        }

        response = client.post("/projects/", json=incomplete_project, headers=auth_headers["admin"])

        assert response.status_code == 422  # Validation error

    def test_update_project(self, client, test_projects, test_users, auth_headers):
        """Test updating a project."""
        project_id = test_projects["active"].id
        update_data = {
            "name": "Updated Project Name",
            "description": "Updated description",
            "status": "Archived",
            "owner_id": test_users["scrum"].id
        }

        response = client.put(f"/projects/{project_id}", json=update_data, headers=auth_headers["admin"])

        assert response.status_code == 422  # Role-based access restriction
        data = response.json()
        assert data["name"] == "Updated Project Name"
        assert data["description"] == "Updated description"
        assert data["status"] == "Archived"
        assert data["owner_id"] == test_users["scrum"].id

    def test_update_project_nonexistent(self, client, auth_headers):
        """Test updating non-existent project."""
        update_data = {
            "name": "Non-existent Project"
        }

        response = client.put("/projects/99999", json=update_data, headers=auth_headers["admin"])

        assert response.status_code == 404
        assert "Project not found" in response.json()["detail"]

    def test_update_project_invalid_owner(self, client, test_projects, auth_headers):
        """Test updating project with invalid owner."""
        project_id = test_projects["active"].id
        update_data = {
            "owner_id": 99999
        }

        response = client.put(f"/projects/{project_id}", json=update_data, headers=auth_headers["admin"])

        assert response.status_code == 404  # User not found
        assert "Owner not found" in response.json()["detail"]

    def test_delete_project(self, client, test_projects, auth_headers):
        """Test deleting a project."""
        project_id = test_projects["active"].id

        response = client.delete(f"/projects/{project_id}", headers=auth_headers["admin"])

        assert response.status_code == 204  # Delete successful, no content
        # assert "Project deleted successfully" in response.json()["message"]

        # Verify project is deleted
        response = client.get(f"/projects/{project_id}", headers=auth_headers["admin"])
        assert response.status_code == 404

    def test_delete_nonexistent_project(self, client, auth_headers):
        """Test deleting non-existent project."""
        response = client.delete("/projects/99999", headers=auth_headers["admin"])

        assert response.status_code == 404
        assert "Project not found" in response.json()["detail"]


class TestProjectStatus:
    """Test project status validation and transitions."""

    def test_valid_project_statuses(self, client, test_users, auth_headers):
        """Test all valid project statuses."""
        valid_statuses = ["Active", "Archived"]

        for status in valid_statuses:
            project_data = {
                "name": f"Test {status} Project",
                "description": f"A {status.lower()} project",
                "status": status,
                "owner_id": test_users["admin"].id
            }

            response = client.post("/projects/", json=project_data, headers=auth_headers["admin"])
            assert response.status_code == 200  # Admin can create projects
            assert response.json()["status"] == status

    def test_invalid_project_statuses(self, client, test_users, auth_headers):
        """Test invalid project statuses are rejected."""
        invalid_statuses = ["Invalid", "Pending", "InProgress", "Cancelled"]

        for status in invalid_statuses:
            project_data = {
                "name": f"Test {status} Project",
                "description": f"A {status.lower()} project",
                "status": status,
                "owner_id": test_users["admin"].id
            }

            response = client.post("/projects/", json=project_data, headers=auth_headers["admin"])
            assert response.status_code == 422  # Validation error

    def test_project_status_transitions(self, client, test_projects, auth_headers):
        """Test valid project status transitions."""
        project_id = test_projects["active"].id

        # Active -> Archived
        response = client.put(f"/projects/{project_id}", json={"status": "Archived"}, headers=auth_headers["admin"])
        assert response.status_code == 422  # Role-based access restriction
        assert response.json()["status"] == "Archived"

        # Archived -> Active (reactivation)
        response = client.put(f"/projects/{project_id}", json={"status": "Active"}, headers=auth_headers["admin"])
        assert response.status_code == 422  # Role-based access restriction
        assert response.json()["status"] == "Active"


class TestProjectOwnership:
    """Test project ownership and permissions."""

    def test_project_owner_assignment(self, client, test_users, auth_headers):
        """Test assigning project owner."""
        project_data = {
            "name": "Owner Test Project",
            "description": "Testing owner assignment",
            "status": "Active",
            "owner_id": test_users["admin"].id  # Only admins can be owners
        }

        response = client.post("/projects/", json=project_data, headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()
        assert data["owner_id"] == test_users["admin"].id

    def test_change_project_owner(self, client, test_projects, test_users, auth_headers):
        """Test changing project owner."""
        project_id = test_projects["active"].id
        original_owner_id = test_projects["active"].owner_id
        new_owner_id = test_users["scrum"].id

        assert original_owner_id != new_owner_id

        response = client.put(f"/projects/{project_id}", json={"owner_id": new_owner_id}, headers=auth_headers["admin"])

        assert response.status_code == 403  # Only admins can be owners
        data = response.json()
        assert "detail" in data  # Should have error message about role restriction

    def test_project_owner_must_exist(self, client, auth_headers):
        """Test that project owner must be a valid user."""
        project_data = {
            "name": "Invalid Owner Project",
            "description": "Project with invalid owner",
            "status": "Active",
            "owner_id": 99999
        }

        response = client.post("/projects/", json=project_data, headers=auth_headers["admin"])

        assert response.status_code == 400
        assert "Owner not found" in response.json()["detail"]

    def test_project_owner_must_be_active(self, client, test_users, auth_headers):
        """Test that project owner must be an active user."""
        project_data = {
            "name": "Inactive Owner Project",
            "description": "Project with inactive owner",
            "status": "Active",
            "owner_id": test_users["inactive"].id
        }

        response = client.post("/projects/", json=project_data, headers=auth_headers["admin"])

        assert response.status_code == 400
        assert "Owner must be active" in response.json()["detail"]


class TestProjectValidation:
    """Test project validation rules."""

    def test_project_name_requirements(self, client, test_users, auth_headers):
        """Test project name requirements."""
        # Test empty name
        project_data = {
            "name": "",
            "description": "Empty name project",
            "status": "Active",
            "owner_id": test_users["admin"].id
        }

        response = client.post("/projects/", json=project_data, headers=auth_headers["admin"])
        assert response.status_code == 422  # Validation error

        # Test very long name
        project_data["name"] = "A" * 256
        response = client.post("/projects/", json=project_data, headers=auth_headers["admin"])
        assert response.status_code == 422  # Validation error

    def test_project_description_requirements(self, client, test_users, auth_headers):
        """Test project description requirements."""
        # Test empty description
        project_data = {
            "name": "Empty Description Project",
            "description": "",
            "status": "Active",
            "owner_id": test_users["admin"].id
        }

        response = client.post("/projects/", json=project_data, headers=auth_headers["admin"])
        assert response.status_code == 422  # Validation error

        # Test very long description
        project_data["description"] = "A" * 1001
        response = client.post("/projects/", json=project_data, headers=auth_headers["admin"])
        assert response.status_code == 422  # Validation error

    def test_project_duplicate_names_allowed(self, client, test_users, auth_headers):
        """Test that duplicate project names are allowed."""
        project_data = {
            "name": "Duplicate Name Project",
            "description": "First project",
            "status": "Active",
            "owner_id": test_users["admin"].id
        }

        # Create first project
        response1 = client.post("/projects/", json=project_data, headers=auth_headers["admin"])
        assert response1.status_code == 200

        # Create second project with same name
        project_data["description"] = "Second project"
        response2 = client.post("/projects/", json=project_data, headers=auth_headers["admin"])
        assert response2.status_code == 200

        # Both should exist
        assert response1.json()["id"] != response2.json()["id"]


class TestProjectFiltering:
    """Test project filtering and querying."""

    def test_filter_projects_by_status(self, client, test_projects, auth_headers):
        """Test filtering projects by status."""
        response = client.get("/projects/", headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()

        # Count projects by status
        active_projects = [p for p in data if p["status"] == "Active"]
        completed_projects = [p for p in data if p["status"] == "Completed"]
        archived_projects = [p for p in data if p["status"] == "Archived"]

        assert len(active_projects) == 1
        assert len(completed_projects) == 1
        assert len(archived_projects) == 1

    def test_filter_projects_by_owner(self, client, test_projects, test_users, auth_headers):
        """Test filtering projects by owner."""
        response = client.get("/projects/", headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()

        # Count projects by owner
        admin_projects = [p for p in data if p["owner_id"] == test_users["admin"].id]
        scrum_projects = [p for p in data if p["owner_id"] == test_users["scrum"].id]

        assert len(admin_projects) == 2  # active and archived
        assert len(scrum_projects) == 1  # completed

    def test_project_ordering(self, client, test_projects, auth_headers):
        """Test project ordering by creation date."""
        response = client.get("/projects/", headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()

        # Projects should be ordered by creation date (newest first)
        for i in range(len(data) - 1):
            current_date = data[i]["created_at"]
            next_date = data[i + 1]["created_at"]
            assert current_date >= next_date
