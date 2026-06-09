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
                    "gender_num": log.gender_num,
                    "imd_band_num": log.imd_band_num,
                    "education_num": log.education_num,
                    "age_num": log.age_num,
                    "disability_num": log.disability_num,
                    "num_of_prev_attempts": log.num_of_prev_attempts,
                    "studied_credits": log.studied_credits,
                    "total_clicks": log.total_clicks,
                    "attendance_rate": 80,
                    "avg_clicks_day": log.total_clicks / 48 if log.total_clicks > 0 else 0,
                    "max_clicks_day": (log.total_clicks / 48) * 2 if log.total_clicks > 0 else 0,
                    "n_resources": 15,
                    "click_density": (log.total_clicks / 50) / 15 if log.total_clicks > 0 else 0,
                    "avg_score": log.avg_score,
                    "min_score": log.min_score,
                    "std_score": (log.avg_score - log.min_score) / 2 if log.avg_score > log.min_score else 2.0,
                    "avg_tma_score": log.avg_score,
                    "n_submitted": log.n_submitted,
                    "n_late": log.n_late,
                    "avg_submit_delay": log.avg_submit_delay,
                    "reg_days_before": log.reg_days_before,
                    "early_registration": 1 if log.reg_days_before <= -30 else 0,
                    "unregistered": 0,
                    "final_result": "Guest Trial"
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
    
    # Calculate derived VLE features (Day 60 milestone)
    active_days = int((guest.attendance_rate / 100.0) * 60)
    if guest.total_clicks > 0 and active_days == 0:
        active_days = 1
    
    avg_clicks_day = guest.total_clicks / active_days if active_days > 0 else 0
    std_score = guest.std_score_eval
    
    full_data = {
        "gender_num": guest.gender_num,
        "imd_band_num": guest.imd_band_num,
        "education_num": guest.education_num,
        "age_num": guest.age_num,
        "disability_num": guest.disability_num,
        "num_of_prev_attempts": guest.num_of_prev_attempts,
        "studied_credits": 60, # Removed from UI, fixed internally
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
        "std_score": std_score,
        "unregistered": 0
    }
    
    prediction = predictor.predict(full_data)
    
    # Try to see if user is logged in
    user_id = None
    try:
        user_session = get_current_user(request)
        if user_session:
            with Session(engine) as session:
                db_user = session.exec(select(User).where(User.username == user_session["username"])).first()
                if db_user:
                    user_id = db_user.id
    except Exception:
        pass

    # Save to database immediately
    try:
        with Session(engine) as session:
            log = InferenceLog(
                user_id=user_id,
                code_module="Guest",
                code_presentation="Guest",
                gender_num=guest.gender_num,
                imd_band_num=guest.imd_band_num,
                education_num=guest.education_num,
                age_num=guest.age_num,
                disability_num=guest.disability_num,
                num_of_prev_attempts=guest.num_of_prev_attempts,
                studied_credits=60, # Removed from UI
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
            session.refresh(log)
            prediction["log_id"] = log.id
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to instantly save inference log: {e}")

    return prediction

@router.post("/persist-trial")
async def persist_trial(request: Request, data: dict):
    user_session = get_current_user(request)
    if not user_session:
        return {"status": "ignored", "reason": "user not logged in"}
    
    with Session(engine) as session:
        db_user = session.exec(select(User).where(User.username == user_session["username"])).first()
        if not db_user: 
            return {"status": "error", "reason": "user not found"}
            
        log_id = data.get("log_id")
        if log_id:
            # Look up the existing instantly-saved log to link it directly to the user
            log = session.get(InferenceLog, log_id)
            if log:
                log.user_id = db_user.id
                session.add(log)
                session.commit()
                return {"status": "success", "log_id": log.id, "linked": True}
        
        # Fallback: Create a new InferenceLog if no log_id was provided or found
        log = InferenceLog(
            user_id=db_user.id,
            code_module="Guest",
            code_presentation="Guest",
            gender_num=data.get("gender_num", 0),
            imd_band_num=data.get("imd_band_num", 5),
            education_num=data.get("education_num", 2),
            age_num=data.get("age_num", 0),
            disability_num=data.get("disability_num", 0),
            num_of_prev_attempts=data.get("num_of_prev_attempts", 0),
            studied_credits=data.get("studied_credits", 60),
            total_clicks=data.get("total_clicks", 600),
            avg_score=data.get("avg_score", 70.0),
            min_score=data.get("min_score", 50.0),
            n_submitted=data.get("n_submitted", 4),
            n_late=data.get("n_late", 0),
            avg_submit_delay=data.get("avg_submit_delay", 0.0),
            reg_days_before=data.get("reg_days_before", -90),
            risk_level=data.get("risk_level", 0),
            risk_label=data.get("risk_label", "Low"),
            confidence=data.get("confidence", 0.0)
        )
        session.add(log)
        session.commit()
        return {"status": "success", "log_id": log.id, "linked": False}
