from fastapi import APIRouter, Request, HTTPException
from sqlmodel import Session, select
from src.core.database import engine
from src.models.student_risk import StudentRisk
from src.services.student_service import student_service
from src.core.security import get_current_user, is_student

router = APIRouter()

@router.get("/query/{student_id}")
async def query_student(student_id: str, request: Request):
    """Query student risk data by student ID (admin/student use)."""
    user_session = get_current_user(request)
    if not user_session:
        raise HTTPException(status_code=401, detail="Vui lòng đăng nhập")

    # Constraint: Student only queries themselves
    if is_student(user_session):
        if user_session["username"] != student_id:
            raise HTTPException(status_code=403, detail="Bạn chỉ có thể xem dữ liệu của chính mình")

    try:
        sid_int = int(student_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Mã sinh viên không hợp lệ")

    report = student_service.get_student_report(sid_int)
    if not report:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
    
    return report
