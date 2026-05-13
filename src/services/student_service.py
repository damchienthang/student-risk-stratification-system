from typing import Optional, Dict, Any
from sqlmodel import Session, select
from src.core.database import engine
from src.models.student_risk import StudentRisk
from src.services.predictor import get_predictor

class StudentService:
    def __init__(self):
        self.predictor = get_predictor()

    def get_student_report(self, student_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch student data and perform risk prediction.
        Consolidates logic from redundant query scripts.
        """
        with Session(engine) as session:
            student = session.exec(select(StudentRisk).where(StudentRisk.id_student == student_id)).first()
            if not student:
                return None
            
            features = student.model_dump()
            prediction = self.predictor.predict(features)
            
            return {
                "student": features,
                "prediction": prediction
            }

student_service = StudentService()
