"""管理介面路由"""

import os
import secrets
from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.repositories.user_repository import UserRepository
from app.config.line_config import line_bot_api

router = APIRouter(prefix="/admin", tags=["admin"])

# 設定 Jinja2 模板
templates = Jinja2Templates(directory="app/templates")

# HTTP Basic Auth
security = HTTPBasic()

# 從環境變數取得管理員帳號密碼
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")


def verify_password(credentials: HTTPBasicCredentials = Depends(security)):
    """驗證帳號密碼"""
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ADMIN_USERNAME or ADMIN_PASSWORD not configured in environment variables"
        )
    
    # 使用 secrets.compare_digest 防止時序攻擊
    is_correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    is_correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username


def get_db():
    """取得資料庫 session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/logout", response_class=HTMLResponse)
async def logout():
    """登出頁面"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>已登出</title>
        <style>
            body {
                font-family: 'Microsoft JhengHei', 'PingFang TC', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0;
            }
            .card {
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                padding: 40px;
                text-align: center;
                max-width: 500px;
            }
            h1 { color: #4C0013; margin-bottom: 20px; }
            p { color: #666; margin-bottom: 15px; line-height: 1.6; }
            .btn {
                display: inline-block;
                padding: 12px 24px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                border-radius: 6px;
                margin-top: 20px;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
            }
            .warning {
                background: #fff3cd;
                border: 1px solid #ffc107;
                border-radius: 6px;
                padding: 15px;
                margin: 20px 0;
                color: #856404;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>✅ 已登出</h1>
            <div class="warning">
                <strong>⚠️ 重要提示：</strong><br>
                HTTP Basic Auth 由瀏覽器管理認證，要完全登出請：<br>
                1. 關閉此瀏覽器分頁<br>
                2. 或清除瀏覽器的網站資料
            </div>
            <p>如需重新登入，請關閉此分頁後重新訪問管理介面。</p>
            <a href="/admin/patient-info" class="btn">重新登入</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.get("/patient-info", response_class=HTMLResponse)
async def patient_info_form(
    request: Request, 
    db: Session = Depends(get_db),
    username: str = Depends(verify_password)
):
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
    username: str = Depends(verify_password)
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
