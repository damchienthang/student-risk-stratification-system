from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from src.api.auth_routes import get_current_user
from src.services.db_manager import get_db_manager

router = APIRouter(tags=["Admin"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "src", "web", "templates"))

@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    user = get_current_user(request)
    if not user or user["role"] != "admin":
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/")
        
    return templates.TemplateResponse("admin.html", {
        "request": request, 
        "module": "BBB", 
        "presentation": "2014J",
        "username": user["username"]
    })

@router.get("/api/analytics/{module}/{presentation}")
async def get_analytics(
    module: str, 
    presentation: str, 
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: str = Query(None)
):
    user = get_current_user(request)
    if not user or user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")

    dbm = get_db_manager()
    
    # Get stats for the dashboard summary
    stats, risk_dist = dbm.get_summary_stats(module, presentation)
    if not stats or stats.total == 0:
        return {"error": "Data not found"}

    # Get paginated students for the class list
    students, total_count = dbm.get_students_paginated(
        module, presentation, page=page, limit=limit, search_id=search
    )
    
    # Format student list for frontend
    student_list = []
    for s in students:
        student_list.append({
            "id": s.id_student,
            "score": round(s.avg_score, 2),
            "clicks": s.total_clicks,
            "risk": s.risk_label,
            "risk_level": s.risk_level
        })

    # Get top 10 at risk for dashboard summary (fixed, not paginated)
    top_at_risk_list, _ = dbm.get_students_paginated(module, presentation, page=1, limit=10)
    top_at_risk = [{
        "id": s.id_student,
        "score": round(s.avg_score, 2),
        "risk": s.risk_label,
        "risk_level": s.risk_level
    } for s in top_at_risk_list]

    return {
        "summary": {
            "total_students": stats.total,
            "avg_clicks": round(stats.avg_clicks, 1) if stats.avg_clicks else 0,
            "avg_score": round(stats.avg_score, 2) if stats.avg_score else 0
        },
        "risk_distribution": [int(risk_dist.get(i, 0)) for i in range(4)],
        "top_at_risk": top_at_risk,
        "all_students": student_list,
        "pagination": {
            "page": page,
            "limit": limit,
            "total_records": total_count,
            "total_pages": (total_count + limit - 1) // limit
        }
    }
