from sqlalchemy.orm import Session
from app.db import models
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut, ProjectRead
from app.crud import user as user_crud
from fastapi import HTTPException
from datetime import datetime

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Project).offset(skip).limit(limit).all()

def get_project_by_id(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def get_project_by_name(db: Session, name: str):
    return db.query(models.Project).filter(models.Project.name == name).first()

def create_project(db: Session, project: ProjectCreate):
    # Check for duplicate project name
    existing_project = get_project_by_name(db=db, name=project.name)
    if existing_project:
        raise HTTPException(status_code=400, detail="A project with this name already exists")

    # Validate that the owner exists and is an Admin
    if project.owner_id:
        owner = user_crud.get_user_by_id(db=db, user_id=project.owner_id)
        if not owner:
            raise HTTPException(status_code=404, detail="Owner user not found")
        if owner.role != "Admin":
            raise HTTPException(status_code=403, detail="Only Admin users can be project owners")

    db_project = models.Project(
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        status=project.status
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, db_project: models.Project, updates: ProjectUpdate):
    if updates.name is not None:
        # Check for duplicate project name (excluding the current project)
        existing_project = get_project_by_name(db=db, name=updates.name)
        if existing_project and existing_project.id != db_project.id:
            raise HTTPException(status_code=400, detail="A project with this name already exists")
        db_project.name = updates.name
    if updates.description is not None:
        db_project.description = updates.description
    if updates.owner_id is not None:
        # Validate that the new owner exists and is an Admin
        owner = user_crud.get_user_by_id(db=db, user_id=updates.owner_id)
        if not owner:
            raise HTTPException(status_code=404, detail="Owner user not found")
        if owner.role != "Admin":
            raise HTTPException(status_code=403, detail="Only Admin users can be project owners")
        db_project.owner_id = updates.owner_id
    if updates.status is not None:
        db_project.status = updates.status

    # Always update the updated_at timestamp
    db_project.updated_at = datetime.now()

    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, db_project: models.Project):
    db.delete(db_project)
    db.commit()
    return db_project

def get_project_tasks(db: Session, project_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Task).filter(models.Task.project_id == project_id).offset(skip).limit(limit).all()

def get_project_task_by_id(db: Session, project_id: int, task_id: int):
    return db.query(models.Task).filter(models.Task.project_id == project_id, models.Task.id == task_id).first()

def get_project_task(db: Session, project_id: int, task_id: int):
    return db.query(models.Task).filter(models.Task.project_id == project_id, models.Task.id == task_id).first()
