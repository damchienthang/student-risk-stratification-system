# Implement business logic services (Auth, Predictor, Email warning, and Admin stats)
import os
import joblib
import pandas as pd
from typing import Optional, Any, Dict, List
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Giải quyết đường dẫn thư mục
from src.core.config import settings

SEARCH_DIRS = settings.MODEL_SEARCH_DIRS

# Nhãn các mức độ rủi ro
RISK_LABELS: Dict[int, str] = {
    0: "Low",
    1: "Medium",
    2: "High",
    3: "Very High"
}

# Mã màu cho việc trực quan hóa
RISK_COLORS: Dict[int, str] = {
    0: "#22c55e",   # xanh lá
    1: "#f59e0b",   # hổ phách
    2: "#f97316",   # cam
    3: "#ef4444"    # đỏ
}

# Các khuyến nghị hành động thân thiện với người dùng
RECOMMENDATIONS: Dict[int, str] = {
    0: "Sinh viên đang có tiến độ học tập tốt. Tiếp tục duy trì và tham gia đầy đủ các hoạt động học tập.",
    1: "Sinh viên cần chú ý hơn đến việc học. Nên tăng cường tương tác với hệ thống VLE và ôn tập bài thường xuyên hơn.",
    2: "Sinh viên có nguy cơ cao cần được hỗ trợ ngay. Giảng viên nên liên hệ trực tiếp và đề xuất kế hoạch học tập phù hợp.",
    3: "Sinh viên có nguy cơ rất cao bỏ học hoặc trượt môn. Cần can thiệp khẩn cấp từ cố vấn học tập và gia đình."
}

# Các cột thuộc tính (features) theo đúng thứ tự huấn luyện mô hình
FEATURE_COLUMNS: List[str] = [
    'gender_num', 'imd_band_num', 'education_num', 'age_num', 'disability_num', 
    'num_of_prev_attempts', 'studied_credits', 'early_registration', 'reg_days_before', 
    'unregistered', 'total_clicks', 'active_days', 'avg_clicks_day', 'max_clicks_day', 
    'n_resources', 'click_density', 'avg_score', 'min_score', 'std_score', 
    'avg_tma_score', 'n_submitted', 'n_late', 'avg_submit_delay'
]

# Giá trị mặc định "trung tính" cho các đặc trưng (dựa trên trung bình cộng của quần thể OULAD)
# Điều này giúp tránh thiên kiến khi chỉ cung cấp dữ liệu một phần
FEATURE_DEFAULTS: Dict[str, Any] = {
    'gender_num': 0, 'imd_band_num': 5, 'education_num': 2, 'age_num': 0, 'disability_num': 0,
    'num_of_prev_attempts': 0, 'studied_credits': 60,
    'early_registration': 1, 'reg_days_before': -90, 'unregistered': 0,
    'total_clicks': 500, 'active_days': 50, 'avg_clicks_day': 10.0, 'max_clicks_day': 100,
    'n_resources': 15, 'click_density': 2.0,
    'avg_score': 65.0, 'min_score': 45.0, 'std_score': 12.0, 'avg_tma_score': 68.0,
    'n_submitted': 4, 'n_late': 0, 'avg_submit_delay': -2.0
}

# Chỉ số hiệu năng của mô hình
MODEL_METRICS = {
    "LightGBM": {
        "f1_macro": 0.8403,        # Validation set
        "balanced_accuracy": 0.8701,
        "auc": 0.9868,
        "accuracy": 0.9208,
        "test_f1": 0.8445,         # Test set
        "test_auc": 0.9887,
        "test_accuracy": 0.93
    },
    "XGBoost": {
        "f1_macro": 0.8356,
        "balanced_accuracy": 0.8804,
        "auc": 0.9872,
        "accuracy": 0.9193
    },
    "Random Forest": {
        "f1_macro": 0.8331,
        "balanced_accuracy": 0.8972,
        "auc": 0.9845,
        "accuracy": 0.9155
    },
    "Logistic Regression": {
        "f1_macro": 0.7041,
        "balanced_accuracy": 0.8261,
        "auc": 0.9624,
        "accuracy": 0.8385
    }
}


