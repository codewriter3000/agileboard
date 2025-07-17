# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from enum import Enum


class Role(str, Enum):
    Admin = "Admin"
    ScrumMaster = "ScrumMaster"
    Developer = "Developer"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: Role
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserRead(BaseModel):
    id: int
    email: str
    full_name: str
    role: Role
    is_active: bool

    class Config:
        from_attributes = True  # Use this for SQLAlchemy models in Pydantic v2+

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    role: Role | None = None
    is_active: bool | None = None

    model_config = {
        "from_attributes": True
    }
