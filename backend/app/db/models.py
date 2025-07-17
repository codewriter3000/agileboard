# app/db/models.py
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum("Admin", "ScrumMaster", "Developer", name="user_roles"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum("Active", "Archived", "Completed", name="project_status"), default="Active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum("Backlog", "In Progress", "Review", "Done", name="task_status"), default="Backlog")
    assignee_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    sprint_id = Column(Integer, nullable=True)  # Temporarily commented until database migration
    created_at = Column(DateTime, default=datetime.utcnow)

