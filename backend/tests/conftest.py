"""
Test configuration and fixtures for the test suite.
"""

import pytest
import asyncio
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Override DATABASE_URL for testing
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.main import app
from app.db.base import Base
from app.core.deps import get_db
from app.core.auth import get_password_hash, create_access_token, token_blacklist, ACCESS_TOKEN_EXPIRE_MINUTES
from app.db.models import User, Project, Task
from app.schemas.user import Role


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Create a test client for each test."""
    # Clear token blacklist for each test
    token_blacklist.clear()

    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function", autouse=True)
def clear_token_blacklist():
    """Clear the token blacklist before each test."""
    token_blacklist.clear()
    yield
    token_blacklist.clear()


@pytest.fixture(scope="function")
def db_session():
    """Create a database session for each test."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up all tables after each test
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def test_users(db_session):
    """Create test users with different roles."""
    users = {}

    # Admin user
    admin_user = User(
        email="admin@test.com",
        full_name="Admin User",
        password_hash=get_password_hash("admin123"),
        role=Role.Admin,
        is_active=True
    )
    db_session.add(admin_user)

    # Scrum Master user
    scrum_user = User(
        email="scrum@test.com",
        full_name="Scrum Master",
        password_hash=get_password_hash("scrum123"),
        role=Role.ScrumMaster,
        is_active=True
    )
    db_session.add(scrum_user)

    # Developer user
    dev_user = User(
        email="dev@test.com",
        full_name="Developer User",
        password_hash=get_password_hash("dev123"),
        role=Role.Developer,
        is_active=True
    )
    db_session.add(dev_user)

    # Inactive user
    inactive_user = User(
        email="inactive@test.com",
        full_name="Inactive User",
        password_hash=get_password_hash("inactive123"),
        role=Role.Developer,
        is_active=False
    )
    db_session.add(inactive_user)

    db_session.commit()
    db_session.refresh(admin_user)
    db_session.refresh(scrum_user)
    db_session.refresh(dev_user)
    db_session.refresh(inactive_user)

    users["admin"] = admin_user
    users["scrum"] = scrum_user
    users["dev"] = dev_user
    users["inactive"] = inactive_user

    return users


@pytest.fixture(scope="function")
def test_projects(db_session, test_users):
    """Create test projects."""
    projects = {}

    # Active project
    active_project = Project(
        name="Active Project",
        description="An active project",
        status="Active",
        owner_id=test_users["admin"].id
    )
    db_session.add(active_project)

    # Completed project
    completed_project = Project(
        name="Completed Project",
        description="A completed project",
        status="Active",
        owner_id=test_users["scrum"].id
    )
    db_session.add(completed_project)

    # Archived project
    archived_project = Project(
        name="Archived Project",
        description="An archived project",
        status="Archived",
        owner_id=test_users["admin"].id
    )
    db_session.add(archived_project)

    db_session.commit()
    db_session.refresh(active_project)
    db_session.refresh(completed_project)
    db_session.refresh(archived_project)

    projects["active"] = active_project
    projects["completed"] = completed_project
    projects["archived"] = archived_project

    return projects


@pytest.fixture(scope="function")
def test_tasks(db_session, test_users, test_projects):
    """Create test tasks."""
    tasks = {}

    # Backlog task (no assignee)
    backlog_task = Task(
        title="Backlog Task",
        description="A task in backlog",
        status="Backlog",
        project_id=test_projects["active"].id
    )
    db_session.add(backlog_task)

    # In Progress task (with assignee)
    in_progress_task = Task(
        title="In Progress Task",
        description="A task in progress",
        status="In Progress",
        project_id=test_projects["active"].id,
        assignee_id=test_users["dev"].id
    )
    db_session.add(in_progress_task)

    # Done task
    done_task = Task(
        title="Done Task",
        description="A completed task",
        status="Done",
        project_id=test_projects["active"].id,
        assignee_id=test_users["dev"].id
    )
    db_session.add(done_task)

    db_session.commit()
    db_session.refresh(backlog_task)
    db_session.refresh(in_progress_task)
    db_session.refresh(done_task)

    tasks["backlog"] = backlog_task
    tasks["in_progress"] = in_progress_task
    tasks["done"] = done_task

    return tasks


@pytest.fixture(scope="function")
def auth_headers(test_users):
    """Generate authentication headers for different users."""
    headers = {}

    for role, user in test_users.items():
        if user.is_active:
            token = create_access_token(data={"sub": user.email, "user_id": user.id})

            # Track the token for this user
            import time
            expires_at = time.time() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
            token_blacklist.track_token(token, user.id, expires_at)

            headers[role] = {"Authorization": f"Bearer {token}"}

    return headers
