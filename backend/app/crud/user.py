# app/crud/user.py
from sqlalchemy.orm import Session
from app.db import models
from app.schemas.user import UserCreate, UserUpdate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).filter(models.User.is_active == True).offset(skip).limit(limit).all()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: UserCreate):
    hashed_pw = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        password_hash=hashed_pw,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: models.User, updates: UserUpdate):
    if updates.full_name is not None:
        db_user.full_name = updates.full_name
    if updates.role is not None:
        db_user.role = updates.role
    if updates.email is not None:
        db_user.email = updates.email
    if updates.is_active is not None:
        db_user.is_active = updates.is_active
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, db_user: models.User):
    db.delete(db_user)
    db.commit()
    return db_user