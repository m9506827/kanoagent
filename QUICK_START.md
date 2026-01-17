# KanoAgent 快速開始指南

## 🚀 快速開始（3 步驟）

### 步驟 1：安裝依賴
```bash
pip install -r requirements.txt
```

### 步驟 2：配置環境變數
複製 `config.example.env` 為 `.env` 並填入您的 API Key：
```bash
# Windows
copy config.example.env .env

# Linux/Mac
cp config.example.env .env
```

編輯 `.env` 檔案：
```env
GOOGLE_API_KEY=your_google_api_key_here
```

### 步驟 3：執行
```bash
python main.py
```

## ⚙️ 進階配置

### 配置每個 Role 使用不同的 LLM

在 `.env` 檔案中設定：
```env
# 使用 API Model
PRODUCT_MANAGER_LLM_TYPE=api
DESIGNER_LLM_TYPE=api

# 使用 Local Model（需要先安裝 Ollama）
REVIEWER_LLM_TYPE=local
TECHNICAL_LLM_TYPE=local
```

### 配置重試機制
```env
# 設定重試次數
PRODUCT_MANAGER_RETRY_TIMES=5

# 設定重試延遲（秒）
PRODUCT_MANAGER_RETRY_DELAY=3.0
```

## 📚 更多資訊

- **進階功能：** 查看 `README_ADVANCED.md`
- **本地 LLM：** 查看 `LOCAL_LLM_RECOMMENDATIONS.md`
- **LLM 建議：** 查看 `LLM_RECOMMENDATIONS.md`
