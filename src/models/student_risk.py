from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session, select, Index

class StudentRisk(SQLModel, table=True):
    __tablename__ = "student_risk"
    
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

# Database configuration
sqlite_file_name = "data/processed/database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
