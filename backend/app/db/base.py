# app/db/base.py
from app.db.base_class import Base
from app.db.models import User, Project, Task  # import all models here
from app.db.session import engine
from sqlalchemy.exc import OperationalError
import time

# Import models here so they get registered with Base metadata
from app.db import models

def init_db():
    retries = 10
    for i in range(retries):
        try:
            print("Attempting DB connection...")
            Base.metadata.create_all(bind=engine)
            print("DB initialized successfully")
            return
        except OperationalError:
            print(f"DB not ready yet(attempt {i+1}/{retries})")
            time.sleep(2)
    raise RuntimeError(f"Could not connect to DB after {retries} attempts")
