from sqlmodel import SQLModel, create_engine, Session
from src.core.config import settings

# create_engine configuration
is_sqlite = settings.DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

def create_db_and_tables():
    """Create all tables defined in SQLModel metadata."""
    from src.models.user import User
    from src.models.student_risk import StudentRisk
    SQLModel.metadata.create_all(engine)

def get_session():
    """Provide a database session."""
    with Session(engine) as session:
        yield session
