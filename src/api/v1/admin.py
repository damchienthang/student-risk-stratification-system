from fastapi import APIRouter, Request, HTTPException, Query
from sqlmodel import Session, select, String
from sqlalchemy import func
from typing import Any, cast

from src.core.database import engine
from src.core.security import get_current_user, is_admin, hash_password
from src.services.admin_service import admin_service
from src.models.user import User
from src.models.student_risk import StudentRisk
from src.services.email_service import send_warning_email

router = APIRouter()

@router.get("/stats")
async def get_analytics(
    request: Request,
    module: str = Query("BBB"),
    semester: str = Query("2014J"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str = Query(None),
    risk: str = Query("all"),
    source: str = Query("official")
):
    user = get_current_user(request)
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Unauthorized")

    with Session(engine) as session:
        # Handle Official Students
        stats_data = admin_service.get_dashboard_stats(module, semester, risk)
        
        statement = select(StudentRisk)
        if module != "all": statement = statement.where(StudentRisk.code_module == module)
        if semester != "all": statement = statement.where(StudentRisk.code_presentation == semester)
        if risk != "all": statement = statement.where(StudentRisk.risk_label == risk)
        if search: statement = statement.where(func.cast(StudentRisk.id_student, String).like(f"%{search}%"))
        
        total_count = len(session.exec(statement).all())
        students = session.exec(statement.order_by(StudentRisk.risk_level.desc()).offset((page-1)*limit).limit(limit)).all()
        
        student_list = [{
            "id": s.id_student,
            "score": round(s.avg_score, 2),
            "clicks": s.total_clicks,
            "risk": s.risk_label,
            "risk_level": s.risk_level,
            "code_module": s.code_module,
            "code_presentation": s.code_presentation
        } for s in students]

        return {
            "summary": {
                "total_students": stats_data["summary"].total if stats_data["summary"] else 0,
                "avg_clicks": round(float(stats_data["summary"].avg_clicks), 1) if stats_data["summary"] and stats_data["summary"].avg_clicks else 0,
                "avg_score": round(float(stats_data["summary"].avg_score), 2) if stats_data["summary"] and stats_data["summary"].avg_score else 0
            },
            "risk_distribution": [stats_data["risk_distribution"].get(i, 0) for i in range(4)],
            "top_at_risk": stats_data["urgent_intervention"],
            "all_students": student_list,
            "pagination": {"page": page, "limit": limit, "total_records": total_count, "total_pages": (total_count + limit - 1) // limit}
        }

@router.get("/users")
async def list_users(request: Request):
    user_session = get_current_user(request)
    if not is_admin(user_session):
        raise HTTPException(status_code=403, detail="Unauthorized")

    with Session(engine) as session:
        users = session.exec(select(User).order_by(User.id.desc())).all()
        result = []
        for u in users:
            # Try to get latest risk if external/student
            latest_risk = "N/A"
            if u.role == "student":
                # Check official data
                try:
                    sid = int(u.username)
                    official = session.exec(select(StudentRisk).where(StudentRisk.id_student == sid)).first()
                    if official: latest_risk = official.risk_label
                except: pass

            result.append({
                "id": u.id,
                "username": u.username,
                "full_name": u.full_name,
                "email": u.email,
                "role": u.role,
                "is_external": u.is_external,
                "is_active": u.is_active,
                "latest_risk": latest_risk
            })
        return {"users": result}

@router.post("/users/{user_id}/toggle-status")
async def toggle_user_status(user_id: int, request: Request):
    user_session = get_current_user(request)
    if not is_admin(user_session):
        raise HTTPException(status_code=403, detail="Unauthorized")

    with Session(engine) as session:
        db_user = session.get(User, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent locking self
        if db_user.username == user_session["username"]:
            raise HTTPException(status_code=400, detail="Cannot lock yourself")

        db_user.is_active = not db_user.is_active
        session.add(db_user)
        session.commit()
        return {"status": "success", "is_active": db_user.is_active}

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, request: Request):
    user_session = get_current_user(request)
    if not is_admin(user_session):
        raise HTTPException(status_code=403, detail="Unauthorized")

    with Session(engine) as session:
        db_user = session.get(User, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if db_user.username == user_session["username"]:
            raise HTTPException(status_code=400, detail="Cannot delete yourself")

        session.delete(db_user)
        # Also clean up their logs if needed, or keep them as orphan? 
        # Usually delete or set user_id to null.
        session.commit()
        return {"status": "success"}

@router.get("/users/{user_id}/details")
async def get_user_details(user_id: int, request: Request):
    user_session = get_current_user(request)
    if not is_admin(user_session):
        raise HTTPException(status_code=403, detail="Unauthorized")

    with Session(engine) as session:
        db_user = session.get(User, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "user": db_user,
            "history": []
        }

@router.post("/users")
async def create_user(request: Request):
    user = get_current_user(request)
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Unauthorized")

    body = await request.json()
    username = body.get("username", "").strip()
    password = body.get("password", "")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Thiếu thông tin")

    with Session(engine) as session:
        if session.exec(select(User).where(User.username == username)).first():
            raise HTTPException(status_code=409, detail="Tài khoản đã tồn tại")
        
        new_user = User(
            username=username,
            password_hash=hash_password(password),
            full_name=body.get("full_name", ""),
            role=body.get("role", "student")
        )
        session.add(new_user)
        session.commit()
        return {"message": "Success"}

@router.post("/send-email")
async def send_student_warning_email(request: Request):
    """
    Gửi email cảnh báo rủi ro học tập cho sinh viên (dùng cho Demo).
    Body: { to_email, student_id, recommendation, risk_label }
    """
    user = get_current_user(request)
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    body = await request.json()
    to_email = body.get("to_email", "").strip()
    student_id = str(body.get("student_id", "")).strip()
    recommendation = body.get("recommendation", "Không có khuyến nghị cụ thể.")
    risk_label = body.get("risk_label", "Unknown")
    
    if not to_email or not student_id:
        raise HTTPException(status_code=400, detail="Thiếu thông tin email hoặc mã sinh viên.")

    success = send_warning_email(
        to_email=to_email,
        student_id=student_id,
        recommendation=recommendation,
        risk_label=risk_label
    )
    
    if success:
        return {"status": "success", "message": f"Đã gửi email cảnh báo tới {to_email} thành công."}
    else:
        raise HTTPException(status_code=500, detail="Gửi email thất bại. Vui lòng kiểm tra lại cấu hình SMTP trong file .env.")