class RiskPredictor:
    """
    Nạp mô hình ML và bộ chuẩn hóa (scaler) để thực hiện phân tầng rủi ro sinh viên.
    """

    def __init__(self, model_name: str = "lightgbm"):
        self.model_name = model_name
        self.model: Any = None
        self.scaler: Any = None
        self._load_model()

    def _find_file(self, filename: str) -> Optional[str]:
        """Tìm kiếm file trong các thư mục ưu tiên."""
        for directory in SEARCH_DIRS:
            path = os.path.join(directory, filename)
            if os.path.exists(path):
                return path
        return None

    def _load_model(self):
        """Nạp mô hình và bộ chuẩn hóa sử dụng các đường dẫn tìm kiếm ưu tiên."""
        try:
            model_file = f"{self.model_name}.pkl"
            scaler_file = "scaler.pkl"

            model_path = self._find_file(model_file)
            scaler_path = self._find_file(scaler_file)

            if not model_path:
                raise FileNotFoundError(f"Không tìm thấy file mô hình '{model_file}' trong các thư mục: {SEARCH_DIRS}")
            if not scaler_path:
                raise FileNotFoundError(f"Không tìm thấy file chuẩn hóa '{scaler_file}' trong các thư mục: {SEARCH_DIRS}")

            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            logger.info(f"✅ Nạp mô hình thành công: {self.model_name} từ {model_path}")

        except Exception as e:
            logger.error(f"❌ Lỗi khi nạp mô hình {self.model_name}: {e}")
            # Không raise lỗi ở đây để ứng dụng vẫn khởi động được ngay cả khi nạp mô hình thất bại
            self.model = None
            self.scaler = None

    def predict(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Thực hiện dự báo rủi ro từ từ điển các đặc trưng sinh viên."""
        if not self.is_loaded():
            raise RuntimeError("Mô hình hoặc Bộ chuẩn hóa chưa được nạp. Kiểm tra nhật ký để biết lỗi khởi tạo.")

        try:
            # Chuẩn bị mảng đầu vào theo đúng thứ tự đặc trưng với các giá trị mặc định thông minh
            input_values = []
            for col in FEATURE_COLUMNS:
                val = student_data.get(col)
                if val is None:
                    val = FEATURE_DEFAULTS.get(col, 0)
                input_values.append(val)
            
            # Đưa vào DataFrame để giữ tên đặc trưng
            X = pd.DataFrame([input_values], columns=FEATURE_COLUMNS)

            # Chuẩn hóa các đặc trưng
            X_scaled = self.scaler.transform(X)

            # Thực hiện dự báo
            risk_level = int(self.model.predict(X_scaled)[0])
            probabilities_raw = self.model.predict_proba(X_scaled)[0]
            confidence = float(probabilities_raw[risk_level] * 100)

            # Định dạng xác suất các lớp rủi ro
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
            logger.error(f"❌ Lỗi dự báo: {e}")
            raise

    def is_loaded(self) -> bool:
        """Kiểm tra xem cả mô hình và bộ chuẩn hóa đã được khởi tạo hay chưa."""
        return self.model is not None and self.scaler is not None

    def get_recommendation(self, risk: Any) -> str:
        """Lấy khuyến nghị hành động dựa trên mức độ rủi ro hoặc nhãn."""
        if isinstance(risk, int):
            return RECOMMENDATIONS.get(risk, "Không có khuyến nghị.")
        
        if isinstance(risk, str):
            for level, label in RISK_LABELS.items():
                if label.lower() == risk.lower():
                    return RECOMMENDATIONS.get(level, "Không có khuyến nghị.")
        
        return "Không có khuyến nghị."

    def get_feature_info(self) -> Dict[str, Any]:
        """Cung cấp metadata của mô hình cho các endpoint API thông tin."""
        return {
            "model_name": self.model_name.upper(),
            "features": FEATURE_COLUMNS,
            "num_features": len(FEATURE_COLUMNS),
            "classes": list(RISK_LABELS.values()),
            "metrics": MODEL_METRICS.get("LightGBM", {})
        }


# Mẫu thiết kế Singleton
_predictor: Optional[RiskPredictor] = None


def get_predictor() -> RiskPredictor:
    """Truy cập thực thể RiskPredictor duy nhất (singleton)."""
    global _predictor
    if _predictor is None:
        _predictor = RiskPredictor()
    return _predictor
