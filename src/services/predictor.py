import os
import joblib
import pandas as pd
from typing import Optional, Any, Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Priority: notebooks/models/ (where training scripts save) > models/ (deployment dir)
SEARCH_DIRS = [
    os.path.join(BASE_DIR, "notebooks", "models"),
    os.path.join(BASE_DIR, "models"),
    os.path.join(BASE_DIR, "data", "models")
]

# Risk level labels
RISK_LABELS: Dict[int, str] = {
    0: "Low",
    1: "Medium",
    2: "High",
    3: "Very High"
}

# Color codes for visualization
RISK_COLORS: Dict[int, str] = {
    0: "#22c55e",   # green
    1: "#f59e0b",   # amber
    2: "#f97316",   # orange
    3: "#ef4444"    # red
}

# Human-readable recommendations
RECOMMENDATIONS: Dict[int, str] = {
    0: "Sinh viên đang có tiến độ học tập tốt. Tiếp tục duy trì và tham gia đầy đủ các hoạt động học tập.",
    1: "Sinh viên cần chú ý hơn đến việc học. Nên tăng cường tương tác với hệ thống VLE và ôn tập bài thường xuyên hơn.",
    2: "Sinh viên có nguy cơ cao cần được hỗ trợ ngay. Giảng viên nên liên hệ trực tiếp và đề xuất kế hoạch học tập phù hợp.",
    3: "Sinh viên có nguy cơ rất cao bỏ học hoặc trượt môn. Cần can thiệp khẩn cấp từ cố vấn học thuật và gia đình."
}

# Feature columns in exact training order
FEATURE_COLUMNS: List[str] = [
    'gender_num', 'imd_band_num', 'education_num', 'age_num', 'disability_num', 
    'num_of_prev_attempts', 'studied_credits', 'early_registration', 'reg_days_before', 
    'unregistered', 'total_clicks', 'active_days', 'avg_clicks_day', 'max_clicks_day', 
    'n_resources', 'click_density', 'avg_score', 'min_score', 'std_score', 
    'avg_tma_score', 'n_submitted', 'n_late', 'avg_submit_delay'
]

# Model benchmarks
MODEL_METRICS = {
    "XGBoost": {
        "f1_macro": 0.8465,
        "balanced_accuracy": 0.8906,
        "auc": 0.9868,
        "accuracy": 0.9271
    }
}


class RiskPredictor:
    """
    RiskPredictor handles loading ML models and scalers to perform student risk stratification.
    """

    def __init__(self, model_name: str = "xgboost"):
        self.model_name = model_name
        self.model: Any = None
        self.scaler: Any = None
        self._load_model()

    def _find_file(self, filename: str) -> Optional[str]:
        for directory in SEARCH_DIRS:
            path = os.path.join(directory, filename)
            if os.path.exists(path):
                return path
        return None

    def _load_model(self):
        """Load the model and scaler using prioritized search paths."""
        try:
            model_file = f"{self.model_name}.pkl"
            scaler_file = "scaler.pkl"

            model_path = self._find_file(model_file)
            scaler_path = self._find_file(scaler_file)

            if not model_path:
                raise FileNotFoundError(f"Model file '{model_file}' not found in any search directories: {SEARCH_DIRS}")
            if not scaler_path:
                raise FileNotFoundError(f"Scaler file '{scaler_file}' not found in any search directories: {SEARCH_DIRS}")

            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            logger.info(f"✅ Successfully loaded model: {self.model_name} from {model_path}")

        except Exception as e:
            logger.error(f"❌ Failed to load model {self.model_name}: {e}")
            # Don't raise here to allow application to start even if model load fails (graceful degradation)
            self.model = None
            self.scaler = None

    def predict(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform risk prediction from student feature dictionary."""
        if not self.is_loaded():
            raise RuntimeError("Model or Scaler not loaded. Check logs for initialization errors.")

        try:
            # Prepare input array in exact feature order
            input_values = [student_data.get(col, 0) for col in FEATURE_COLUMNS]
            
            # Wrap in DataFrame to maintain feature names
            X = pd.DataFrame([input_values], columns=FEATURE_COLUMNS)

            # Standardize features
            X_scaled = self.scaler.transform(X)

            # Perform inference
            risk_level = int(self.model.predict(X_scaled)[0])
            probabilities_raw = self.model.predict_proba(X_scaled)[0]
            confidence = float(probabilities_raw[risk_level] * 100)

            # Format class probabilities
            probabilities = {
                RISK_LABELS[i]: round(float(p) * 100, 2)
                for i, p in enumerate(probabilities_raw)
            }

            return {
                "risk_level": risk_level,
                "risk_label": RISK_LABELS[risk_level],
                "confidence": round(confidence, 2),
                "probabilities": probabilities,
                "recommendation": RECOMMENDATIONS[risk_level],
                "model_used": self.model_name.upper(),
                "risk_color": RISK_COLORS[risk_level]
            }

        except Exception as e:
            logger.error(f"❌ Prediction error: {e}")
            raise

    def is_loaded(self) -> bool:
        """Check if both model and scaler are initialized."""
        return self.model is not None and self.scaler is not None

    def get_recommendation(self, risk: Any) -> str:
        """Retrieve action recommendation based on risk level or label."""
        if isinstance(risk, int):
            return RECOMMENDATIONS.get(risk, "Không có khuyến nghị.")
        
        if isinstance(risk, str):
            for level, label in RISK_LABELS.items():
                if label.lower() == risk.lower():
                    return RECOMMENDATIONS.get(level, "Không có khuyến nghị.")
        
        return "Không có khuyến nghị."

    def get_feature_info(self) -> Dict[str, Any]:
        """Expose model metadata for API info endpoints."""
        return {
            "model_name": self.model_name.upper(),
            "features": FEATURE_COLUMNS,
            "num_features": len(FEATURE_COLUMNS),
            "classes": list(RISK_LABELS.values()),
            "metrics": MODEL_METRICS.get("XGBoost", {})
        }


# Singleton pattern
_predictor: Optional[RiskPredictor] = None


def get_predictor() -> RiskPredictor:
    """Access the RiskPredictor singleton instance."""
    global _predictor
    if _predictor is None:
        _predictor = RiskPredictor()
    return _predictor
