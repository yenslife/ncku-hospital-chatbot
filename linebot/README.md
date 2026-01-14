# NCKU Hospital Linebot

## 使用方式

請務必確保執行的系統有安裝 sqlite3 和 redis

1. 複製 `.env.example` 到 `.env`，並替換其中的值
    ```bash
    $ cp .env.example .env
    ```
2. 使用 uv 運行，這邊可以設定多一點 worker
    ```bash
    $ uv run uvicorn app.main:app --host=0.0.0.0 --port=8000 --reload --workers 4
    ```
