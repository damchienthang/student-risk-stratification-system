# Configure core settings, database connection, and security session handlers
import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory: src/core/config.py -> src/core/ -> src/ -> Project Root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "Student Risk Stratification System"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    BASE_DIR = BASE_DIR
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    
    # SMTP Settings cho Demo Email
    SMTP_EMAIL: str = os.getenv("SMTP_EMAIL", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    
    # Database
    DB_DIR = BASE_DIR / "data" / "processed"
    DATABASE_URL: str = os.getenv("DATABASE_URL") or f"sqlite:///{DB_DIR}/database.db"
    
    # Data Paths
    PROCESSED_DATA_PATH = DB_DIR / "student_features_labeled.csv"
    
    # Model Paths
    MODEL_SEARCH_DIRS = [
        BASE_DIR / "notebooks" / "models",
        BASE_DIR / "models",
    ]

settings = Settings()

# Ensure DB dir exists
os.makedirs(settings.DB_DIR, exist_ok=True)
