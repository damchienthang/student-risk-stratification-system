from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter(tags=["Auth"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "src", "web", "templates"))

# Mock user database for demo
ADMIN_USERS = {"admin": "admin123"}

@router.get("/login", response_class=RedirectResponse)
async def login_page_redirect():
    return RedirectResponse(url="/")

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    # Determine role automatically
    if username in ADMIN_USERS:
        if password == ADMIN_USERS[username]:
            response = RedirectResponse(url="/admin", status_code=303)
            response.set_cookie(key="session_v2", value=f"admin:{username}")
            return response
    else:
        # Check if it's a student (username == password and username is numeric)
        if username == password and username.isdigit():
            # In a real app, we would verify against the data manager or DB
            # For now, let's just allow it if username == password
            response = RedirectResponse(url="/student", status_code=303)
            response.set_cookie(key="session_v2", value=f"student:{username}")
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
