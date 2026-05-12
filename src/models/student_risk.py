from typing import ClassVar, Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

class StudentRisk(SQLModel, table=True):
    __tablename__: ClassVar[str] = "student_risk"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_student: int = Field(index=True)
    code_module: str = Field(index=True)
    code_presentation: str = Field(index=True)

    gender_num: int
    imd_band_num: int
    education_num: int
    age_num: int
    disability_num: int
    num_of_prev_attempts: int
    studied_credits: int
    early_registration: int
    reg_days_before: int
    unregistered: int
    total_clicks: int
    active_days: int
    avg_clicks_day: float
    max_clicks_day: int
    n_resources: int
    click_density: float
    avg_score: float
    min_score: float
    std_score: float
    avg_tma_score: float
    n_submitted: int
    n_late: int
    avg_submit_delay: float
    risk_level: int
    risk_label: str
    final_result: str

class InferenceLog(SQLModel, table=True):
    __tablename__: ClassVar[str] = "inference_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Input features
    code_module: str = Field(default="Guest")
    code_presentation: str = Field(default="Guest")
    gender_num: int
    imd_band_num: int
    education_num: int
    age_num: int
    disability_num: int
    num_of_prev_attempts: int
    studied_credits: int
    total_clicks: int
    avg_score: float

    # Result
    risk_level: int
    risk_label: str
    confidence: float
