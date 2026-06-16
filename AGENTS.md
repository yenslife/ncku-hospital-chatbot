# 成大醫院洗腎聊天機器人專案

## 專案概述
成大醫院 LINE 聊天機器人，專為洗腎患者設計。使用 FastAPI + Dify LLM + LINE Bot SDK。

**技術**: FastAPI (Python 3.13+), Dify API, LINE Bot SDK v3, SQLite, Redis, uv, pytest, Ruff

## 專案結構
```
linebot/
├── app/
│   ├── api/          # 外部 API (Dify, 音訊, 圖片)
│   ├── config/       # LINE, Logger 配置
│   ├── db/           # SQLite, Redis 連接
│   ├── models/       # 資料模型
│   ├── repositories/ # 資料存取層
│   ├── routers/      # FastAPI 路由
│   ├── services/     # 業務邏輯
│   └── templates/    # Admin panel HTML
├── tests/            # 測試檔案
└── sql_app.db        # SQLite 資料庫
```

## 開發環境設置
```bash
cd linebot
cp .env.example .env
# 填寫 .env: DIFY_API_KEY, LINE_TOKENS, REDIS, ADMIN_CREDENTIALS, SECRET_KEY
openssl rand -hex 32  # 生成 SECRET_KEY
uv sync
docker run -d -p 6379:6379 redis:latest
uv run uvicorn app.main:app --host=0.0.0.0 --port=8000 --reload --workers 4
```

## 常用命令
```bash
cd linebot
# 測試
uv run pytest tests/ -v
# 程式碼檢查
ruff check . && ruff format .
# 資料庫備份
cp sql_app.db "sql_app.db.backup_$(date +%Y%m%d_%H%M%S)"
# 資料庫遷移 (手動 SQL)
sqlite3 sql_app.db "ALTER TABLE users ADD COLUMN new_column DATETIME;"
# 新增套件 (請一律使用 uv，不要直接 pip 或者 python)
uv add [package_name]
```

## ⚠️ 關鍵注意事項

### 資料庫遷移
**沒有 Alembic**，修改模型後需手動執行 SQL 遷移，記得先備份資料庫。

### 測試環境
測試時必須設定 `TESTING=true` 環境變數，避免 logger 權限問題。

### LINE API 速率限制
約 1000 requests/minute，高流量時需考慮 rate limiter。

### Dify API
使用 streaming 模式避免超時，自動管理 conversation_id。

## 開發規範
- **Commit**: conventional commits (e.g. `feat:`, `fix:`, `style:`)
- **程式碼**: Ruff lint + format, PEP 8, type hints
- **測試**: `test_<module>.py`, pytest fixtures
- **架構**: 分層架構 (Routers → Services → Repositories → Models)

## 已知問題
1. 資料庫遷移需手動執行 SQL
2. Logger 在測試環境需 `TESTING=true`
3. .env 檔案不應 commit 到 git
