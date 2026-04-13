"""管理介面路由"""

import os
import secrets
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.repositories.user_repository import UserRepository
from app.config.line_config import line_bot_api
from app.services.auth.jwt_handler import create_access_token, get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

# 設定 Jinja2 模板
templates = Jinja2Templates(directory="app/templates")

# 從環境變數取得管理員帳號密碼
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")


def get_db():
    """取得資料庫 session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    """顯示登入頁面"""
    # 如果已登入，重定向到管理頁面
    username = get_current_user(request)
    if username:
        return RedirectResponse(url="/admin/patient-info", status_code=302)

    return templates.TemplateResponse(
        "login.html", {"request": request, "error": error}
    )


@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """處理登入請求"""
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "系統未正確設定管理員帳號密碼"}
        )

    # 驗證帳號密碼
    is_correct_username = secrets.compare_digest(username, ADMIN_USERNAME)
    is_correct_password = secrets.compare_digest(password, ADMIN_PASSWORD)

    if not (is_correct_username and is_correct_password):
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "帳號或密碼錯誤"}
        )

    # 生成 JWT token
    access_token = create_access_token(data={"sub": username})

    # 重定向到管理頁面，並設置 cookie
    response = RedirectResponse(url="/admin/patient-info", status_code=302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # 防止 XSS
        max_age=60 * 60 * 24,  # 24 小時
        expires=60 * 60 * 24,
    )

    return response


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    """登出 - 清除 cookie 中的 token"""
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("access_token")
    return response


@router.get("/patient-info", response_class=HTMLResponse)
async def patient_info_form(
    request: Request,
    db: Session = Depends(get_db),
):
    """顯示病患資訊填寫表單"""
    # 檢查認證
    username = get_current_user(request)
    if not username:
        return RedirectResponse(url="/admin/login", status_code=302)

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

        user_list.append(
            {
                "line_id": user.line_id,
                "display_name": display_name,
                "bed_number": user.bed_number or "",
                "diagnosis": user.diagnosis or "",
                "attending_physician": user.attending_physician or "",
                "dialysis_reason": user.dialysis_reason or "",
            }
        )

    return templates.TemplateResponse(
        "patient_info.html", {"request": request, "users": user_list}
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
    # 檢查認證
    username = get_current_user(request)
    if not username:
        return RedirectResponse(url="/admin/login", status_code=302)

    user_repository = UserRepository(db)
    user = user_repository.get_user(line_id)

    user.bed_number = bed_number if bed_number else None
    user.diagnosis = diagnosis if diagnosis else None
    user.attending_physician = attending_physician if attending_physician else None
    user.dialysis_reason = dialysis_reason if dialysis_reason else None

    db.commit()

    return RedirectResponse(url="/admin/patient-info", status_code=303)
