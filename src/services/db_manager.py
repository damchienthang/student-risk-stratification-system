import os
import hashlib
import pandas as pd
from typing import Optional, Any
from sqlmodel import Session, select, func
from src.models.student_risk import StudentRisk, InferenceLog
from src.models.user import User
from src.database import engine, create_db_and_tables

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class DBManager:
    def __init__(self):
        self.engine = engine

    def initialize_db(self, csv_path: str):
        """Create tables and migrate data if DB is empty"""
        create_db_and_tables()

        with Session(self.engine) as session:
            # Check and seed default Admin if users table is empty
            if session.exec(select(func.count()).select_from(User)).one() == 0:
                print("[DB] Seeding default admin user...")
                admin = User(
                    username="admin",
                    password_hash=hash_password("admin123"),
                    role="lecturer",
                    full_name="Quản trị viên Hệ thống"
                )
                session.add(admin)
                session.commit()

            # Check if student data already exists
            statement = select(func.count()).select_from(StudentRisk)
            count = session.exec(statement).one()

            if count == 0:
                print(f"[DB] Database is empty. Migrating from {csv_path}...")
                if not os.path.exists(csv_path):
                    print(f"[ERROR] Migration source not found: {csv_path}")
                    return

                # Load CSV in chunks to avoid memory issues if it's large
                chunksize = 5000
                for chunk in pd.read_csv(csv_path, chunksize=chunksize):
                    # Convert NaN to None for SQL
                    chunk = chunk.where(pd.notnull(chunk), None)

                    records = []
                    for _, row in chunk.iterrows():
                        record = StudentRisk(**row.to_dict())
                        records.append(record)

                    session.add_all(records)
                    session.commit()
                    print(f"[DB] Migrated {len(records)} records...")

                print("[DB] Migration completed successfully.")
            else:
                print(f"[DB] Database already contains {count} student records. Skipping migration.")

    def authenticate_user(self, username: str, password: str):
        """Xác thực người dùng từ Database"""
        with Session(self.engine) as session:
            # 1. Check in users table (Admin/Lecturers and external students)
            user = session.exec(select(User).where(User.username == username)).first()
            if user and user.password_hash == hash_password(password):
                return {"role": user.role, "username": user.username, "is_external": user.is_external}

            # 2. Check if OULAD student (internal)
            # Login if username == password and is numeric (default for OULAD)
            if username == password and username.isdigit():
                student = session.exec(select(StudentRisk).where(StudentRisk.id_student == int(username))).first()
                if student:
                    return {"role": "student", "username": username, "is_external": False}

            return None

    def register_external_student(self, username: str, email: str, password: str, full_name: str):
        """Đăng ký sinh viên tự do (ngoài OULAD)"""
        with Session(self.engine) as session:
            # Check existing
            if session.exec(select(User).where((User.username == username) | (User.email == email))).first():
                return None

            new_user = User(
                username=username,
                email=email,
                password_hash=hash_password(password),
                role="student",
                is_external=True,
                full_name=full_name
            )
            session.add(new_user)
            session.commit()
            return new_user

    def get_user_by_email(self, email: str):
        """Lấy thông tin người dùng qua email (cho quên mật khẩu)"""
        with Session(self.engine) as session:
            return session.exec(select(User).where(User.email == email)).first()

    def reset_password(self, email: str, new_password: str):
        """Đặt lại mật khẩu mới"""
        with Session(self.engine) as session:
            user = session.exec(select(User).where(User.email == email)).first()
            if user:
                user.password_hash = hash_password(new_password)
                session.add(user)
                session.commit()
                return True
            return False

    def get_students_paginated(self, module: str, presentation: str, page: int = 1, limit: int = 50, search_id: Optional[str] = None, risk_level: Optional[str] = None):
        """Fetch students with filtering, searching and pagination"""
        offset = (page - 1) * limit

        with Session(self.engine) as session:
            statement = select(StudentRisk)

            # Apply module filter only if not 'all'
            if module and module != "all":
                statement = statement.where(StudentRisk.code_module == module)

            # Apply presentation filter only if not 'all'
            if presentation and presentation != "all":
                statement = statement.where(StudentRisk.code_presentation == presentation)

            # Apply risk filter
            if risk_level and risk_level != "all":
                statement = statement.where(StudentRisk.risk_label == risk_level)

            if search_id:
                statement = statement.where(getattr(StudentRisk, "id_student").like(f"%{search_id}%"))

            # Get total count for pagination metadata
            count_statement = select(func.count()).select_from(statement.subquery())
            total_count = session.exec(count_statement).one()

            # Order by risk level desc, then avg_score asc
            statement = statement.order_by(getattr(StudentRisk, "risk_level").desc(), getattr(StudentRisk, "avg_score").asc())
            statement = statement.offset(offset).limit(limit)

            results = session.exec(statement).all()
            return results, total_count

    def get_guest_predictions_paginated(self, page: int = 1, limit: int = 50, risk_level: Optional[str] = None):
        """Fetch guest trial logs with pagination"""
        offset = (page - 1) * limit
        with Session(self.engine) as session:
            statement = select(InferenceLog)
            if risk_level and risk_level != "all":
                statement = statement.where(InferenceLog.risk_label == risk_level)

            count_statement = select(func.count()).select_from(statement.subquery())
            total_count = session.exec(count_statement).one()

            statement = statement.order_by(getattr(InferenceLog, "timestamp").desc())
            statement = statement.offset(offset).limit(limit)

            results = session.exec(statement).all()
            return results, total_count

    def save_inference_log(self, data: dict):
        """Save a guest prediction trial to InferenceLogs"""
        with Session(self.engine) as session:
            log = InferenceLog(**data)
            session.add(log)
            session.commit()
            session.refresh(log)
            return log

    def get_student_by_id(self, student_id: int):
        """Fetch a single student by ID"""
        with Session(self.engine) as session:
            statement = select(StudentRisk).where(StudentRisk.id_student == student_id)
            return session.exec(statement).first()

    def get_student_features(self, student_id: int):
        """Fetch student as a feature dict for prediction"""
        student = self.get_student_by_id(student_id)
        if student:
            return student.model_dump()
        return None

    def get_summary_stats(self, module: str, presentation: str):
        """Get summary stats using SQL aggregations"""
        with Session(self.engine) as session:
            statement = select(
                func.count(getattr(StudentRisk, "id")).label("total"),
                func.avg(getattr(StudentRisk, "total_clicks")).label("avg_clicks"),
                func.avg(getattr(StudentRisk, "avg_score")).label("avg_score")
            )

            if module != "all":
                statement = statement.where(StudentRisk.code_module == module)
            if presentation != "all":
                statement = statement.where(StudentRisk.code_presentation == presentation)

            stats = session.exec(statement).first()

            # Risk distribution
            dist_statement = select(
                getattr(StudentRisk, "risk_level"),
                func.count(getattr(StudentRisk, "id"))
            )

            if module != "all":
                dist_statement = dist_statement.where(StudentRisk.code_module == module)
            if presentation != "all":
                dist_statement = dist_statement.where(StudentRisk.code_presentation == presentation)

            dist_statement = dist_statement.group_by(getattr(StudentRisk, "risk_level"))

            dist_results = session.exec(dist_statement).all()
            risk_dist = {0: 0, 1: 0, 2: 0, 3: 0}
            for level, count in dist_results:
                risk_dist[level] = count

            return stats, risk_dist

# Singleton helper
_db_manager = DBManager()

def get_db_manager():
    return _db_manager
