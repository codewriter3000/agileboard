# app/core/deps.py
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.auth import verify_token, TokenData
from app.db.session import SessionLocal
from app.crud import user as user_crud
from app.db.models import User

# HTTP Bearer token security scheme
security = HTTPBearer()

def get_db():
    """Database dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    token = credentials.credentials
    token_data = verify_token(token)

    user = user_crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current authenticated and active user."""
    # You can add user status checks here if needed
    return current_user

def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Require the current user to be an Admin."""
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def require_admin_or_scrum_master(current_user: User = Depends(get_current_active_user)) -> User:
    """Require the current user to be an Admin or ScrumMaster."""
    if current_user.role not in ["Admin", "ScrumMaster"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or ScrumMaster access required"
        )
    return current_user

def require_self_or_admin(user_id: int, current_user: User = Depends(get_current_active_user)) -> User:
    """Require the current user to be the same user or an Admin."""
    if current_user.id != user_id and current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own account"
        )
    return current_user
