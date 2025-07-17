from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate
from app.crud import task as task_crud
from app.core.deps import get_current_user, require_admin_or_scrum_master, get_db
from app.db.models import User, Project
from typing import List

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskOut, status_code=201)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only Scrum Masters and Admins can create tasks
    if current_user.role not in ["Admin", "ScrumMaster"]:
        raise HTTPException(
            status_code=403,
            detail="Only Scrum Masters and Admins can create tasks"
        )

    # Validate project_id exists
    project = db.query(Project).filter_by(id=task.project_id).first()
    if not project:
        raise HTTPException(status_code=400, detail="Project not found")

    # Validate assignee_id exists (if provided)
    if task.assignee_id is not None:
        assignee = db.query(User).filter_by(id=task.assignee_id).first()
        if not assignee:
            raise HTTPException(status_code=400, detail="Assignee not found")
        if not assignee.is_active:
            raise HTTPException(status_code=400, detail="Cannot assign task to inactive user")

    # Task should have a name in between 1 and 255 characters
    if not task.title or len(task.title) < 1 or len(task.title) > 255:
        raise HTTPException(status_code=422, detail="Task title must be between 1 and 255 characters")

    return task_crud.create_task(db=db, task=task)

@router.get("/", response_model=List[TaskOut])
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return task_crud.get_tasks(db=db, skip=skip, limit=limit)

@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = task_crud.get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only Scrum Masters and Admins can update tasks
    if current_user.role not in ["Admin", "ScrumMaster"]:
        raise HTTPException(
            status_code=403,
            detail="Only Scrum Masters and Admins can update tasks"
        )

    db_task = task_crud.get_task_by_id(db=db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Validate assignee_id exists (if provided)
    if task.assignee_id is not None:
        assignee = db.query(User).filter_by(id=task.assignee_id).first()
        if not assignee:
            raise HTTPException(status_code=400, detail="Assignee not found")

    return task_crud.update_task(db=db, db_task=db_task, updates=task)

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_scrum_master)
):
    # Only Scrum Masters and Admins can delete tasks
    db_task = task_crud.get_task_by_id(db=db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_crud.delete_task(db=db, db_task=db_task)
    return Response(status_code=204, content='{"message": "Task deleted successfully"}', media_type="application/json")
