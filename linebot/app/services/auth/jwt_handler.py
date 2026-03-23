"""JWT Token 認證工具"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Request
from fastapi.responses import RedirectResponse

# 從環境變數取得設定
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """生成 JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """驗證 JWT token，返回 payload 或 None"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user(request: Request) -> Optional[str]:
    """從 cookie 取得並驗證當前使用者，返回 username 或 None"""
    token = request.cookies.get("access_token")
    
    if not token:
        return None
    
    payload = verify_token(token)
    if not payload:
        return None
    
    username: str = payload.get("sub")
    return username


def require_auth(request: Request) -> str:
    """要求認證，若未認證則拋出重定向異常"""
    username = get_current_user(request)
    
    if not username:
        # 返回重定向到登入頁面
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": "/admin/login"}
        )
    
    return username
