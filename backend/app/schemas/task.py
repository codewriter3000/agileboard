from pydantic import BaseModel, model_validator
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
    project_id: int  # Required field
    sprint_id: Optional[int] = None

    @model_validator(mode='after')
    def validate_assignee_for_active_status(self):
        if self.status in [TaskStatus.in_progress, TaskStatus.review, TaskStatus.done]:
            if self.assignee_id is None:
                raise ValueError(f"assignee_id is required when task status is '{self.status.value}'")
        return self


class TaskCreate(TaskBase):
    pass  # Same as TaskBase


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[int] = None
    project_id: Optional[int] = None
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
    project_id: int
    sprint_id: Optional[int]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    assignee_id: Optional[int]
    project_id: int
    sprint_id: Optional[int]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class TaskDelete(BaseModel):
    id: int
    reason: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
