"""
Dashboard Router
"""
from fastapi import APIRouter, Depends, HTTPException, Request, templating
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import get_current_user
from app.db.models import Bot, AdminLog, SystemStats
from app.services.bot_manager import bot_manager

router = APIRouter()

# Jinja2 templates
templates = templating.Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Render main dashboard"""
    # Get all bots
    bots = db.query(Bot).all()
    bots_data = [bot.to_dict() for bot in bots]
    
    # Get system stats
    active_count = bot_manager.get_active_bots_count()
    total_count = len(bots)
    error_count = len([b for b in bots if b.status == "error"])
    
    # Get recent logs
    recent_logs = db.query(AdminLog).order_by(AdminLog.created_at.desc()).limit(10).all()
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "bots": bots_data,
            "active_bots": active_count,
            "total_bots": total_count,
            "error_bots": error_count,
            "recent_logs": [log.to_dict() for log in recent_logs]
        }
    )

@router.get("/", response_class=HTMLResponse)
async def admin_index(
    request: Request,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin panel index"""
    return RedirectResponse(url="/admin/dashboard")

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    user: dict = Depends(get_current_user)
):
    """Render settings page"""
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "user": user
        }
    )

@router.get("/logs", response_class=HTMLResponse)
async def logs_page(
    request: Request,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Render logs page"""
    logs = db.query(AdminLog).order_by(AdminLog.created_at.desc()).limit(100).all()
    return templates.TemplateResponse(
        "logs.html",
        {
            "request": request,
            "user": user,
            "logs": [log.to_dict() for log in logs]
        }
    )
