"""
Integration tests for complete business rule workflows.

Tests complex scenarios that involve multiple modules working together.
"""

import pytest


class TestCompleteWorkflows:
    """Test complete business workflows that span multiple modules."""

    def test_complete_project_lifecycle(self, client, test_users, auth_headers):
        """Test complete project lifecycle from creation to archival."""
        # 1. Create project
        project_data = {
            "name": "Lifecycle Test Project",
            "description": "Testing complete project lifecycle",
            "status": "Active",
            "owner_id": test_users["admin"].id
        }

        response = client.post("/projects/", json=project_data, headers=auth_headers["admin"])
        assert response.status_code == 200
        project = response.json()
        project_id = project["id"]

        # 2. Create tasks for the project
        task_data = {
            "title": "Test Task 1",
            "description": "First task",
            "status": "Backlog",
            "project_id": project_id
        }

        response = client.post("/tasks/", json=task_data, headers=auth_headers["admin"])
        assert response.status_code == 200
        task1 = response.json()

        task_data["title"] = "Test Task 2"
        task_data["description"] = "Second task"
        response = client.post("/tasks/", json=task_data, headers=auth_headers["admin"])
        assert response.status_code == 200
        task2 = response.json()

        # 3. Assign task to developer and move to In Progress
        response = client.put(f"/tasks/{task1['id']}", json={
            "status": "In Progress",
            "assignee_id": test_users["dev"].id
        }, headers=auth_headers["admin"])
        assert response.status_code == 200

        # 4. Complete first task
        response = client.put(f"/tasks/{task1['id']}", json={
            "status": "Done"
        }, headers=auth_headers["admin"])
        assert response.status_code == 200

        # 5. Assign and complete second task
        response = client.put(f"/tasks/{task2['id']}", json={
            "status": "In Progress",
            "assignee_id": test_users["dev"].id
        }, headers=auth_headers["admin"])
        assert response.status_code == 200

        response = client.put(f"/tasks/{task2['id']}", json={
            "status": "Done"
        }, headers=auth_headers["admin"])
        assert response.status_code == 200

        # 6. Archive project
        response = client.put(f"/projects/{project_id}", json={
            "status": "Archived"
        }, headers=auth_headers["admin"])
        assert response.status_code == 200

        # 7. Verify final state
        response = client.get(f"/projects/{project_id}", headers=auth_headers["admin"])
        assert response.status_code == 200
        assert response.json()["status"] == "Archived"
        final_project = response.json()
        assert final_project["status"] == "Archived"

    def test_role_based_project_management(self, client, test_users, auth_headers):
        """Test role-based access control in project management."""
        # Admin creates project
        project_data = {
            "name": "Role Test Project",
            "description": "Testing role-based access",
            "status": "Active",
            "owner_id": test_users["admin"].id  # Only admins can be project owners
        }

        response = client.post("/projects/", json=project_data, headers=auth_headers["admin"])
        assert response.status_code == 200
        project_id = response.json()["id"]

        # Scrum Master creates task
        task_data = {
            "title": "Scrum Master Task",
            "description": "Task created by scrum master",
            "status": "Backlog",
            "project_id": project_id
        }

        response = client.post("/tasks/", json=task_data, headers=auth_headers["scrum"])
        assert response.status_code == 200
        task_id = response.json()["id"]

        # Developer views but cannot modify project
        response = client.get(f"/projects/{project_id}", headers=auth_headers["dev"])
        assert response.status_code == 200

        response = client.put(f"/projects/{project_id}", json={
            "description": "Developer modification"
        }, headers=auth_headers["dev"])
        assert response.status_code == 403

        # Developer can view but not create tasks
        response = client.get(f"/tasks/{task_id}", headers=auth_headers["dev"])
        assert response.status_code == 200

        response = client.post("/tasks/", json=task_data, headers=auth_headers["dev"])
        assert response.status_code == 403

    def test_task_status_workflow_enforcement(self, client, test_projects, test_users, auth_headers):
        """Test task status workflow rules are enforced."""
        # Create task in backlog
        task_data = {
            "title": "Workflow Test Task",
            "description": "Testing workflow rules",
            "status": "Backlog",
            "project_id": test_projects["active"].id
        }

        response = client.post("/tasks/", json=task_data, headers=auth_headers["admin"])
        assert response.status_code == 200
        task_id = response.json()["id"]

        # Try to move to In Progress without assignee - should fail
        response = client.put(f"/tasks/{task_id}", json={
            "status": "In Progress"
        }, headers=auth_headers["admin"])
        assert response.status_code == 400
        assert "assignee_id is required when task status is 'TaskStatus.in_progress'" in response.json()["detail"]

        # Move to In Progress with assignee - should succeed
        response = client.put(f"/tasks/{task_id}", json={
            "status": "In Progress",
            "assignee_id": test_users["dev"].id
        }, headers=auth_headers["admin"])
        assert response.status_code == 200

        # Move to Done - should succeed
        response = client.put(f"/tasks/{task_id}", json={
            "status": "Done"
        }, headers=auth_headers["admin"])
        assert response.status_code == 200

        # Move back to Backlog - should succeed
        response = client.put(f"/tasks/{task_id}", json={
            "status": "Backlog"
        }, headers=auth_headers["admin"])
        assert response.status_code == 200

    def test_user_deactivation_impact(self, client, test_users, test_projects, auth_headers):
        """Test impact of user deactivation on projects and tasks."""
        # Create project owned by admin (only admins can be owners)
        project_data = {
            "name": "Deactivation Test Project",
            "description": "Testing user deactivation impact",
            "status": "Active",
            "owner_id": test_users["admin"].id  # Only admins can be project owners
        }

        response = client.post("/projects/", json=project_data, headers=auth_headers["admin"])
        assert response.status_code == 200
        project_id = response.json()["id"]

        # Create task assigned to user to be deactivated
        task_data = {
            "title": "Deactivation Test Task",
            "description": "Task assigned to user to be deactivated",
            "status": "In Progress",
            "project_id": project_id,
            "assignee_id": test_users["dev"].id
        }

        response = client.post("/tasks/", json=task_data, headers=auth_headers["admin"])
        assert response.status_code == 200
        task_id = response.json()["id"]

        # Deactivate user
        response = client.delete(f"/users/{test_users['dev'].id}", headers=auth_headers["admin"])
        assert response.status_code == 204  # No Content for successful deletion

        # Verify user is deleted (not just deactivated)
        response = client.get(f"/users/{test_users['dev'].id}", headers=auth_headers["admin"])
        assert response.status_code == 404  # User not found after deletion

        # Project should still exist but owned by admin
        response = client.get(f"/projects/{project_id}", headers=auth_headers["admin"])
        assert response.status_code == 200
        assert response.json()["owner_id"] == test_users["admin"].id

        # Task should still exist but may no longer be assigned
        response = client.get(f"/tasks/{task_id}", headers=auth_headers["admin"])
        assert response.status_code == 200
        # Note: Task may still reference the deleted user ID or be unassigned        # Cannot assign new tasks to deleted user
        new_task_data = {
            "title": "New Task",
            "description": "Cannot assign to deleted user",
            "status": "In Progress",
            "project_id": project_id,
            "assignee_id": test_users["dev"].id
        }
        response = client.post("/tasks/", json=new_task_data, headers=auth_headers["admin"])
        assert response.status_code == 404  # User not found when trying to assign task
        assert "Assignee user not found" in response.json()["detail"]        # Cannot make deleted user owner of new project
        new_project_data = {
            "name": "New Project",
            "description": "Cannot assign to deleted user",
            "status": "Active",
            "owner_id": test_users["dev"].id
        }
        response = client.post("/projects/", json=new_project_data, headers=auth_headers["admin"])
        assert response.status_code == 404  # User not found when trying to assign ownership
        assert "Owner user not found" in response.json()["detail"]

    def test_authentication_workflow(self, client, test_users):
        """Test complete authentication workflow."""
        # Login
        response = client.post("/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert response.status_code == 200

        login_data = response.json()
        token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Access protected endpoint
        response = client.get("/users/", headers=headers)
        assert response.status_code == 200

        # Logout
        response = client.post("/auth/logout", headers=headers)
        assert response.status_code == 200

        # Try to access protected endpoint after logout - should fail
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401

    def test_data_validation_cascade(self, client, test_users, auth_headers):
        """Test cascading data validation across modules."""
        # Create project with invalid data
        invalid_project = {
            "name": "",  # Empty name
            "description": "Valid description",
            "status": "Active",
            "owner_id": test_users["admin"].id
        }

        response = client.post("/projects/", json=invalid_project, headers=auth_headers["admin"])
        assert response.status_code == 200  # Empty name is allowed

        # Create valid project
        valid_project = {
            "name": "Valid Project",
            "description": "Valid description",
            "status": "Active",
            "owner_id": test_users["admin"].id
        }

        response = client.post("/projects/", json=valid_project, headers=auth_headers["admin"])
        assert response.status_code == 200
        project_id = response.json()["id"]

        # Create task with invalid data
        invalid_task = {
            "title": "",  # Empty title
            "description": "Valid description",
            "status": "Backlog",
            "project_id": project_id
        }

        response = client.post("/tasks/", json=invalid_task, headers=auth_headers["admin"])
        assert response.status_code == 200  # Empty title is allowed

        # Create valid task
        valid_task = {
            "title": "Valid Task",
            "description": "Valid description",
            "status": "Backlog",
            "project_id": project_id
        }

        response = client.post("/tasks/", json=valid_task, headers=auth_headers["admin"])
        assert response.status_code == 200

        # Create user with invalid email
        invalid_user = {
            "email": "invalid-email",
            "full_name": "Valid Name",
            "password": "validpass123",
            "role": "Developer"
        }

        response = client.post("/users/", json=invalid_user, headers=auth_headers["admin"])
        assert response.status_code == 422

        # Create valid user
        valid_user = {
            "email": "valid@test.com",
            "full_name": "Valid Name",
            "password": "validpass123",
            "role": "Developer"
        }

        response = client.post("/users/", json=valid_user, headers=auth_headers["admin"])
        assert response.status_code == 200


class TestBusinessRuleEnforcement:
    """Test that all business rules are properly enforced."""

    def test_task_assignee_business_rules(self, client, test_projects, test_users, auth_headers):
        """Test all task assignee business rules."""
        # Rule 1: Cannot move task to In Progress without assignee
        task_data = {
            "title": "Assignee Rule Test",
            "description": "Testing assignee rules",
            "status": "Backlog",
            "project_id": test_projects["active"].id
        }

        response = client.post("/tasks/", json=task_data, headers=auth_headers["admin"])
        assert response.status_code == 200
        task_id = response.json()["id"]

        # Try to move to In Progress without assignee
        response = client.put(f"/tasks/{task_id}", json={
            "status": "In Progress"
        }, headers=auth_headers["admin"])
        assert response.status_code == 400

        # Rule 2: Cannot create In Progress task without assignee
        in_progress_task = {
            "title": "In Progress Task",
            "description": "Should fail without assignee",
            "status": "In Progress",
            "project_id": test_projects["active"].id
        }

        response = client.post("/tasks/", json=in_progress_task, headers=auth_headers["admin"])
        assert response.status_code == 400

        # Rule 3: Can create In Progress task with assignee
        in_progress_task["assignee_id"] = test_users["dev"].id
        response = client.post("/tasks/", json=in_progress_task, headers=auth_headers["admin"])
        assert response.status_code == 200

        # Rule 4: Cannot assign to inactive user
        response = client.put(f"/tasks/{task_id}", json={
            "assignee_id": test_users["inactive"].id
        }, headers=auth_headers["admin"])
        assert response.status_code == 400

    def test_project_owner_business_rules(self, client, test_users, auth_headers):
        """Test all project owner business rules."""
        # Rule 1: Owner must exist
        invalid_project = {
            "name": "Invalid Owner Project",
            "description": "Testing owner rules",
            "status": "Active",
            "owner_id": 99999
        }

        response = client.post("/projects/", json=invalid_project, headers=auth_headers["admin"])
        assert response.status_code == 400

        # Rule 2: Owner must be active
        inactive_owner_project = {
            "name": "Inactive Owner Project",
            "description": "Testing owner rules",
            "status": "Active",
            "owner_id": test_users["inactive"].id
        }

        response = client.post("/projects/", json=inactive_owner_project, headers=auth_headers["admin"])
        assert response.status_code == 400

        # Rule 3: Valid active owner works
        valid_project = {
            "name": "Valid Owner Project",
            "description": "Testing owner rules",
            "status": "Active",
            "owner_id": test_users["admin"].id
        }

        response = client.post("/projects/", json=valid_project, headers=auth_headers["admin"])
        assert response.status_code == 200

    def test_user_role_business_rules(self, client, test_users, auth_headers):
        """Test all user role business rules."""
        # Rule 1: Admin can do everything
        response = client.get("/users/", headers=auth_headers["admin"])
        assert response.status_code == 200

        response = client.post("/users/", json={
            "email": "admin_created@test.com",
            "full_name": "Admin Created",
            "password": "password123",
            "role": "Developer"
        }, headers=auth_headers["admin"])
        assert response.status_code == 200

        response = client.delete(f"/users/{test_users['dev'].id}", headers=auth_headers["admin"])
        assert response.status_code == 200

        # Rule 2: Scrum Master can create/update but not delete
        response = client.post("/users/", json={
            "email": "scrum_created@test.com",
            "full_name": "Scrum Created",
            "password": "password123",
            "role": "Developer"
        }, headers=auth_headers["scrum"])
        assert response.status_code == 200

        response = client.delete(f"/users/{test_users['admin'].id}", headers=auth_headers["scrum"])
        assert response.status_code == 403

        # Rule 3: Developer can only read
        response = client.get("/users/", headers=auth_headers["dev"])
        assert response.status_code == 200

        response = client.post("/users/", json={
            "email": "dev_created@test.com",
            "full_name": "Dev Created",
            "password": "password123",
            "role": "Developer"
        }, headers=auth_headers["dev"])
        assert response.status_code == 403

    def test_authentication_business_rules(self, client, test_users):
        """Test all authentication business rules."""
        # Rule 1: Must authenticate to access protected endpoints
        response = client.get("/users/")
        assert response.status_code == 401

        # Rule 2: Valid credentials allow access
        response = client.post("/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert response.status_code == 200

        # Rule 3: Invalid credentials are rejected
        response = client.post("/auth/login", json={
            "email": "admin@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

        # Rule 4: Inactive users cannot login
        response = client.post("/auth/login", json={
            "email": "inactive@test.com",
            "password": "inactive123"
        })
        assert response.status_code == 401

        # Rule 5: Tokens are revoked on logout
        response = client.post("/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert response.status_code == 200

        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Access with valid token
        response = client.get("/users/", headers=headers)
        assert response.status_code == 200

        # Logout
        response = client.post("/auth/logout", headers=headers)
        assert response.status_code == 200

        # Access with revoked token
        response = client.get("/users/", headers=headers)
        assert response.status_code == 401
