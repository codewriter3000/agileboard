# Agileboard Backend Tests

This directory contains comprehensive unit tests for the Agileboard backend application.

## Test Structure

- `conftest.py` - Test configuration and fixtures
- `test_auth.py` - Authentication and authorization tests
- `test_users.py` - User management tests
- `test_projects.py` - Project management tests
- `test_tasks.py` - Task management tests
- `test_integration.py` - Integration tests for complete workflows

## Business Rules Tested

### Authentication & Authorization
- JWT token creation and validation
- Password hashing and verification
- Token blacklisting on logout
- Role-based access control (Admin, ScrumMaster, Developer)
- Session management

### User Management
- User CRUD operations
- Email uniqueness validation
- Password requirements
- Role assignment and validation
- User activation/deactivation
- Permission-based access control

### Project Management
- Project CRUD operations
- Project status validation (Active, Completed, Archived)
- Owner assignment and validation
- Owner must be active user
- Project status transitions
- Project filtering and ordering

### Task Management
- Task CRUD operations
- Task status validation (Backlog, In Progress, Done)
- **Key Business Rule**: Cannot move task to "In Progress" without assignee
- **Key Business Rule**: Cannot create task in "In Progress" status without assignee
- Task assignment validation
- Assignee must be active user
- Task-project relationships
- Task filtering and ordering

### Integration Workflows
- Complete project lifecycle
- Role-based project management
- Task status workflow enforcement
- User deactivation impact on projects/tasks
- Authentication workflow
- Data validation cascades

## Running Tests

### Option 1: Using the test runner script
```bash
python run_tests.py
```

### Option 2: Using pytest directly
```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest tests/ -v

# Run specific test class
pytest tests/test_tasks.py::TestTaskStatus

# Run specific test method
pytest tests/test_tasks.py::TestTaskStatus::test_backlog_to_in_progress_requires_assignee
```

### Option 3: Using Docker
```bash
# Build and run tests in container
docker-compose run --rm backend python run_tests.py
```

## Test Configuration

The tests use an in-memory SQLite database for fast execution and isolation. Each test function gets a fresh database state through the fixtures defined in `conftest.py`.

### Key Fixtures
- `client` - FastAPI test client
- `db_session` - Database session
- `test_users` - Pre-created test users with different roles
- `test_projects` - Pre-created test projects
- `test_tasks` - Pre-created test tasks
- `auth_headers` - Authentication headers for different user roles

## Coverage

The tests cover:
- ✅ All API endpoints
- ✅ All business rules and validations
- ✅ Permission-based access control
- ✅ Database constraints and relationships
- ✅ Authentication and authorization flows
- ✅ Error handling and edge cases
- ✅ Integration scenarios

## Key Business Rules Validated

1. **Task Status Workflow**: Tasks cannot be moved to "In Progress" without an assignee
2. **User Roles**: Admin > ScrumMaster > Developer permissions
3. **Active Users Only**: Only active users can be assigned tasks or own projects
4. **Authentication**: JWT tokens are properly validated and blacklisted on logout
5. **Data Validation**: All input data is validated according to schema requirements
6. **Relationship Integrity**: Tasks must belong to projects, assignees must exist, etc.

## Test Data

The tests use consistent test data:
- `admin@test.com` - Admin user
- `scrum@test.com` - Scrum Master user
- `dev@test.com` - Developer user
- `inactive@test.com` - Inactive user
- Projects in Active, Completed, and Archived states
- Tasks in Backlog, In Progress, and Done states

All passwords are hashed using bcrypt and follow the format `{role}123` (e.g., `admin123`, `dev123`).
