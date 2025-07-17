from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from app.schemas.task import TaskOut
from app.crud import project as project_crud
from app.core.deps import get_current_user, require_admin_or_scrum_master, get_db
from app.db.models import User
from typing import List

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=ProjectOut, status_code=201)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_scrum_master)
):
    return project_crud.create_project(db=db, project=project)

@router.get("/", response_model=List[ProjectOut])
def get_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return project_crud.get_projects(db=db, skip=skip, limit=limit)

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = project_crud.get_project_by_id(db=db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_scrum_master)
):
    db_project = project_crud.get_project_by_id(db=db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_crud.update_project(db=db, db_project=db_project, updates=project)

@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_scrum_master)
):
    db_project = project_crud.get_project_by_id(db=db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    project_crud.delete_project(db=db, db_project=db_project)
    return Response(status_code=204)

@router.get("/{project_id}/tasks", response_model=List[TaskOut])
def get_project_tasks(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return project_crud.get_project_tasks(db=db, project_id=project_id, skip=skip, limit=limit)

@router.get("/{project_id}/tasks/{task_id}", response_model=TaskOut)
def get_project_task(project_id: int, task_id: int, db: Session = Depends(get_db)):
    return project_crud.get_project_task(db=db, project_id=project_id, task_id=task_id)
