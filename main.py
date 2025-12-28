#!/usr/bin/env python3
"""
Master Telegram Bot Management System
A FastAPI-based system to host and manage multiple Telegram bots
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import uvicorn

from app.core.config import settings
from app.core.logging import setup_logging
from app.routers import auth, dashboard, bots, api
from app.db.init_db import init_db

# Setup logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Master Bot System...")
    await init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down Master Bot System...")

# Create FastAPI app
app = FastAPI(
    title="Master Bot Control Panel",
    description="A powerful system to manage multiple Telegram bots",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/admin", tags=["Dashboard"])
app.include_router(bots.router, prefix="/admin/bots", tags=["Bot Management"])
app.include_router(api.router, prefix="/api", tags=["API"])

@app.get("/")
async def root():
    """Root endpoint redirects to admin login"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/admin/login")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

def main():
    """Main entry point"""
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

if __name__ == "__main__":
    main()
