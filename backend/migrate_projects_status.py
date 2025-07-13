#!/usr/bin/env python3
"""
Database migration script to add status field to projects table.
This script should be run once to update existing projects to have the status field.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.session import SessionLocal

def migrate_projects_status():
    """Add status column to projects table if it doesn't exist."""
    db = SessionLocal()
    try:
        # Check if status column exists (PostgreSQL syntax)
        result = db.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'projects' AND table_schema = 'public'
        """))
        columns = [row[0] for row in result.fetchall()]

        print(f"Existing columns in projects table: {columns}")

        if 'status' not in columns:
            print("Adding status column to projects table...")
            # Add status column with default value 'Active'
            db.execute(text("ALTER TABLE projects ADD COLUMN status VARCHAR(20) DEFAULT 'Active'"))

        if 'created_at' not in columns:
            print("Adding created_at column to projects table...")
            db.execute(text("ALTER TABLE projects ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))

        if 'updated_at' not in columns:
            print("Adding updated_at column to projects table...")
            db.execute(text("ALTER TABLE projects ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))

        # Update existing projects to have 'Active' status if null
        db.execute(text("UPDATE projects SET status = 'Active' WHERE status IS NULL"))

        db.commit()
        print("Migration completed successfully!")

    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_projects_status()
