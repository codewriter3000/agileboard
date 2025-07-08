from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional


class TaskStatus(str, Enum):
    backlog = "Backlog"
    in_progress = "In Progress"
    review = "Review"
    done = "Done"


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.backlog
    assignee_id: Optional[int] = None
    sprint_id: Optional[int] = None


class TaskCreate(TaskBase):
    pass  # Same as TaskBase


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[int] = None
    sprint_id: Optional[int] = None

    model_config = {
        "from_attributes": True
    }


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    assignee_id: Optional[int]
    sprint_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
