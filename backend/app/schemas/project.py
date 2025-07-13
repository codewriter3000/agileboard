from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional


class ProjectStatus(str, Enum):
    active = "Active"
    archived = "Archived"

class ProjectBase(BaseModel):
    name: str
    owner_id: int
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.active
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    owner_id: Optional[int] = None
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = {
        "from_attributes": True
    }

class ProjectOut(ProjectBase):
    id: int

    model_config = {
        "from_attributes": True
    }

class ProjectRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # Use this for SQLAlchemy models in Pydantic v2+
    }
