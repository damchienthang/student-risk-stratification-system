# Create web routes, HTML templates, and static assets for frontend dashboard
from typing import Optional
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.core.config import settings
from src.core.security import get_current_user, is_admin, is_student, UserRole
from src.services.student_service import student_service

from src.core.database import engine
from src.models.user import User
from sqlmodel import Session, select

router = APIRouter()
templates = Jinja2Templates(directory=str(settings.BASE_DIR / "src" / "web" / "templates"))

async def get_db_user(request: Request) -> Optional[User]:
    session_data = get_current_user(request)
    if not session_data:
        return None
    with Session(engine) as session:
        return session.exec(select(User).where(User.username == session_data["username"])).first()

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = await get_db_user(request)
    
    return templates.TemplateResponse(request=request, name="pages/home/index.html", context={
        "user": user,
        "UserRole": UserRole
    })

@router.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    user = await get_db_user(request)
    return templates.TemplateResponse(request=request, name="pages/about/index.html", context={"user": user})

@router.get("/model", response_class=HTMLResponse)
async def model_page(request: Request):
    user = await get_db_user(request)
    return templates.TemplateResponse(request=request, name="pages/model/index.html", context={"user": user})

@router.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    user = await get_db_user(request)
    if not user or user.role != UserRole.ADMIN:
        return RedirectResponse(url="/")
    return templates.TemplateResponse(request=request, name="pages/admin/dashboard.html", context={
        "user": user,
        "UserRole": UserRole
    })

@router.get("/student", response_class=HTMLResponse)
async def student_page(request: Request):
    user = await get_db_user(request)
    # Only Official Students can access their dashboard
    if not user or user.role != UserRole.STUDENT:
        return RedirectResponse(url="/")
    
    # Auto-fetch official prediction for OULAD students
    report = None
    if user.role == UserRole.STUDENT:
        try:
            sid = int(user.username)
            report = student_service.get_student_report(sid)
        except Exception:
            pass
        
    return templates.TemplateResponse(request=request, name="pages/student/dashboard.html", context={
        "user": user,
        "UserRole": UserRole,
        "student": report["student"] if report else None,
        "prediction": report["prediction"] if report else None
    })
