"""
API Routes - Định nghĩa các API endpoint (FastAPI)
Các đường dẫn nhận request dự đoán rủi ro học tập sinh viên
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import os

from src.schemas.student import StudentInput, RiskPrediction, HealthResponse, ModelInfoResponse
from src.services.predictor import get_predictor

# Khởi tạo router
router = APIRouter()

# Templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "src", "web", "templates"))


# ─── Web Routes ──────────────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse, tags=["Web"])
async def dashboard(request: Request):
    """Trang chủ - Hiển thị Landing Page"""
    from src.api.auth_routes import get_current_user
    user = get_current_user(request)
    
    return templates.TemplateResponse("index.html", {
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
            model_name="LightGBM",
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
    Dự đoán mức độ rủi ro học tập của sinh viên.
    """
    try:
        predictor = get_predictor()
        result = predictor.predict(student.model_dump())
        return RiskPrediction(**result)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Model chưa được load: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi dự đoán: {str(e)}")


@router.get("/api/query/{student_id}", tags=["Query"])
async def query_student_by_id(student_id: int):
    """Truy vấn thông tin chi tiết và dự báo cho một sinh viên cụ thể"""
    from src.services.db_manager import get_db_manager
    
    dbm = get_db_manager()
    student = dbm.get_student_by_id(student_id)

    if not student:
        raise HTTPException(status_code=404, detail=f"Student ID {student_id} not found")

    # Convert SQLModel object to dict
    student_dict = student.model_dump()
    
    return {
        "student": student_dict,
        "prediction": {
            "risk_level": student.risk_level,
            "risk_label": student.risk_label,
            "recommendation": get_recommendation(student.risk_level)
        }
    }

def get_recommendation(risk_level: int) -> str:
    recs = [
        "Sinh viên đang có tiến độ học tập tốt. Tiếp tục duy trì và tham gia đầy đủ các hoạt động học tập.",
        "Sinh viên cần chú ý hơn đến việc học. Nên tăng cường tương tác với hệ thống VLE.",
        "Sinh viên có nguy cơ cao cần được hỗ trợ ngay. Giảng viên nên liên hệ trực tiếp.",
        "Sinh viên có nguy cơ rất cao bỏ học. Cần can thiệp khẩn cấp từ cố vấn học thuật."
    ]
    return recs[risk_level] if 0 <= risk_level < len(recs) else "Không có khuyến nghị."
