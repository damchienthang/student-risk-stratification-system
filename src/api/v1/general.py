from fastapi import APIRouter, HTTPException
from src.schemas.student import HealthResponse, ModelInfoResponse
from src.services.predictor import get_predictor

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    try:
        predictor = get_predictor()
        return HealthResponse(
            status="healthy",
            model_loaded=predictor.is_loaded(),
            model_name="XGBoost",
            version="2.0.0"
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.get("/models/info", response_model=ModelInfoResponse)
async def get_model_info():
    try:
        predictor = get_predictor()
        return ModelInfoResponse(**predictor.get_feature_info())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
