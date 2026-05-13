from fastapi import APIRouter, Request, Form, HTTPException, Response
from fastapi.responses import RedirectResponse
from src.services.auth_service import auth_service
from src.core.security import get_current_user, UserRole
from src.schemas.student import UserUpdate
from sqlmodel import Session, select
from src.core.database import engine
from src.models.user import User

router = APIRouter()

@router.get("/me")
async def get_me(request: Request):
    user_session = get_current_user(request)
    if not user_session:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == user_session["username"])).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

@router.post("/me/update")
async def update_me(request: Request, data: UserUpdate):
    user_session = get_current_user(request)
    if not user_session:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == user_session["username"])).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if data.full_name is not None: user.full_name = data.full_name
        if data.email is not None: user.email = data.email
        if data.phone_number is not None: user.phone_number = data.phone_number
        
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

@router.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...)
):
    user = auth_service.authenticate_user(username, password)
    if user:
        if user["role"] == UserRole.ADMIN:
            response = RedirectResponse(url="/admin", status_code=303)
        elif user["role"] == UserRole.STUDENT:
            response = RedirectResponse(url="/student", status_code=303)
        else:
            # Guest/External users stay on home page to use Guest Trial
            response = RedirectResponse(url="/", status_code=303)
        
        response.set_cookie(
            key="session_v2", 
            value=f"{user['role']}:{user['username']}",
            path="/"
        )
        return response

    return RedirectResponse(url="/?error=auth_failed", status_code=303)

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("session_v2", path="/")
    return response

@router.post("/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...)
):
    user = auth_service.register_user(username, email, password, full_name)
    if user:
        return RedirectResponse(url="/?msg=reg_success", status_code=303)
    return RedirectResponse(url="/?error=reg_failed", status_code=303)

@router.post("/forgot-password")
async def forgot_password(
    email: str = Form(...),
    new_password: str = Form(...)
):
    # Basic implementation: just log it for now or return success
    return RedirectResponse(url="/?msg=password_reset_simulated", status_code=303)
