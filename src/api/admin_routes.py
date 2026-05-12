from fastapi import APIRouter, Request, HTTPException, Query
from typing import Any, cast
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os

from src.api.auth_routes import get_current_user
from src.services.db_manager import get_db_manager

router = APIRouter(tags=["Admin"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "src", "web", "templates"))

@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    user = get_current_user(request)
    if not user or user["role"] != "lecturer":
        return RedirectResponse(url="/")

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "module": "BBB",
        "presentation": "2014J",
        "user": user
    })

@router.get("/api/analytics")
async def get_analytics(
    request: Request,
    module: str = Query("BBB"),
    semester: str = Query("2014J"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: str = Query(None),
    risk: str = Query("all"),
    source: str = Query("official")  # 'official' or 'guest'
):
    user = get_current_user(request)
    if not user or user["role"] != "lecturer":
        raise HTTPException(status_code=403, detail="Unauthorized")

    dbm = get_db_manager()

    # Handle GUEST predictions source
    if source == "guest":
        logs, total_count = dbm.get_guest_predictions_paginated(page=page, limit=limit, risk_level=risk)
        guest_list = []
        for log in logs:
            guest_list.append({
                "id": f"GUEST_{log.id}",
                "score": round(log.avg_score or 0, 2),
                "clicks": log.total_clicks or 0,
                "risk": log.risk_label or "Unknown",
                "risk_level": log.risk_level or 0,
                "code_module": "Guest",
                "code_presentation": log.timestamp
            })
        return {
            "summary": {"total_students": total_count, "avg_clicks": 0, "avg_score": 0},
            "risk_distribution": [0, 0, 0, 0],
            "top_at_risk": [],
            "all_students": guest_list,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_records": total_count,
                "total_pages": (total_count + limit - 1) // limit
            }
        }

    # Handle OFFICIAL students source (default)
    presentation = semester
    summary_data = dbm.get_summary_stats(module, presentation)
    stats = cast(Any, summary_data[0])
    risk_dist = summary_data[1]
    
    if not stats or stats.total == 0:
        return {"error": "Data not found", "all_students": [], "top_at_risk": []}

    students, total_count = dbm.get_students_paginated(
        module, presentation, page=page, limit=limit, search_id=search, risk_level=risk
    )

    student_list = []
    for s in students:
        student_list.append({
            "id": s.id_student,
            "score": round(s.avg_score, 2),
            "clicks": s.total_clicks,
            "risk": s.risk_label,
            "risk_level": s.risk_level,
            "code_module": s.code_module,
            "code_presentation": s.code_presentation
        })

    top_at_risk_list, _ = dbm.get_students_paginated(module, presentation, page=1, limit=10)
    top_at_risk = [{
        "id": s.id_student,
        "score": round(s.avg_score, 2),
        "clicks": s.total_clicks,
        "risk": s.risk_label,
        "risk_level": s.risk_level,
        "code_module": s.code_module,
        "code_presentation": s.code_presentation
    } for s in top_at_risk_list]

    return {
        "summary": {
            "total_students": stats.total,
            "avg_clicks": round(float(stats.avg_clicks), 1) if stats.avg_clicks else 0,
            "avg_score": round(float(stats.avg_score), 2) if stats.avg_score else 0
        },
        "risk_distribution": [risk_dist.get(i, 0) for i in range(4)],
        "top_at_risk": top_at_risk,
        "all_students": student_list,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_records": total_count,
            "total_pages": (total_count + limit - 1) // limit
        }
    }

@router.get("/api/admin/users")
async def list_users(request: Request):
    user = get_current_user(request)
    if not user or user["role"] != "lecturer":
        raise HTTPException(status_code=403, detail="Unauthorized")

    from sqlmodel import Session, select
    from src.models.user import User
    from src.database import engine

    with Session(engine) as session:
        users = session.exec(select(User)).all()
        return {
            "users": [
                {"username": u.username, "full_name": u.full_name, "role": u.role}
                for u in users
            ]
        }

@router.post("/api/admin/users")
async def create_user(request: Request):
    user = get_current_user(request)
    if not user or user["role"] != "lecturer":
        raise HTTPException(status_code=403, detail="Unauthorized")

    from sqlmodel import Session, select
    from src.models.user import User
    from src.database import engine
    from src.services.db_manager import hash_password

    body = await request.json()
    username  = body.get("username", "").strip()
    password  = body.get("password", "")
    full_name = body.get("full_name", "")
    role      = body.get("role", "student")

    if not username or not password:
        raise HTTPException(status_code=400, detail="Tên đăng nhập và mật khẩu không được để trống")

    with Session(engine) as session:
        existing = session.exec(select(User).where(User.username == username)).first()
        if existing:
            raise HTTPException(status_code=409, detail=f"Tài khoản '{username}' đã tồn tại")

        new_user = User(
            username=username,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role
        )
        session.add(new_user)
        session.commit()
        return {"message": "Tạo tài khoản thành công", "username": username}
