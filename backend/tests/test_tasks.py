"""
Unit tests for task management business rules.

Tests cover:
- Task CRUD operations
- Task status validation and transitions
- Assignee requirements
- Task-project relationships
- Status workflow rules (Backlog->In Progress requires assignee)
"""

import pytest


class TestTaskCRUD:
    """Test task CRUD operations."""

    def test_get_all_tasks(self, client, test_tasks, auth_headers):
        """Test getting all tasks."""
        response = client.get("/tasks/", headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3  # backlog, in_progress, done

        # Verify task data structure
        task = data[0]
        assert "id" in task
        assert "title" in task
        assert "description" in task
        assert "status" in task
        assert "project_id" in task
        assert "assigned_to" in task
        assert "created_at" in task
        assert "updated_at" in task

    def test_get_task_by_id(self, client, test_tasks, auth_headers):
        """Test getting task by ID."""
        task_id = test_tasks["backlog"].id
        response = client.get(f"/tasks/{task_id}", headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Backlog Task"
        assert data["status"] == "Backlog"

    def test_get_nonexistent_task(self, client, auth_headers):
        """Test getting non-existent task."""
        response = client.get("/tasks/99999", headers=auth_headers["admin"])

        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]

    def test_create_task(self, client, test_projects, auth_headers):
        """Test creating a new task."""
        new_task = {
            "title": "New Test Task",
            "description": "A new task for testing",
            "status": "Backlog",
            "project_id": test_projects["active"].id
        }

        response = client.post("/tasks/", json=new_task, headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == new_task["title"]
        assert data["description"] == new_task["description"]
        assert data["status"] == new_task["status"]
        assert data["project_id"] == new_task["project_id"]
        assert data["assigned_to"] is None  # No assignee by default

    def test_create_task_with_assignee(self, client, test_projects, test_users, auth_headers):
        """Test creating a task with assignee."""
        new_task = {
            "title": "Assigned Task",
            "description": "A task with assignee",
            "status": "In Progress",
            "project_id": test_projects["active"].id,
            "assigned_to": test_users["dev"].id
        }

        response = client.post("/tasks/", json=new_task, headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()
        assert data["assigned_to"] == test_users["dev"].id

    def test_create_task_invalid_status(self, client, test_projects, auth_headers):
        """Test creating task with invalid status."""
        invalid_task = {
            "title": "Invalid Task",
            "description": "Task with invalid status",
            "status": "InvalidStatus",
            "project_id": test_projects["active"].id
        }

        response = client.post("/tasks/", json=invalid_task, headers=auth_headers["admin"])

        assert response.status_code == 422  # Validation error

    def test_create_task_nonexistent_project(self, client, auth_headers):
        """Test creating task with non-existent project."""
        invalid_task = {
            "title": "Invalid Project Task",
            "description": "Task with non-existent project",
            "status": "Backlog",
            "project_id": 99999
        }

        response = client.post("/tasks/", json=invalid_task, headers=auth_headers["admin"])

        assert response.status_code == 400
        assert "Project not found" in response.json()["detail"]

    def test_create_task_nonexistent_assignee(self, client, test_projects, auth_headers):
        """Test creating task with non-existent assignee."""
        invalid_task = {
            "title": "Invalid Assignee Task",
            "description": "Task with non-existent assignee",
            "status": "In Progress",
            "project_id": test_projects["active"].id,
            "assigned_to": 99999
        }

        response = client.post("/tasks/", json=invalid_task, headers=auth_headers["admin"])

        assert response.status_code == 400
        assert "Assignee not found" in response.json()["detail"]

    def test_create_task_missing_fields(self, client, auth_headers):
        """Test creating task with missing required fields."""
        incomplete_task = {
            "title": "Incomplete Task",
            # Missing description, status, project_id
        }

        response = client.post("/tasks/", json=incomplete_task, headers=auth_headers["admin"])

        assert response.status_code == 422  # Validation error

    def test_update_task(self, client, test_tasks, test_users, auth_headers):
        """Test updating a task."""
        task_id = test_tasks["backlog"].id
        update_data = {
            "title": "Updated Task Title",
            "description": "Updated description",
            "status": "In Progress",
            "assigned_to": test_users["dev"].id
        }

        response = client.put(f"/tasks/{task_id}", json=update_data, headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task Title"
        assert data["description"] == "Updated description"
        assert data["status"] == "In Progress"
        assert data["assigned_to"] == test_users["dev"].id

    def test_update_task_nonexistent(self, client, auth_headers):
        """Test updating non-existent task."""
        update_data = {
            "title": "Non-existent Task"
        }

        response = client.put("/tasks/99999", json=update_data, headers=auth_headers["admin"])

        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]

    def test_update_task_invalid_assignee(self, client, test_tasks, auth_headers):
        """Test updating task with invalid assignee."""
        task_id = test_tasks["backlog"].id
        update_data = {
            "assigned_to": 99999
        }

        response = client.put(f"/tasks/{task_id}", json=update_data, headers=auth_headers["admin"])

        assert response.status_code == 400
        assert "Assignee not found" in response.json()["detail"]

    def test_delete_task(self, client, test_tasks, auth_headers):
        """Test deleting a task."""
        task_id = test_tasks["backlog"].id

        response = client.delete(f"/tasks/{task_id}", headers=auth_headers["admin"])

        assert response.status_code == 200
        assert "Task deleted successfully" in response.json()["message"]

        # Verify task is deleted
        response = client.get(f"/tasks/{task_id}", headers=auth_headers["admin"])
        assert response.status_code == 404

    def test_delete_nonexistent_task(self, client, auth_headers):
        """Test deleting non-existent task."""
        response = client.delete("/tasks/99999", headers=auth_headers["admin"])

        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]


class TestTaskStatus:
    """Test task status validation and transitions."""

    def test_valid_task_statuses(self, client, test_projects, auth_headers):
        """Test all valid task statuses."""
        valid_statuses = ["Backlog", "In Progress", "Done"]

        for status in valid_statuses:
            task_data = {
                "title": f"Test {status} Task",
                "description": f"A {status.lower()} task",
                "status": status,
                "project_id": test_projects["active"].id
            }

            # Add assignee for In Progress status
            if status == "In Progress":
                task_data["assigned_to"] = test_projects["active"].owner_id

            response = client.post("/tasks/", json=task_data, headers=auth_headers["admin"])
            assert response.status_code == 200
            assert response.json()["status"] == status

    def test_invalid_task_statuses(self, client, test_projects, auth_headers):
        """Test invalid task statuses are rejected."""
        invalid_statuses = ["Invalid", "Pending", "Completed", "Cancelled"]

        for status in invalid_statuses:
            task_data = {
                "title": f"Test {status} Task",
                "description": f"A {status.lower()} task",
                "status": status,
                "project_id": test_projects["active"].id
            }

            response = client.post("/tasks/", json=task_data, headers=auth_headers["admin"])
            assert response.status_code == 422  # Validation error

    def test_backlog_to_in_progress_requires_assignee(self, client, test_tasks, test_users, auth_headers):
        """Test that moving from Backlog to In Progress requires assignee."""
        task_id = test_tasks["backlog"].id

        # Try to move to In Progress without assignee - should fail
        response = client.put(f"/tasks/{task_id}", json={"status": "In Progress"}, headers=auth_headers["admin"])

        assert response.status_code == 400
        assert "Cannot move task to In Progress without assignee" in response.json()["detail"]

        # Move to In Progress with assignee - should succeed
        response = client.put(f"/tasks/{task_id}", json={
            "status": "In Progress",
            "assigned_to": test_users["dev"].id
        }, headers=auth_headers["admin"])

        assert response.status_code == 200
        assert response.json()["status"] == "In Progress"
        assert response.json()["assigned_to"] == test_users["dev"].id

    def test_in_progress_to_done_transition(self, client, test_tasks, auth_headers):
        """Test moving from In Progress to Done."""
        task_id = test_tasks["in_progress"].id

        response = client.put(f"/tasks/{task_id}", json={"status": "Done"}, headers=auth_headers["admin"])

        assert response.status_code == 200
        assert response.json()["status"] == "Done"

    def test_done_to_backlog_transition(self, client, test_tasks, auth_headers):
        """Test moving from Done back to Backlog."""
        task_id = test_tasks["done"].id

        # Should be able to move back to Backlog
        response = client.put(f"/tasks/{task_id}", json={"status": "Backlog"}, headers=auth_headers["admin"])

        assert response.status_code == 200
        assert response.json()["status"] == "Backlog"

    def test_backlog_to_done_direct_transition(self, client, test_tasks, auth_headers):
        """Test moving directly from Backlog to Done."""
        task_id = test_tasks["backlog"].id

        # Should be able to move directly to Done
        response = client.put(f"/tasks/{task_id}", json={"status": "Done"}, headers=auth_headers["admin"])

        assert response.status_code == 200
        assert response.json()["status"] == "Done"

    def test_create_in_progress_task_requires_assignee(self, client, test_projects, auth_headers):
        """Test creating In Progress task requires assignee."""
        # Try to create In Progress task without assignee - should fail
        task_data = {
            "title": "In Progress Task",
            "description": "Should fail without assignee",
            "status": "In Progress",
            "project_id": test_projects["active"].id
        }

        response = client.post("/tasks/", json=task_data, headers=auth_headers["admin"])

        assert response.status_code == 400
        assert "Cannot create task in In Progress status without assignee" in response.json()["detail"]


class TestTaskAssignment:
    """Test task assignment and ownership."""

    def test_assign_task_to_user(self, client, test_tasks, test_users, auth_headers):
        """Test assigning task to a user."""
        task_id = test_tasks["backlog"].id

        response = client.put(f"/tasks/{task_id}", json={
            "assigned_to": test_users["dev"].id
        }, headers=auth_headers["admin"])

        assert response.status_code == 200
        assert response.json()["assigned_to"] == test_users["dev"].id

    def test_reassign_task(self, client, test_tasks, test_users, auth_headers):
        """Test reassigning task to different user."""
        task_id = test_tasks["in_progress"].id
        original_assignee = test_tasks["in_progress"].assigned_to
        new_assignee = test_users["scrum"].id

        assert original_assignee != new_assignee

        response = client.put(f"/tasks/{task_id}", json={
            "assigned_to": new_assignee
        }, headers=auth_headers["admin"])

        assert response.status_code == 200
        assert response.json()["assigned_to"] == new_assignee

    def test_unassign_task(self, client, test_tasks, auth_headers):
        """Test unassigning task (removing assignee)."""
        task_id = test_tasks["in_progress"].id

        # First move to Backlog to allow unassignment
        response = client.put(f"/tasks/{task_id}", json={
            "status": "Backlog",
            "assigned_to": None
        }, headers=auth_headers["admin"])

        assert response.status_code == 200
        assert response.json()["assigned_to"] is None
        assert response.json()["status"] == "Backlog"

    def test_assign_to_nonexistent_user(self, client, test_tasks, auth_headers):
        """Test assigning task to non-existent user."""
        task_id = test_tasks["backlog"].id

        response = client.put(f"/tasks/{task_id}", json={
            "assigned_to": 99999
        }, headers=auth_headers["admin"])

        assert response.status_code == 400
        assert "Assignee not found" in response.json()["detail"]

    def test_assign_to_inactive_user(self, client, test_tasks, test_users, auth_headers):
        """Test assigning task to inactive user."""
        task_id = test_tasks["backlog"].id

        response = client.put(f"/tasks/{task_id}", json={
            "assigned_to": test_users["inactive"].id
        }, headers=auth_headers["admin"])

        assert response.status_code == 400
        assert "Cannot assign task to inactive user" in response.json()["detail"]


class TestTaskValidation:
    """Test task validation rules."""

    def test_task_title_requirements(self, client, test_projects, auth_headers):
        """Test task title requirements."""
        # Test empty title
        task_data = {
            "title": "",
            "description": "Empty title task",
            "status": "Backlog",
            "project_id": test_projects["active"].id
        }

        response = client.post("/tasks/", json=task_data, headers=auth_headers["admin"])
        assert response.status_code == 422  # Validation error

        # Test very long title
        task_data["title"] = "A" * 256
        response = client.post("/tasks/", json=task_data, headers=auth_headers["admin"])
        assert response.status_code == 422  # Validation error

    def test_task_description_requirements(self, client, test_projects, auth_headers):
        """Test task description requirements."""
        # Test empty description
        task_data = {
            "title": "Empty Description Task",
            "description": "",
            "status": "Backlog",
            "project_id": test_projects["active"].id
        }

        response = client.post("/tasks/", json=task_data, headers=auth_headers["admin"])
        assert response.status_code == 422  # Validation error

        # Test very long description
        task_data["description"] = "A" * 1001
        response = client.post("/tasks/", json=task_data, headers=auth_headers["admin"])
        assert response.status_code == 422  # Validation error

    def test_task_duplicate_titles_allowed(self, client, test_projects, auth_headers):
        """Test that duplicate task titles are allowed."""
        task_data = {
            "title": "Duplicate Title Task",
            "description": "First task",
            "status": "Backlog",
            "project_id": test_projects["active"].id
        }

        # Create first task
        response1 = client.post("/tasks/", json=task_data, headers=auth_headers["admin"])
        assert response1.status_code == 200

        # Create second task with same title
        task_data["description"] = "Second task"
        response2 = client.post("/tasks/", json=task_data, headers=auth_headers["admin"])
        assert response2.status_code == 200

        # Both should exist
        assert response1.json()["id"] != response2.json()["id"]


class TestTaskProjectRelationship:
    """Test task-project relationships."""

    def test_task_must_belong_to_project(self, client, auth_headers):
        """Test that task must belong to a valid project."""
        task_data = {
            "title": "Orphaned Task",
            "description": "Task without project",
            "status": "Backlog",
            "project_id": 99999
        }

        response = client.post("/tasks/", json=task_data, headers=auth_headers["admin"])

        assert response.status_code == 400
        assert "Project not found" in response.json()["detail"]

    def test_task_project_relationship(self, client, test_tasks, test_projects, auth_headers):
        """Test that task belongs to correct project."""
        task_id = test_tasks["backlog"].id
        expected_project_id = test_projects["active"].id

        response = client.get(f"/tasks/{task_id}", headers=auth_headers["admin"])

        assert response.status_code == 200
        assert response.json()["project_id"] == expected_project_id

    def test_change_task_project(self, client, test_tasks, test_projects, auth_headers):
        """Test changing task's project."""
        task_id = test_tasks["backlog"].id
        new_project_id = test_projects["completed"].id

        response = client.put(f"/tasks/{task_id}", json={
            "project_id": new_project_id
        }, headers=auth_headers["admin"])

        assert response.status_code == 200
        assert response.json()["project_id"] == new_project_id


class TestTaskFiltering:
    """Test task filtering and querying."""

    def test_filter_tasks_by_status(self, client, test_tasks, auth_headers):
        """Test filtering tasks by status."""
        response = client.get("/tasks/", headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()

        # Count tasks by status
        backlog_tasks = [t for t in data if t["status"] == "Backlog"]
        in_progress_tasks = [t for t in data if t["status"] == "In Progress"]
        done_tasks = [t for t in data if t["status"] == "Done"]

        assert len(backlog_tasks) == 1
        assert len(in_progress_tasks) == 1
        assert len(done_tasks) == 1

    def test_filter_tasks_by_project(self, client, test_tasks, test_projects, auth_headers):
        """Test filtering tasks by project."""
        response = client.get("/tasks/", headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()

        # All test tasks should belong to active project
        active_project_tasks = [t for t in data if t["project_id"] == test_projects["active"].id]
        assert len(active_project_tasks) == 3

    def test_filter_tasks_by_assignee(self, client, test_tasks, test_users, auth_headers):
        """Test filtering tasks by assignee."""
        response = client.get("/tasks/", headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()

        # Count tasks by assignee
        dev_tasks = [t for t in data if t["assigned_to"] == test_users["dev"].id]
        unassigned_tasks = [t for t in data if t["assigned_to"] is None]

        assert len(dev_tasks) == 2  # in_progress and done
        assert len(unassigned_tasks) == 1  # backlog

    def test_task_ordering(self, client, test_tasks, auth_headers):
        """Test task ordering by creation date."""
        response = client.get("/tasks/", headers=auth_headers["admin"])

        assert response.status_code == 200
        data = response.json()

        # Tasks should be ordered by creation date (newest first)
        for i in range(len(data) - 1):
            current_date = data[i]["created_at"]
            next_date = data[i + 1]["created_at"]
            assert current_date >= next_date
