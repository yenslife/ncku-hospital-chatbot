"""測試 JWT handler"""

from datetime import datetime, timedelta, timezone
from jose import jwt

from app.services.auth.jwt_handler import (
    create_access_token,
    verify_token,
    get_current_user,
    SECRET_KEY,
    ALGORITHM,
)


class TestJWTHandler:
    """JWT handler 測試類別"""

    def test_create_access_token(self):
        """測試建立 access token"""
        # Arrange
        data = {"sub": "admin_user"}

        # Act
        token = create_access_token(data)

        # Assert
        assert token is not None
        assert isinstance(token, str)

        # 驗證 token 可以解碼
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "admin_user"
        assert "exp" in payload

    def test_create_access_token_with_expiration(self):
        """測試建立有過期時間的 token"""
        # Arrange
        data = {"sub": "test_user"}
        expires_delta = timedelta(hours=1)

        # Act
        token = create_access_token(data, expires_delta)

        # Assert
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)

        # 驗證過期時間在未來
        assert exp_datetime > datetime.now(timezone.utc)
        # 驗證過期時間在 1 小時內
        assert exp_datetime < datetime.now(timezone.utc) + timedelta(hours=2)

    def test_verify_token_valid(self):
        """測試驗證有效的 token"""
        # Arrange
        data = {"sub": "valid_user", "role": "admin"}
        token = create_access_token(data)

        # Act
        payload = verify_token(token)

        # Assert
        assert payload is not None
        assert payload["sub"] == "valid_user"
        assert payload["role"] == "admin"

    def test_verify_token_invalid(self):
        """測試驗證無效的 token"""
        # Arrange
        invalid_token = "invalid.token.here"

        # Act
        payload = verify_token(invalid_token)

        # Assert
        assert payload is None

    def test_verify_token_expired(self):
        """測試驗證過期的 token"""
        # Arrange - 建立一個已過期的 token
        data = {"sub": "expired_user"}
        expired_token = create_access_token(data, expires_delta=timedelta(seconds=-1))

        # Act
        payload = verify_token(expired_token)

        # Assert
        assert payload is None

    def test_get_current_user_valid_token(self):
        """測試從 request 取得目前使用者（有效 token）"""
        # Arrange
        from fastapi import Request
        from unittest.mock import MagicMock

        data = {"sub": "test_admin"}
        token = create_access_token(data)

        # 模擬 request 物件
        mock_request = MagicMock(spec=Request)
        mock_request.cookies = {"access_token": token}

        # Act
        username = get_current_user(mock_request)

        # Assert
        assert username == "test_admin"

    def test_get_current_user_no_token(self):
        """測試從 request 取得目前使用者（無 token）"""
        # Arrange
        from fastapi import Request
        from unittest.mock import MagicMock

        mock_request = MagicMock(spec=Request)
        mock_request.cookies = {}

        # Act
        username = get_current_user(mock_request)

        # Assert
        assert username is None

    def test_get_current_user_invalid_token(self):
        """測試從 request 取得目前使用者（無效 token）"""
        # Arrange
        from fastapi import Request
        from unittest.mock import MagicMock

        mock_request = MagicMock(spec=Request)
        mock_request.cookies = {"access_token": "invalid_token"}

        # Act
        username = get_current_user(mock_request)

        # Assert
        assert username is None
