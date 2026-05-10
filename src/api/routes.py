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

# Templates (để dự phòng)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "src", "web", "templates"))


# ─── Web Routes ──────────────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse, tags=["Web"])
async def dashboard(request: Request):
    """Trang chủ - Dashboard hệ thống"""
    index_path = os.path.join(BASE_DIR, "src", "web", "templates", "index.html")
    return FileResponse(index_path)


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
    
    Trả về:
    - **risk_level**: 0=Low, 1=Medium, 2=High, 3=Very High
    - **risk_label**: Nhãn mức độ rủi ro
    - **confidence**: Độ tin cậy dự đoán (%)
    - **probabilities**: Xác suất cho từng mức rủi ro
    - **recommendation**: Khuyến nghị hành động cụ thể
    """
    try:
        predictor = get_predictor()
        result = predictor.predict(student.model_dump())
        return RiskPrediction(**result)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=f"Model chưa được load: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi dự đoán: {str(e)}")


@router.post("/api/predict/batch", tags=["Prediction"])
async def predict_batch(students: list[StudentInput]):
    """Dự đoán hàng loạt cho nhiều sinh viên"""
    if len(students) > 100:
        raise HTTPException(status_code=400, detail="Tối đa 100 sinh viên mỗi batch")
    try:
        predictor = get_predictor()
        results = [predictor.predict(s.model_dump()) for s in students]
        return {"count": len(results), "predictions": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
