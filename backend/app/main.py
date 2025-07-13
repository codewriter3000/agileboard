# app/main.py
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from app.api import user, project, task
from app.db.base import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Initialize the database
    init_db()
    yield
    # Here you could add any cleanup code if needed

app = FastAPI(
    title="AgileBoard API",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(user.router)
app.include_router(project.router)
app.include_router(task.router)
