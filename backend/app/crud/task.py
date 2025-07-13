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
            raise HTTPException(status_code=404, detail="Assignee user not found")

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
    # Apply updates to determine final state
    final_status = updates.status if updates.status is not None else db_task.status
    final_assignee_id = updates.assignee_id if updates.assignee_id is not None else db_task.assignee_id

    # Validate that the assignee exists if being updated
    if updates.assignee_id is not None:
        assignee = user_crud.get_user_by_id(db=db, user_id=updates.assignee_id)
        if not assignee:
            raise HTTPException(status_code=404, detail="Assignee user not found")

    # Validate assignee requirement for active statuses
    if final_status in ["In Progress", "Review", "Done"]:
        if final_assignee_id is None:
            raise HTTPException(
                status_code=400,
                detail=f"assignee_id is required when task status is '{final_status}'"
            )

    # Apply the updates
    if updates.title is not None:
        db_task.title = updates.title
    if updates.description is not None:
        db_task.description = updates.description
    if updates.status is not None:
        db_task.status = updates.status
    if updates.assignee_id is not None:
        db_task.assignee_id = updates.assignee_id
    if updates.project_id is not None:
        db_task.project_id = updates.project_id
    if updates.sprint_id is not None:
        db_task.sprint_id = updates.sprint_id
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, db_task: models.Task):
    db.delete(db_task)
    db.commit()
    return db_task