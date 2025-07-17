from sqlalchemy.orm import Session
from app.db import models
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut, TaskRead, TaskDelete
from app.crud import user as user_crud
from fastapi import HTTPException

def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Task).offset(skip).limit(limit).all()

def get_task_by_id(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def create_task(db: Session, task: TaskCreate):
    # Validate that the assignee exists if provided
    if task.assignee_id is not None:
        assignee = user_crud.get_user_by_id(db=db, user_id=task.assignee_id)
        if not assignee:
            raise HTTPException(status_code=400, detail="Assignee not found")
        if not assignee.is_active:
            raise HTTPException(status_code=400, detail="Cannot assign task to inactive user")

    # Validate that In Progress status requires an assignee
    if task.status == "In Progress" and task.assignee_id is None:
        raise HTTPException(
            status_code=400,
            detail="Cannot create task in In Progress status without assignee"
        )

    db_task = models.Task(
        title=task.title,
        description=task.description,
        status=task.status,
        assignee_id=task.assignee_id,
        project_id=task.project_id,
        sprint_id=task.sprint_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, db_task: models.Task, updates: TaskUpdate):
    # Get the model fields that were explicitly set in the update
    update_data = updates.model_dump(exclude_unset=True)

    # Apply updates to determine final state
    final_status = update_data.get('status', db_task.status)
    final_assignee_id = update_data.get('assignee_id', db_task.assignee_id)

    # Validate that the assignee exists if being updated and is not None
    if 'assignee_id' in update_data and update_data['assignee_id'] is not None:
        assignee = user_crud.get_user_by_id(db=db, user_id=update_data['assignee_id'])
        if not assignee:
            raise HTTPException(status_code=400, detail="Assignee not found")
        if not assignee.is_active:
            raise HTTPException(status_code=400, detail="Cannot assign task to inactive user")

    # Validate "In Progress" status requires an assignee
    if final_status == "In Progress" and final_assignee_id is None:
        raise HTTPException(
            status_code=400,
            detail="Cannot move task to In Progress without assignee"
        )

    # Apply the updates
    for field, value in update_data.items():
        setattr(db_task, field, value)

    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, db_task: models.Task):
    db.delete(db_task)
    db.commit()
    return db_task