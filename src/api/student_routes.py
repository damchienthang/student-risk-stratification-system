from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import pandas as pd
from src.api.auth_routes import get_current_user
from src.services.predictor import get_predictor
from src.services.data_manager import get_data_manager

router = APIRouter(tags=["Student"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "src", "web", "templates"))

@router.get("/student", response_class=HTMLResponse)
async def student_dashboard(request: Request):
    user = get_current_user(request)
    if not user or user["role"] != "student":
        return RedirectResponse(url="/")
    
    student_id = int(user["username"])
    
    # Load data from memory
    dm = get_data_manager()
    df = dm.get_df()
    
    if df is None:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Dữ liệu chưa được tải vào hệ thống."
        })
        
    student_data = df[df['id_student'] == student_id]
    
    if student_data.empty:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"Student ID {student_id} not found."
        })
        
    # Get the latest record
    student_record = student_data.iloc[0].to_dict()
    
    # Predict to get recommendations and confidence if not in CSV or for fresh result
    predictor = get_predictor()
    prediction = predictor.predict(student_record)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "student": student_record,
        "prediction": prediction,
        "user": user
    })
