# -*- coding: utf-8 -*-
"""
main.py - Entry point for Student Risk Stratification System
"""
import sys
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.core.config import settings
from src.services.auth_service import auth_service
from src.services.predictor import get_predictor

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[START] {settings.PROJECT_NAME} v{settings.VERSION}...", flush=True)
    try:
        # Initialize ML Model
        predictor = get_predictor()
        print(f"[MODEL] Status: {'READY' if predictor.is_loaded() else 'FAILED'}", flush=True)
        
        # Initialize Database & Seeding
        auth_service.initialize_system()
        print("[DB] Initialized and Seeded.", flush=True)
    except Exception as e:
        print(f"[CRITICAL ERROR] {e}", flush=True)
    host = settings.HOST if hasattr(settings, 'HOST') else "0.0.0.0"
    port = settings.PORT if hasattr(settings, 'PORT') else 8000
    print(f"[SERVER] Đang chạy tại: http://localhost:{port}", flush=True)
    print(f"[DOCS]   API Docs    : http://localhost:{port}/docs", flush=True)
    yield
    print("[STOP] Server shutting down.", flush=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory=str(settings.BASE_DIR / "src" / "web" / "static")), name="static")
app.mount("/visuals", StaticFiles(directory=str(settings.BASE_DIR / "visuals")), name="visuals")

# Import Routers
from src.api.v1.auth import router as auth_api
from src.api.v1.student import router as student_api
from src.api.v1.admin import router as admin_api
from src.api.v1.general import router as general_api
from src.web.routes import router as web_router

# Include Routers
app.include_router(auth_api, prefix=f"{settings.API_V1_STR}/auth", tags=["API Auth"])
app.include_router(student_api, prefix=f"{settings.API_V1_STR}/student", tags=["API Student"])
app.include_router(admin_api, prefix=f"{settings.API_V1_STR}/admin", tags=["API Admin"])
app.include_router(general_api, prefix=f"{settings.API_V1_STR}/general", tags=["API General"])
app.include_router(web_router, tags=["Web"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
