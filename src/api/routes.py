"""
API Routes - Định nghĩa các API endpoint (FastAPI)
Các đường dẫn nhận request dự đoán rủi ro học tập sinh viên
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import os

from src.schemas.student import StudentInput, GuestStudentInput, RiskPrediction, HealthResponse, ModelInfoResponse
from src.services.predictor import get_predictor
from src.services.db_manager import get_db_manager
from src.api.auth_routes import get_current_user

# Khởi tạo router
router = APIRouter()

# Templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "src", "web", "templates"))


# ─── Web Routes ──────────────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse, tags=["Web"])
async def dashboard(request: Request):
    """Trang chủ - Hiển thị Landing Page"""
    user = get_current_user(request)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user
    })


@router.get("/about", response_class=HTMLResponse, tags=["Web"])
async def about_page(request: Request):
    """Trang Giới thiệu - Về chúng tôi"""
    user = get_current_user(request)
    return templates.TemplateResponse("about.html", {
        "request": request,
        "user": user
    })


# ─── API Routes ──────────────────────────────────────────────────────────────

@router.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Kiểm tra trạng thái hoạt động của hệ thống"""
    try:
        predictor = get_predictor()
        return HealthResponse(
            status="healthy",
            model_loaded=predictor.is_loaded(),
            model_name="XGBoost",
            version="1.0.0"
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service không khả dụng: {str(e)}")


@router.get("/api/models/info", response_model=ModelInfoResponse, tags=["Model"])
async def get_model_info():
    """Thông tin chi tiết về model đang sử dụng"""
    try:
        predictor = get_predictor()
        info = predictor.get_feature_info()
        return ModelInfoResponse(**info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/predict", response_model=RiskPrediction, tags=["Prediction"])
async def predict_risk(student: StudentInput):
    """
    Dự đoán mức độ rủi ro học tập của sinh viên chính thức.
    """
    try:
        predictor = get_predictor()
        result = predictor.predict(student.model_dump())
        return RiskPrediction(**result)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Model chưa được load: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi dự đoán: {str(e)}")


@router.post("/api/predict/guest", response_model=RiskPrediction, tags=["Prediction"])
async def predict_risk_guest(guest: GuestStudentInput):
    """
    Dự đoán mức độ rủi ro học tập cho sinh viên tự do (Guest).
    Kết quả sẽ được lưu vào bảng inference_logs.
    """
    try:
        predictor = get_predictor()
        # Chuyển đổi từ GuestInput (8 fields) sang FullInput (23 fields) bằng cách điền giá trị mặc định
        full_data = {
            # User provided
            "gender_num": guest.gender_num,
            "imd_band_num": guest.imd_band_num,
            "education_num": guest.education_num,
            "age_num": guest.age_num,
            "disability_num": 0,  # Mặc định không khuyết tật
            "num_of_prev_attempts": guest.num_of_prev_attempts,
            "studied_credits": guest.studied_credits,
            "total_clicks": guest.total_clicks,
            "avg_score": guest.avg_score,

            # Default values for missing features (based on dataset averages/medians)
            "early_registration": 1,
            "reg_days_before": -30,
            "unregistered": 0,
            "active_days": 50,
            "avg_clicks_day": guest.total_clicks / 50 if guest.total_clicks > 0 else 0,
            "max_clicks_day": 100,
            "n_resources": 15,
            "click_density": 2.5,
            "min_score": guest.avg_score - 10 if guest.avg_score > 10 else 0,
            "std_score": 5.0,
            "avg_tma_score": guest.avg_score,
            "n_submitted": 5,
            "n_late": 0,
            "avg_submit_delay": 0.5
        }

        result = predictor.predict(full_data)

        # Lưu vào InferenceLogs
        dbm = get_db_manager()
        dbm.save_inference_log({
            "gender_num": guest.gender_num,
            "imd_band_num": guest.imd_band_num,
            "education_num": guest.education_num,
            "age_num": guest.age_num,
            "disability_num": 0,
            "num_of_prev_attempts": guest.num_of_prev_attempts,
            "studied_credits": guest.studied_credits,
            "total_clicks": guest.total_clicks,
            "avg_score": guest.avg_score,
            "risk_level": result["risk_level"],
            "risk_label": result["risk_label"],
            "confidence": result["confidence"]
        })

        return RiskPrediction(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi dự đoán khách: {str(e)}")


@router.get("/api/query/{student_id}", tags=["Query"])
async def query_student_by_id(student_id: str, request: Request):
    """Truy vấn thông tin chi tiết và dự báo cho một sinh viên cụ thể (Hỗ trợ cả Guest ID)"""
    user = get_current_user(request)

    predictor = get_predictor()
    dbm = get_db_manager()
    if student_id.startswith("GUEST_"):
        try:
            log_id = int(student_id.split("_")[1])
            from sqlmodel import Session, select
            from src.models.student_risk import InferenceLog
            from src.database import engine
            with Session(engine) as session:
                log = session.exec(select(InferenceLog).where(InferenceLog.id == log_id)).first()
                if not log:
                    raise HTTPException(status_code=404, detail="Không tìm thấy lịch sử dự báo khách")

                student_data = {
                    "id_student": f"GUEST_{log.id}",
                    "code_module": "Guest",
                    "code_presentation": log.timestamp,
                    "avg_score": log.avg_score,
                    "total_clicks": log.total_clicks,
                    "active_days": 0,
                    "n_late": 0,
                    "studied_credits": log.studied_credits,
                    "num_of_prev_attempts": log.num_of_prev_attempts,
                    "reg_days_before": 0
                }
                prediction = {
                    "risk_level": log.risk_level,
                    "risk_label": log.risk_label,
                    "confidence": log.confidence,
                    "recommendation": predictor.get_recommendation(log.risk_label)
                }
                return {"student": student_data, "prediction": prediction}
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=400, detail="Mã Guest không hợp lệ")

    # Case 2: Standard Student ID
    try:
        sid_int = int(student_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Mã sinh viên phải là số hoặc mã Guest (GUEST_x)")

    student = dbm.get_student_by_id(sid_int)
    if not student:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy sinh viên #{student_id}")

    features = dbm.get_student_features(sid_int)
    if features is None:
        # Fallback to stored data if feature method not available
        features = student.model_dump()

    result = predictor.predict(features)
    return {"student": student.model_dump(), "prediction": result}


