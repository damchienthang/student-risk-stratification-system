# -*- coding: utf-8 -*-
"""
main.py - File chay chinh cua server
Student Risk Stratification System - FastAPI Backend
"""
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Load biến môi trường
load_dotenv()

# Khởi tạo FastAPI app
app = FastAPI(
    title="Student Risk Stratification System",
    description="""
    ## 🎓 Hệ Thống Phân Tầng Rủi Ro Sinh Viên
    
    API này sử dụng mô hình **XGBoost** được huấn luyện trên bộ dữ liệu OULAD 
    để dự đoán mức độ rủi ro học tập của sinh viên gồm 4 mức:
    
    - 🟢 **Low** - Rủi ro thấp
    - 🟡 **Medium** - Rủi ro trung bình  
    - 🟠 **High** - Rủi ro cao
    - 🔴 **Very High** - Rủi ro rất cao
    
    ### Nhóm phát triển: Nhóm 14 - Học kỳ 6
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (CSS, JS, Images)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "src", "web", "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Mount visuals directory
visuals_dir = os.path.join(BASE_DIR, "visuals")
if os.path.exists(visuals_dir):
    app.mount("/visuals", StaticFiles(directory=visuals_dir), name="visuals")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle"""
    print("[START] Student Risk Stratification System...", flush=True)
    try:
        from src.services.predictor import get_predictor
        predictor = get_predictor()
        status = "OK" if predictor.is_loaded() else "FAILED"
        print(f"[MODEL] XGBoost load: {status}", flush=True)
        
        # Initialize Database
        data_path = os.path.join(BASE_DIR, 'data', 'processed', 'student_features_labeled.csv')
        
        from src.services.db_manager import get_db_manager
        dbm = get_db_manager()
        dbm.initialize_db(data_path)
    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
    yield
    print("[STOP] Server shutting down.", flush=True)


# Rebuild app with lifespan
app.router.lifespan_context = lifespan

# Include routers
from src.api.routes import router as general_router
from src.api.auth_routes import router as auth_router
from src.api.admin_routes import router as admin_router
from src.api.student_routes import router as student_router

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(student_router)
app.include_router(general_router)


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "true").lower() == "true"

    print(f"Server running at: http://localhost:{port}", flush=True)
    print(f"API Docs: http://localhost:{port}/docs", flush=True)

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
