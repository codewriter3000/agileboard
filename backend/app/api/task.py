from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate
from app.crud import task as task_crud
from typing import List

router = APIRouter(prefix="/tasks", tags=["tasks"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TaskOut)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    return task_crud.create_task(db=db, task=task)

@router.get("/", response_model=List[TaskOut])
def get_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return task_crud.get_tasks(db=db, skip=skip, limit=limit)

@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = task_crud.get_task_by_id(db=db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = task_crud.get_task_by_id(db=db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_crud.update_task(db=db, db_task=db_task, updates=task)

@router.delete("/{task_id}", response_model=TaskOut)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = task_crud.get_task_by_id(db=db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_crud.delete_task(db=db, db_task=db_task)
    return Response(status_code=204, content=None)
