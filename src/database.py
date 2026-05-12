import os
from sqlmodel import SQLModel, create_engine, Session

# Base directory relative to this file
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_db_dir = os.path.join(_BASE_DIR, "data", "processed")

# Ensure the directory exists
os.makedirs(_db_dir, exist_ok=True)

sqlite_file_name = os.path.join(_db_dir, "database.db")
sqlite_url = f"sqlite:///{sqlite_file_name}"

# create_engine configuration
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    """Create all tables defined in SQLModel metadata."""
    from src.models.user import User
    from src.models.student_risk import StudentRisk, InferenceLog
    SQLModel.metadata.create_all(engine)

def get_session():
    """Provide a database session."""
    with Session(engine) as session:
        yield session
