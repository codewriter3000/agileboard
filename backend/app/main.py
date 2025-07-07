# app/main.py
from fastapi import FastAPI
from app.api import user
from app.db.base import init_db

app = FastAPI(
    title="AgileBoard API",
    version="0.1.0"
)

app.include_router(user.router)

@app.on_event("startup")
def on_startup():
    init_db()
