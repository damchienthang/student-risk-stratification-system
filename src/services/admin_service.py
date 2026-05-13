from typing import Dict, Any, List
from sqlmodel import Session, select, func
from src.core.database import engine
from src.models.student_risk import StudentRisk
from src.services.predictor import get_predictor

class AdminService:
    def __init__(self):
        self.predictor = get_predictor()

    def get_dashboard_stats(self, module: str = "all", presentation: str = "all", risk: str = "all") -> Dict[str, Any]:
        """
        Get aggregated risk statistics for the admin dashboard.
        Consolidates logic from admin_analytics.py.
        """
        with Session(engine) as session:
            # 1. Base query for counts and averages
            statement = select(
                func.count(StudentRisk.id).label("total"),
                func.avg(StudentRisk.total_clicks).label("avg_clicks"),
                func.avg(StudentRisk.avg_score).label("avg_score")
            )

            if module != "all":
                statement = statement.where(StudentRisk.code_module == module)
            if presentation != "all":
                statement = statement.where(StudentRisk.code_presentation == presentation)
            if risk != "all":
                statement = statement.where(StudentRisk.risk_label == risk)

            stats = session.exec(statement).first()

            # 2. Risk distribution
            dist_statement = select(
                StudentRisk.risk_level,
                func.count(StudentRisk.id)
            )

            if module != "all":
                dist_statement = dist_statement.where(StudentRisk.code_module == module)
            if presentation != "all":
                dist_statement = dist_statement.where(StudentRisk.code_presentation == presentation)

            dist_statement = dist_statement.group_by(StudentRisk.risk_level)
            dist_results = session.exec(dist_statement).all()
            
            risk_dist = {0: 0, 1: 0, 2: 0, 3: 0}
            for level, count in dist_results:
                risk_dist[level] = count

            # 3. Urgent intervention list
            # If a specific risk is selected, show most vulnerable in that group (lowest score)
            # If all, show High/Very High (level >= 2)
            if risk != "all":
                urgent_stmt = select(StudentRisk).where(StudentRisk.risk_label == risk)
            else:
                urgent_stmt = select(StudentRisk).where(StudentRisk.risk_level >= 2)

            if module != "all":
                urgent_stmt = urgent_stmt.where(StudentRisk.code_module == module)
            if presentation != "all":
                urgent_stmt = urgent_stmt.where(StudentRisk.code_presentation == presentation)
                
            urgent_stmt = urgent_stmt.order_by(StudentRisk.risk_level.desc(), StudentRisk.avg_score.asc()).limit(10)
            urgent_list = session.exec(urgent_stmt).all()

            return {
                "summary": stats,
                "risk_distribution": risk_dist,
                "urgent_intervention": [s.model_dump() for s in urgent_list]
            }

admin_service = AdminService()
