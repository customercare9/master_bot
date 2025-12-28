"""
API Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import get_current_user
from app.db.models import Bot, AdminLog
from app.services.bot_manager import bot_manager

router = APIRouter()

@router.get("/bots")
async def get_bots(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all bots (API endpoint)"""
    bots = db.query(Bot).all()
    return {
        "success": True,
        "data": [bot.to_dict() for bot in bots]
    }

@router.get("/bots/{bot_id}")
async def get_bot(
    bot_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific bot (API endpoint)"""
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    return {
        "success": True,
        "data": bot.to_dict()
    }

@router.post("/bots")
async def create_bot_api(
    name: str,
    token: str,
    description: str = "",
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new bot (API endpoint)"""
    # Check for duplicate
    existing = db.query(Bot).filter(Bot.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bot with this name already exists")
    
    bot = Bot(
        name=name,
        token=token,
        description=description,
        status="stopped",
        is_active=False
    )
    db.add(bot)
    db.commit()
    
    return {
        "success": True,
        "message": "Bot created successfully",
        "data": bot.to_dict()
    }

@router.delete("/bots/{bot_id}")
async def delete_bot_api(
    bot_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a bot (API endpoint)"""
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    # Stop if running
    if bot.is_active:
        await bot_manager.stop_bot(db, bot_id)
    
    bot_name = bot.name
    db.delete(bot)
    db.commit()
    
    return {
        "success": True,
        "message": f"Bot {bot_name} deleted successfully"
    }

@router.post("/bots/{bot_id}/start")
async def start_bot_api(
    bot_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a bot (API endpoint)"""
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    success = await bot_manager.start_bot(db, bot_id)
    
    if success:
        return {
            "success": True,
            "message": f"Bot {bot.name} started successfully"
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to start bot")

@router.post("/bots/{bot_id}/stop")
async def stop_bot_api(
    bot_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stop a bot (API endpoint)"""
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    
    success = await bot_manager.stop_bot(db, bot_id)
    
    if success:
        return {
            "success": True,
            "message": f"Bot {bot.name} stopped successfully"
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to stop bot")

@router.get("/stats")
async def get_stats(
    user: dict = Depends(get_current_user)
):
    """Get system statistics (API endpoint)"""
    return {
        "success": True,
        "data": {
            "active_bots": bot_manager.get_active_bots_count(),
            "timestamp": status.__name__
        }
    }

@router.get("/logs")
async def get_logs(
    limit: int = 50,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get admin logs (API endpoint)"""
    logs = db.query(AdminLog).order_by(AdminLog.created_at.desc()).limit(limit).all()
    return {
        "success": True,
        "data": [log.to_dict() for log in logs]
    }
