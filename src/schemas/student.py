"""
Schemas - Định nghĩa kiểu dữ liệu đầu vào/đầu ra (Pydantic)
"""
from pydantic import BaseModel, Field
from typing import Optional


class GuestStudentInput(BaseModel):
    """Dữ liệu chi tiết để sinh viên tự đánh giá rủi ro (Guest Trial)"""
    # Nhân khẩu học
    gender_num: int = Field(0, description="Giới tính: 0=M, 1=F")
    imd_band_num: int = Field(5, description="Chỉ số kinh tế (0-9)")
    education_num: int = Field(2, description="Học vấn (0-4)")
    age_num: int = Field(0, description="Tuổi (0-2)")
    disability_num: int = Field(0, description="Khuyết tật (0-1)")
    
    # Lộ trình & Lịch sử
    num_of_prev_attempts: int = Field(0, description="Số lần thi lại")
    studied_credits: int = Field(60, description="Số tín chỉ")
    reg_days_before: int = Field(-90, description="Số ngày đăng ký trước khi bắt đầu")
    
    # Kỷ luật nộp bài
    n_submitted: int = Field(4, description="Số bài đã nộp")
    n_late: int = Field(0, description="Số bài nộp muộn")
    avg_submit_delay: float = Field(-2.0, description="Độ trễ nộp bài trung bình")
    
    # Năng lực học tập
    avg_score: float = Field(70.0, description="Điểm trung bình")
    min_score: float = Field(50.0, description="Điểm thấp nhất")
    
    # VLE (Giữ lại cuối cùng)
    total_clicks: int = Field(500, description="Tổng số click")


class StudentInput(BaseModel):
    """Format dữ liệu sinh viên cần truyền vào để dự đoán rủi ro học tập (23 features)"""

    # Demographics
    gender_num: int = Field(..., ge=0, le=1, description="Giới tính: 0=M, 1=F")
    imd_band_num: int = Field(..., ge=0, le=9, description="Chỉ số kinh tế xã hội")
    education_num: int = Field(..., ge=0, le=4, description="Trình độ học vấn")
    age_num: int = Field(..., ge=0, le=2, description="Nhóm tuổi")
    disability_num: int = Field(..., ge=0, le=1, description="Khuyết tật: 0=Không, 1=Có")
    num_of_prev_attempts: int = Field(..., ge=0, description="Số lần đăng ký trước")
    studied_credits: int = Field(..., ge=0, description="Số tín chỉ đang học")

    # Registration
    early_registration: int = Field(..., ge=0, le=1, description="Đăng ký sớm")
    reg_days_before: int = Field(..., description="Số ngày đăng ký trước khi bắt đầu")
    unregistered: int = Field(..., ge=0, le=1, description="Trạng thái hủy đăng ký")

    # VLE Interaction
    total_clicks: int = Field(..., ge=0, description="Tổng số click")
    active_days: int = Field(..., ge=0, description="Số ngày hoạt động")
    avg_clicks_day: float = Field(..., ge=0.0, description="Trung bình click/ngày")
    max_clicks_day: int = Field(..., ge=0, description="Số click tối đa trong 1 ngày")
    n_resources: int = Field(..., ge=0, description="Số loại tài nguyên tương tác")
    click_density: float = Field(..., ge=0.0, description="Mật độ click")

    # Assessment
    avg_score: float = Field(..., ge=0.0, le=100.0, description="Điểm trung bình")
    min_score: float = Field(..., ge=0.0, le=100.0, description="Điểm thấp nhất")
    std_score: float = Field(..., ge=0.0, description="Độ lệch chuẩn của điểm")
    avg_tma_score: float = Field(..., ge=0.0, le=100.0, description="Điểm trung bình TMA")
    n_submitted: int = Field(..., ge=0, description="Số bài kiểm tra đã nộp")
    n_late: int = Field(..., ge=0, description="Số bài nộp muộn")
    avg_submit_delay: float = Field(..., description="Trung bình độ trễ nộp bài (ngày)")


class RiskPrediction(BaseModel):
    """Kết quả dự đoán mức độ rủi ro"""

    risk_level: int = Field(..., description="Mức độ rủi ro: 0=Low, 1=Medium, 2=High, 3=Very High")
    risk_label: str = Field(..., description="Nhãn mức độ rủi ro")
    confidence: float = Field(..., description="Độ tin cậy dự đoán (0-100%)")
    probabilities: dict = Field(..., description="Xác suất cho từng mức rủi ro")
    recommendation: str = Field(..., description="Khuyến nghị hành động")
    model_used: str = Field(default="XGBoost", description="Mô hình được sử dụng")
    risk_color: Optional[str] = Field(default=None, description="Mã màu hex tương ứng mức rủi ro")


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str
    version: str = "1.0.0"


class ModelInfoResponse(BaseModel):
    model_name: str
    features: list
    num_features: int
    classes: list
    metrics: dict
