"""
Authentication Router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import get_current_user, authenticate_admin, create_access_token
from app.db.models import AdminLog

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render login page"""
    return {
        "template": "login.html",
        "context": {"request": request}
    }

@router.post("/login")
async def login(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(HTTPBasic),
    db: Session = Depends(get_db)
):
    """Handle login request"""
    username = credentials.username
    password = credentials.password
    
    if authenticate_admin(username, password):
        # Create access token
        access_token = create_access_token(data={"sub": username})
        
        # Log the login
        log = AdminLog(
            username=username,
            action="login",
            details="Admin logged in successfully",
            ip_address=request.client.host if request.client else None
        )
        db.add(log)
        db.commit()
        
        response = RedirectResponse(url="/admin/dashboard", status_code=status.HTTP_302_FOUND)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=60 * 24 * 7  # 7 days
        )
        return response
    else:
        return {
            "template": "login.html",
            "context": {
                "request": request,
                "error": "Invalid username or password"
            }
        }

@router.get("/logout")
async def logout():
    """Handle logout"""
    response = RedirectResponse(url="/admin/login")
    response.delete_cookie("access_token")
    return response

@router.get("/check-auth")
async def check_auth(user: dict = Depends(get_current_user)):
    """Check if user is authenticated"""
    return {"authenticated": True, "username": user["username"]}
