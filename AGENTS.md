# 成大醫院洗腎聊天機器人專案

## 專案定位
兩個獨立工作線：
- `linebot/`: FastAPI webhook server (uv + Python 3.13)
- `richmenu/`: LINE Rich Menu 部署腳本 (bash + curl + jq)

## 工作原則
- 明確區分 linebot/richmenu 工作線，避免混改
- 不提交真實金鑰或 `.env`
- 跨功能需求需同時檢查 richmenu action data 與 linebot postback handler
- **一律使用 uv 管理套件，禁止使用 pip 或直接 python 安裝**
  - 安裝套件：`uv add [package_name]`
  - 移除套件：`uv remove [package_name]`
  - 執行命令：`uv run [command]`

## linebot (FastAPI Webhook)

### 啟動與環境
```bash
cd linebot
uv sync
cp .env.example .env  # 填寫 LINE_TOKENS, DIFY_API_KEY, REDIS, ADMIN_CREDENTIALS, SECRET_KEY
openssl rand -hex 32  # 生成 SECRET_KEY
docker run -d -p 6379:6379 redis:latest
uv run uvicorn app.main:app --host=0.0.0.0 --port=8000 --reload --workers 4
```

### 核心架構
- **入口**: `app/main.py` → `routers/linebot.py` (webhook) + `routers/admin.py` (管理介面)
- **Webhook 事件**: TextMessage, ImageMessage, AudioMessage, FollowEvent, PostbackEvent
- **分層**: Routers → Services → Repositories → Models
- **外部 API**: Dify LLM (streaming), OpenAI/Gemini (音訊轉文字)

### 修改指引
- **Webhook 行為**: `services/handlers/`, `services/message_service.py`, `services/postback_service.py`
- **資料儲存**: `db/`, `repositories/`, `models/`
- **LINE 設定**: `config/line_config.py`

### ⚠️ 關鍵注意
- **資料庫遷移**: 無 Alembic，需手動 SQL + 備份
- **測試環境**: 需 `TESTING=true` 避免 logger 權限問題
- **LINE API**: 速率限制 ~1000 req/min

## richmenu (部署腳本)

### 執行需求
- 環境變數: `LINE_ACCESS_TOKEN`
- 系統工具: `curl`, `jq`
- 腳本: `richmenu_deploy_page1.sh`, `page2.sh`, `page3.sh`

### 操作特性
- 刪除舊 menu → 建立新 menu → 設定 alias → 設定預設 menu
- 修改時需跨頁檢查 `name`/`alias`/`richmenuswitch` 一致性
- 圖片在 `richmenu/images/`，需同步 `IMAGE_PATH` 和 `areas.bounds`

## 常用命令
```bash
cd linebot
uv run pytest tests/ -v          # 測試
ruff check . && ruff format .     # 程式碼檢查
cp sql_app.db "sql_app.db.backup_$(date +%Y%m%d_%H%M%S)"  # 資料庫備份
sqlite3 sql_app.db "ALTER TABLE users ADD COLUMN new_column DATETIME;"  # 手動遷移
```

## 開發規範
- **Commit**: conventional commits (`feat:`, `fix:`, `style:`)
- **程式碼**: Ruff lint + format, PEP 8, type hints
- **測試**: `test_<module>.py`, pytest fixtures
