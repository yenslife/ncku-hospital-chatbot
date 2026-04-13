"""pytest 共用設定和 fixtures"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.database import Base, get_db
from app.main import app

# 使用記憶體中的 SQLite 進行測試
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session():
    """建立測試用的資料庫 session"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # 建立所有表格
    Base.metadata.create_all(bind=engine)

    # 建立 session
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # 清理表格
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """建立 FastAPI 測試客戶端，使用測試資料庫"""

    # 覆蓋 get_db 依賴
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # 清理覆蓋
    app.dependency_overrides.clear()
