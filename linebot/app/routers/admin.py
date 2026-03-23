"""管理介面路由"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.repositories.user_repository import UserRepository
from app.config.line_config import line_bot_api

router = APIRouter(prefix="/admin", tags=["admin"])

# 設定 Jinja2 模板
templates = Jinja2Templates(directory="app/templates")


def get_db():
    """取得資料庫 session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/patient-info", response_class=HTMLResponse)
async def patient_info_form(request: Request, db: Session = Depends(get_db)):
    """顯示病患資訊填寫表單"""
    # 直接查詢所有使用者
    from app.models.user import User
    users = db.query(User).all()
    
    # 取得 LINE 顯示名稱
    user_list = []
    for user in users:
        try:
            profile = line_bot_api.get_profile(user.line_id)
            display_name = profile.display_name
        except Exception:
            display_name = "無法取得"
        
        user_list.append({
            "line_id": user.line_id,
            "display_name": display_name,
            "bed_number": user.bed_number or "",
            "diagnosis": user.diagnosis or "",
            "attending_physician": user.attending_physician or "",
            "dialysis_reason": user.dialysis_reason or "",
        })
    
    return templates.TemplateResponse(
        "patient_info.html",
        {"request": request, "users": user_list}
    )


@router.post("/patient-info", response_class=HTMLResponse)
async def update_patient_info(
    request: Request,
    line_id: str = Form(...),
    bed_number: str = Form(default=""),
    diagnosis: str = Form(default=""),
    attending_physician: str = Form(default=""),
    dialysis_reason: str = Form(default=""),
    db: Session = Depends(get_db),
):
    """更新病患資訊"""
    user_repository = UserRepository(db)
    user = user_repository.get_user(line_id)
    
    user.bed_number = bed_number if bed_number else None
    user.diagnosis = diagnosis if diagnosis else None
    user.attending_physician = attending_physician if attending_physician else None
    user.dialysis_reason = dialysis_reason if dialysis_reason else None
    
    db.commit()
    
    return RedirectResponse(url="/admin/patient-info", status_code=303)
