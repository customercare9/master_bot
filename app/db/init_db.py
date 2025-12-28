"""
Database Initialization
"""
from sqlalchemy.orm import Session
from app.db.models import Base, engine

def init_db():
    """Initialize database tables"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")

def drop_db():
    """Drop all database tables (use with caution)"""
    Base.metadata.drop_all(bind=engine)
    print("⚠️ Database tables dropped")
