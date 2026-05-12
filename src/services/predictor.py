"""
Services - Logic xử lý chính: Load model và thực hiện dự đoán từ input sinh viên
"""
import os
import joblib
import pandas as pd
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Đường dẫn tới các file model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Nhãn mức độ rủi ro
RISK_LABELS = {
    0: "Low",
    1: "Medium",
    2: "High",
    3: "Very High"
}

RISK_COLORS = {
    0: "#22c55e",   # green
    1: "#f59e0b",   # amber
    2: "#f97316",   # orange
    3: "#ef4444"    # red
}

RECOMMENDATIONS = {
    0: "Sinh viên đang có tiến độ học tập tốt. Tiếp tục duy trì và tham gia đầy đủ các hoạt động học tập.",
    1: "Sinh viên cần chú ý hơn đến việc học. Nên tăng cường tương tác với hệ thống VLE và ôn tập bài thường xuyên hơn.",
    2: "Sinh viên có nguy cơ cao cần được hỗ trợ ngay. Giảng viên nên liên hệ trực tiếp và đề xuất kế hoạch học tập phù hợp.",
    3: "Sinh viên có nguy cơ rất cao bỏ học hoặc trượt môn. Cần can thiệp khẩn cấp từ cố vấn học thuật và gia đình."
}

# Các feature theo đúng thứ tự 23 features khi train model
FEATURE_COLUMNS = [
    'gender_num', 'imd_band_num', 'education_num', 'age_num', 'disability_num', 
    'num_of_prev_attempts', 'studied_credits', 'early_registration', 'reg_days_before', 
    'unregistered', 'total_clicks', 'active_days', 'avg_clicks_day', 'max_clicks_day', 
    'n_resources', 'click_density', 'avg_score', 'min_score', 'std_score', 
    'avg_tma_score', 'n_submitted', 'n_late', 'avg_submit_delay'
]

# Model metrics (Cập nhật theo XGBoost - mô hình tối ưu nhất)
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
    Service để load model XGBoost (hoặc LightGBM) và thực hiện dự đoán mức độ rủi ro sinh viên
    """

    def __init__(self, model_name: str = "xgboost"):
        self.model_name = model_name
        self.model = None
        self.scaler = None
        self._load_model()

    def _load_model(self):
        """Load model và scaler từ file .pkl"""
        try:
            # Check notebooks/models first then root models/
            model_path = os.path.join(BASE_DIR, "notebooks", "models", f"{self.model_name}.pkl")
            scaler_path = os.path.join(BASE_DIR, "notebooks", "models", "scaler.pkl")
            
            if not os.path.exists(model_path):
                model_path = os.path.join(MODELS_DIR, f"{self.model_name}.pkl")
            if not os.path.exists(scaler_path):
                scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")

            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file không tìm thấy: {model_path}")
            if not os.path.exists(scaler_path):
                raise FileNotFoundError(f"Scaler file không tìm thấy: {scaler_path}")

            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            logger.info(f"✅ Đã load model: {self.model_name}")

        except Exception as e:
            logger.error(f"❌ Lỗi load model: {e}")
            raise

    def predict(self, student_data: dict) -> dict:
        """
        Thực hiện dự đoán mức độ rủi ro từ dữ liệu sinh viên
        """
        try:
            # Chuẩn bị input data theo đúng thứ tự feature (23 tính năng)
            input_values = [student_data.get(col, 0) for col in FEATURE_COLUMNS]
            
            # Chuyển thành DataFrame để có feature names (Dùng cho cả XGBoost và LightGBM)
            X = pd.DataFrame([input_values], columns=FEATURE_COLUMNS)

            # Chuẩn hóa dữ liệu
            X_scaled = self.scaler.transform(X)

            # Dự đoán
            risk_level = int(self.model.predict(X_scaled)[0])
            probabilities_raw = self.model.predict_proba(X_scaled)[0]
            confidence = float(probabilities_raw[risk_level] * 100)

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
            logger.error(f"❌ Lỗi predict: {e}")
            raise

    def is_loaded(self) -> bool:
        return self.model is not None and self.scaler is not None

    def get_feature_info(self) -> dict:
        return {
            "model_name": self.model_name.upper(),
            "features": FEATURE_COLUMNS,
            "num_features": len(FEATURE_COLUMNS),
            "classes": list(RISK_LABELS.values()),
            "metrics": MODEL_METRICS.get("XGBoost", {})
        }


# Singleton instance
_predictor: Optional[RiskPredictor] = None


def get_predictor() -> RiskPredictor:
    """Lấy singleton instance của predictor"""
    global _predictor
    if _predictor is None:
        _predictor = RiskPredictor()
    return _predictor
