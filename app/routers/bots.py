"""
Bot Management Router
"""
from fastapi import APIRouter, Depends, HTTPException, Request, templating, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import get_current_user
from app.db.models import Bot, AdminLog
from app.services.bot_manager import bot_manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

templates = templating.Jinja2Templates(directory="app/templates")

@router.get("/bots", response_class=HTMLResponse)
async def bots_list(
    request: Request,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all managed bots"""
    bots = db.query(Bot).all()
    return templates.TemplateResponse(
        "bots.html",
        {
            "request": request,
            "user": user,
            "bots": [bot.to_dict() for bot in bots]
        }
    )

@router.get("/bots/add", response_class=HTMLResponse)
async def add_bot_page(
    request: Request,
    user: dict = Depends(get_current_user)
):
    """Render add bot page"""
    return templates.TemplateResponse(
        "bot_form.html",
        {
            "request": request,
            "user": user,
            "bot": None,
            "title": "Add New Bot"
        }
    )

@router.post("/bots/add")
async def add_bot(
    request: Request,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new bot"""
    form_data = await request.form()
    name = form_data.get("name")
    token = form_data.get("token")
    description = form_data.get("description", "")
    
    # Validation
    if not name or not token:
        return templates.TemplateResponse(
            "bot_form.html",
            {
                "request": request,
                "user": user,
                "bot": {"name": name, "token": token, "description": description},
                "error": "Name and token are required"
            }
        )
    
    # Check for duplicate
    existing = db.query(Bot).filter(Bot.name == name).first()
    if existing:
        return templates.TemplateResponse(
            "bot_form.html",
            {
                "request": request,
                "user": user,
                "bot": {"name": name, "token": token, "description": description},
                "error": "A bot with this name already exists"
            }
        )
    
    # Create bot
    bot = Bot(
        name=name,
        token=token,
        description=description,
        status="stopped",
        is_active=False
    )
    db.add(bot)
    db.commit()
    
    # Log the action
    log = AdminLog(
        username=user["username"],
        action="add_bot",
        details=f"Added new bot: {name}",
        ip_address=request.client.host if request.client else None
    )
    db.add(log)
    db.commit()
    
    return RedirectResponse(url="/admin/bots", status_code=status.HTTP_302_FOUND)

@router.get("/bots/{bot_id}/edit", response_class=HTMLResponse)
async def edit_bot_page(
    request: Request,
    bot_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Render edit bot page"""
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    return templates.TemplateResponse(
        "bot_form.html",
        {
            "request": request,
            "user": user,
            "bot": bot.to_dict(),
            "title": f"Edit Bot: {bot.name}"
        }
    )

@router.post("/bots/{bot_id}/edit")
async def edit_bot(
    request: Request,
    bot_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a bot"""
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    form_data = await request.form()
    name = form_data.get("name")
    token = form_data.get("token")
    description = form_data.get("description", "")
    
    # Update bot
    bot.name = name
    bot.token = token
    bot.description = description
    db.commit()
    
    # Log the action
    log = AdminLog(
        username=user["username"],
        action="edit_bot",
        details=f"Updated bot: {name}",
        ip_address=request.client.host if request.client else None
    )
    db.add(log)
    db.commit()
    
    return RedirectResponse(url="/admin/bots", status_code=status.HTTP_302_FOUND)

@router.get("/bots/{bot_id}/start")
async def start_bot(
    request: Request,
    bot_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a bot"""
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    success = await bot_manager.start_bot(db, bot_id)
    
    if success:
        log = AdminLog(
            username=user["username"],
            action="start_bot",
            details=f"Started bot: {bot.name}",
            ip_address=request.client.host if request.client else None
        )
    else:
        log = AdminLog(
            username=user["username"],
            action="start_bot_failed",
            details=f"Failed to start bot: {bot.name}",
            ip_address=request.client.host if request.client else None
        )
    db.add(log)
    db.commit()
    
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)

@router.get("/bots/{bot_id}/stop")
async def stop_bot(
    request: Request,
    bot_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stop a bot"""
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    success = await bot_manager.stop_bot(db, bot_id)
    
    if success:
        log = AdminLog(
            username=user["username"],
            action="stop_bot",
            details=f"Stopped bot: {bot.name}",
            ip_address=request.client.host if request.client else None
        )
    else:
        log = AdminLog(
            username=user["username"],
            action="stop_bot_failed",
            details=f"Failed to stop bot: {bot.name}",
            ip_address=request.client.host if request.client else None
        )
    db.add(log)
    db.commit()
    
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)

@router.get("/bots/{bot_id}/restart")
async def restart_bot(
    request: Request,
    bot_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restart a bot"""
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    success = await bot_manager.restart_bot(db, bot_id)
    
    log = AdminLog(
        username=user["username"],
        action="restart_bot",
        details=f"Restarted bot: {bot.name}",
        ip_address=request.client.host if request.client else None
    )
    db.add(log)
    db.commit()
    
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)

@router.get("/bots/{bot_id}/delete")
async def delete_bot(
    request: Request,
    bot_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a bot"""
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Stop if running
    if bot.is_active:
        await bot_manager.stop_bot(db, bot_id)
    
    bot_name = bot.name
    db.delete(bot)
    db.commit()
    
    log = AdminLog(
        username=user["username"],
        action="delete_bot",
        details=f"Deleted bot: {bot_name}",
        ip_address=request.client.host if request.client else None
    )
    db.add(log)
    db.commit()
    
    return RedirectResponse(url="/admin/bots", status_code=status.HTTP_302_FOUND)

@router.get("/bots/stop-all")
async def stop_all_bots(
    request: Request,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stop all running bots"""
    await bot_manager.stop_all_bots(db)
    
    log = AdminLog(
        username=user["username"],
        action="stop_all_bots",
        details="Stopped all running bots",
        ip_address=request.client.host if request.client else None
    )
    db.add(log)
    db.commit()
    
    return RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
