"""測試 FastAPI 應用程式啟動"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """建立測試客戶端"""
    return TestClient(app)


def test_app_startup(client):
    """測試應用程式能正常啟動"""
    assert app is not None


def test_root_endpoint(client):
    """測試根路由返回預期訊息"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
