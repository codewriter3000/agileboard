# app/api/user.py
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.db import models
from app.db.session import SessionLocal
from app.schemas.user import UserCreate, UserOut, UserRead, UserUpdate
from app.crud import user as user_crud
from app.core.deps import get_current_user, require_admin, get_db
from typing import List

import re

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut, status_code=201)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    # Password must be at least 8 characters and contain at least one letter and number
    if (
        user.password is None
        or len(user.password) < 8
        or not any(c.isalpha() for c in user.password)
        or not any(c.isdigit() for c in user.password)
    ):
        raise HTTPException(
            status_code=422,
            detail="Password must be at least 8 characters long and contain at least one letter and number."
        )

    # Validate full name
    if not user.full_name or len(user.full_name) < 1 or len(user.full_name) > 255:
        raise HTTPException(status_code=422, detail="Full name must be between 1 and 255 characters")

    if not re.match(r"^[a-zA-Z -]+$", user.full_name):
        raise HTTPException(status_code=422, detail="Full name can only contain letters, spaces, and hyphens")

    # Validate email format
    if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", user.email):
        raise HTTPException(status_code=422, detail="Invalid email format")

    # Check if email already exists
    db_user = user_crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_crud.create_user(db, user)

@router.get("/", response_model=List[UserRead])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return user_crud.get_users(db, skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserRead)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    updates: UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_user = user_crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check permissions: developers can only update their own email/password
    if current_user.role == "Developer":
        if current_user.id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Developers can only update their own account"
            )
        # Developers can only update email and password
        allowed_fields = {"email", "password"}
        update_dict = updates.dict(exclude_unset=True)
        for field in update_dict:
            if field not in allowed_fields:
                raise HTTPException(
                    status_code=403,
                    detail="Developers can only update email and password"
                )
    elif current_user.role == "ScrumMaster":
        # Scrum masters can update any user but cannot change roles
        if "role" in updates.dict(exclude_unset=True):
            raise HTTPException(
                status_code=403,
                detail="Only admins can change user roles"
            )
    # Admin can update anything - no restrictions

    if updates.email:
        existing_user = user_crud.get_user_by_email(db, updates.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Check if email is actually changing
        if db_user.email != updates.email:
            # Email is changing, revoke all existing tokens for security
            from app.core.auth import revoke_all_user_tokens
            revoke_all_user_tokens(user_id)

    return user_crud.update_user(db, db_user, updates)

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    db_user = user_crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    user_crud.delete_user(db, db_user)
    return Response(status_code=204)
