"""
Routers Package
"""
from app.routers.auth import router as auth_router
from app.routers.dashboard import router as dashboard_router
from app.routers.bots import router as bots_router
from app.routers.api import router as api_router

__all__ = [
    "auth_router",
    "dashboard_router",
    "bots_router",
    "api_router"
]
