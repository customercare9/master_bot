"""
Database Models
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os

from app.core.config import settings

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Bot(Base):
    """Telegram Bot Model"""
    __tablename__ = "bots"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    token = Column(String(200), unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False)
    status = Column(String(20), default="stopped")  # stopped, running, error
    webhook_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "token_masked": self.token[:10] + "..." if self.token else "",
            "description": self.description,
            "is_active": self.is_active,
            "status": self.status,
            "webhook_url": self.webhook_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
        }

class AdminLog(Base):
    """Admin Activity Log Model"""
    __tablename__ = "admin_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100))
    action = Column(String(200))
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "action": self.action,
            "details": self.details,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class SystemStats(Base):
    """System Statistics Model"""
    __tablename__ = "system_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    cpu_usage = Column(Integer, default=0)
    memory_usage = Column(Integer, default=0)
    active_bots = Column(Integer, default=0)
    total_bots = Column(Integer, default=0)
    recorded_at = Column(DateTime, default=datetime.utcnow)
