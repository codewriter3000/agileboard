# app/api/auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from sqlalchemy.orm import Session
from app.core.auth import (
    verify_password,
    create_access_token,
    get_password_hash,
    Token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    revoke_token,
    revoke_all_user_tokens,
    token_blacklist
)
from app.core.deps import get_db, get_current_user
from app.crud import user as user_crud
from app.schemas.user import UserCreate, UserOut
from app.db.models import User
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

def authenticate_user(db: Session, email: str, password: str) -> User:
    """Authenticate a user by email and password."""
    user = user_crud.get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    if not user.is_active:
        return False
    return user

@router.post("/login", response_model=LoginResponse, status_code=201)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},  # Use user ID as subject
        expires_delta=access_token_expires
    )

    # Track the token for this user
    import time
    expires_at = time.time() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    token_blacklist.track_token(access_token, user.id, expires_at)

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserOut(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role
        )
    )

@router.post("/token", response_model=Token, status_code=201)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 compatible token endpoint."""
    user = authenticate_user(db, form_data.username, form_data.password)  # username is email
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},  # Use user ID as subject
        expires_delta=access_token_expires
    )

    # Track the token for this user
    import time
    expires_at = time.time() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    token_blacklist.track_token(access_token, user.id, expires_at)

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role
    )

@router.post("/logout", status_code=201)
def logout(current_user: User = Depends(get_current_user)):
    """Logout endpoint that revokes all tokens for the current user."""
    # Revoke all tokens belonging to this user
    revoke_all_user_tokens(current_user.id)
    return {"message": "Successfully logged out from all devices"}

@router.post("/logout-current", status_code=201)
def logout_current_device(
    current_user: User = Depends(get_current_user),
    token: str = Depends(security)
):
    """Logout from current device only (revokes current token only)."""
    # Revoke only the current token
    revoke_token(token.credentials)
    return {"message": "Successfully logged out from current device"}

@router.post("/register", response_model=UserOut, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (temporarily disabled)."""
    # Temporarily disable registration
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Public registration is disabled on this application"
    )

    # Original registration code (commented out)
    # # Check if user already exists
    # existing_user = user_crud.get_user_by_email(db, user_data.email)
    # if existing_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Email already registered"
    #     )
    #
    # # Create new user
    # new_user = user_crud.create_user(db, user_data)
    # return UserOut(
    #     id=new_user.id,
    #     email=new_user.email,
    #     full_name=new_user.full_name,
    #     role=new_user.role
    # )
