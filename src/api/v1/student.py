from fastapi import APIRouter, Request, HTTPException
from sqlmodel import Session, select
from src.core.database import engine
from src.models.student_risk import StudentRisk, InferenceLog
from src.models.user import User
from src.services.student_service import student_service
from src.services.predictor import get_predictor
from src.core.security import get_current_user, is_student, is_admin
from src.schemas.student import GuestStudentInput, RiskPrediction

router = APIRouter()

@router.get("/history")
async def get_my_history(request: Request):
    """Get prediction history for the logged in user."""
    user_session = get_current_user(request)
    if not user_session:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    with Session(engine) as session:
        # Get user ID first
        db_user = session.exec(select(User).where(User.username == user_session["username"])).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
            
        logs = session.exec(select(InferenceLog).where(InferenceLog.user_id == db_user.id).order_by(InferenceLog.timestamp.desc())).all()
        return logs

@router.get("/query/{student_id}")
async def query_student(student_id: str, request: Request):
    """Query student risk data by student ID (admin/student use)."""
    user_session = get_current_user(request)
    if not user_session:
        raise HTTPException(status_code=401, detail="Vui lòng đăng nhập")

    # Handle Guest Trial Query
    if student_id.startswith("GUEST_"):
        try:
            log_id = int(student_id.replace("GUEST_", ""))
        except ValueError:
            raise HTTPException(status_code=400, detail="Mã guest không hợp lệ")
        
        with Session(engine) as session:
            from src.models.student_risk import InferenceLog
            log = session.get(InferenceLog, log_id)
            if not log:
                raise HTTPException(status_code=404, detail="Không tìm thấy lịch sử dự báo")
            
            # Format to match StudentRisk report
            return {
                "student": {
                    "id_student": f"GUEST_{log.id}",
                    "code_module": log.code_module,
                    "code_presentation": log.code_presentation,
                    "avg_score": log.avg_score,
                    "total_clicks": log.total_clicks,
                    "active_days": 50, # Guest default
                    "n_late": log.n_late,
                    "studied_credits": log.studied_credits,
                    "num_of_prev_attempts": log.num_of_prev_attempts
                },
                "prediction": {
                    "risk_label": log.risk_label,
                    "confidence": log.confidence,
                    "recommendation": get_predictor().get_recommendation(log.risk_label)
                }
            }

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


@router.post("/predict/guest", response_model=RiskPrediction)
async def predict_guest(guest: GuestStudentInput, request: Request):
    """Guest trial prediction logic with saving to DB."""
    predictor = get_predictor()
    
    # Calculate derived VLE features
    active_days = 50
    avg_clicks_day = guest.total_clicks / active_days if guest.total_clicks > 0 else 0
    
    full_data = {
        "gender_num": guest.gender_num,
        "imd_band_num": guest.imd_band_num,
        "education_num": guest.education_num,
        "age_num": guest.age_num,
        "disability_num": guest.disability_num,
        "num_of_prev_attempts": guest.num_of_prev_attempts,
        "studied_credits": guest.studied_credits,
        "reg_days_before": guest.reg_days_before,
        "n_submitted": guest.n_submitted,
        "n_late": guest.n_late,
        "avg_submit_delay": guest.avg_submit_delay,
        "avg_score": guest.avg_score,
        "min_score": guest.min_score,
        "total_clicks": guest.total_clicks,
        "early_registration": 1 if guest.reg_days_before <= -30 else 0,
        "active_days": active_days,
        "avg_clicks_day": avg_clicks_day,
        "max_clicks_day": avg_clicks_day * 2,
        "n_resources": 15,
        "click_density": avg_clicks_day / 15 if avg_clicks_day > 0 else 0,
        "avg_tma_score": guest.avg_score,
        "std_score": (guest.avg_score - guest.min_score) / 2 if guest.avg_score > guest.min_score else 2.0,
        "unregistered": 0
    }
    
    prediction = predictor.predict(full_data)
    
    # Persistence
    user_session = get_current_user(request)
    with Session(engine) as session:
        user_id = None
        if user_session:
            db_user = session.exec(select(User).where(User.username == user_session["username"])).first()
            if db_user: user_id = db_user.id
            
        log = InferenceLog(
            user_id=user_id,
            gender_num=guest.gender_num,
            imd_band_num=guest.imd_band_num,
            education_num=guest.education_num,
            age_num=guest.age_num,
            disability_num=guest.disability_num,
            num_of_prev_attempts=guest.num_of_prev_attempts,
            studied_credits=guest.studied_credits,
            total_clicks=guest.total_clicks,
            avg_score=guest.avg_score,
            min_score=guest.min_score,
            n_submitted=guest.n_submitted,
            n_late=guest.n_late,
            avg_submit_delay=guest.avg_submit_delay,
            reg_days_before=guest.reg_days_before,
            risk_level=prediction["risk_level"],
            risk_label=prediction["risk_label"],
            confidence=prediction["confidence"]
        )
        session.add(log)
        session.commit()
        
    return prediction
