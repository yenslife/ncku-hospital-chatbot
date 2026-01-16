# 我在腎邊，你問我懂

這是成大醫院的聊天機器人專案，回答你所有和洗腎相關的問題。

以 Dify 作為主要 LLM Service 後端，前端則是用 Linebot，這個 Repo 主要是 Linebot 的部分。

## 開發環境設置

### 安裝套件

請務必確保執行的系統有安裝 sqlite3 和 redis

```bash
cd linebot
uv sync
```

### 設定 Pre-commit Hook

Pre-commit 會在每次 commit 時自動執行程式碼檢查和格式化：

```bash
pip install pre-commit
pre-commit install  # 安裝 hook
pre-commit run --all-files  # 手動執行檢查
```

### 執行服務

```bash
cp .env.example .env  # 複製環境變數設定檔並填入你的值
uv run uvicorn app.main:app --host=0.0.0.0 --port=8000 --reload --workers 4
```

## TODOs

- [x] 支援語音功能
    - [x] 串接 gpt-4o-mini-transcribe
    - [x] 將轉換好的文字傳送到 Dify
- [ ] 收到需求圖片後，記得要更新 Rich Menu
- [ ] 等測得差不多後，寫一個 .service 檔案，然後用 systemd 啟動服務
