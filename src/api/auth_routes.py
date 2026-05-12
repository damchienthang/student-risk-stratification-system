from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os

from src.services.db_manager import get_db_manager

router = APIRouter(tags=["Auth"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "src", "web", "templates"))

@router.get("/login", response_class=RedirectResponse)
async def login_page_redirect():
    return RedirectResponse(url="/")

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    dbm = get_db_manager()
    user = dbm.authenticate_user(username, password)
    
    if user:
        # Điều hướng theo vai trò
        if user["role"] == "lecturer":
            response = RedirectResponse(url="/admin", status_code=303)
        else:
            response = RedirectResponse(url="/student", status_code=303)
            
        # Lưu session
        response.set_cookie(key="session_v2", value=f"{user['role']}:{user['username']}")
        return response
            
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "error": "Thông tin đăng nhập không chính xác (Mã SV/Mật khẩu)",
        "show_login": True
    })

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("session_v2")
    return response

def get_current_user(request: Request):
    session = request.cookies.get("session_v2")
    if not session:
        return None
    try:
        role, username = session.split(":", 1)
        return {"role": role, "username": username}
    except ValueError:
        return None
