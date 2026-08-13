import os
import pandas as pd
from typing import Optional, Any, List, Tuple
from sqlmodel import Session, select, func
from src.core.database import engine, create_db_and_tables
from src.core.security import hash_password, UserRole
from src.core.config import settings
from src.models.student_risk import StudentRisk, InferenceLog
from src.models.user import User
from src.services.predictor import FEATURE_DEFAULTS

class AuthService:
    def __init__(self):
        self.engine = engine

    def initialize_system(self):
        """Create tables and migrate data if DB is empty"""
        create_db_and_tables()

        with Session(self.engine) as session:
            # Seed Admin
            if session.exec(select(func.count()).select_from(User)).one() == 0:
                admin = User(
                    username="admin",
                    password_hash=hash_password("admin123"),
                    role=UserRole.ADMIN,
                    full_name="Quản trị viên Hệ thống"
                )
                session.add(admin)
                session.commit()

            # Migrate CSV data
            if session.exec(select(func.count()).select_from(StudentRisk)).one() == 0:
                csv_path = settings.PROCESSED_DATA_PATH
                if not csv_path.exists():
                    return

                chunksize = 5000
                int_cols = [
                    'gender_num', 'imd_band_num', 'education_num', 'age_num', 'disability_num',
                    'num_of_prev_attempts', 'studied_credits', 'early_registration', 'reg_days_before',
                    'unregistered', 'total_clicks', 'active_days', 'max_clicks_day', 'n_resources',
                    'n_submitted', 'n_late', 'risk_level'
                ]
                for chunk in pd.read_csv(csv_path, chunksize=chunksize):
                    # Fill NaNs using defaults
                    for col, default_val in FEATURE_DEFAULTS.items():
                        if col in chunk.columns:
                            chunk[col] = chunk[col].fillna(default_val)
                    
                    # Ensure integer columns are correctly typed (pandas casts ints with NaNs to floats)
                    for col in int_cols:
                        if col in chunk.columns:
                            chunk[col] = chunk[col].astype(int)

                    chunk = chunk.where(pd.notnull(chunk), None)
                    records = [StudentRisk(**row.to_dict()) for _, row in chunk.iterrows()]
                    session.add_all(records)
                    session.commit()

    def authenticate_user(self, username: str, password: str):
        with Session(self.engine) as session:
            user = session.exec(select(User).where(User.username == username)).first()
            if user and user.password_hash == hash_password(password):
                if not user.is_active:
                    return {"error": "locked"} # Account locked
                return {"role": user.role, "username": user.username, "is_external": user.is_external}

            # OULAD login fallback
            if username == password and username.isdigit():
                student_id = int(username)
                student_data = session.exec(select(StudentRisk).where(StudentRisk.id_student == student_id)).first()
                if student_data:
                    # Auto-create User record for OULAD student if not exists
                    existing_user = session.exec(select(User).where(User.username == username)).first()
                    if not existing_user:
                        new_user = User(
                            username=username,
                            password_hash=hash_password(password), # Default password is same as username
                            role=UserRole.STUDENT,
                            is_external=False,
                            full_name=f"Sinh viên OULAD #{username}"
                        )
                        session.add(new_user)
                        session.commit()
                    return {"role": UserRole.STUDENT, "username": username, "is_external": False}
            return None

    def register_user(self, username: str, email: str, password: str, full_name: str):
        with Session(self.engine) as session:
            if session.exec(select(User).where((User.username == username) | (User.email == email))).first():
                return None
            new_user = User(
                username=username,
                email=email,
                password_hash=hash_password(password),
                role=UserRole.GUEST,
                is_external=True,
                full_name=full_name
            )
            session.add(new_user)
            session.commit()
            return new_user

auth_service = AuthService()
