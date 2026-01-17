# KanoAgent 進階版使用指南

## 🚀 新功能特色

### 1. 每個 Role 獨立配置 LLM
- ✅ 每個 Role 可以選擇使用 **API Model** 或 **Local Model**
- ✅ 支援混合使用（部分 Role 用 API，部分用 Local）
- ✅ 可通過環境變數靈活配置

### 2. 自動重試機制
- ✅ 可配置重試次數和延遲時間
- ✅ 指數退避策略處理 API 過載
- ✅ 智能錯誤處理（503、429 等錯誤自動重試）

### 3. 優化的 Role 和 Task
- ✅ 更詳細的任務描述
- ✅ 更明確的產出要求
- ✅ 更好的上下文傳遞

## 📋 配置方式

### 方法 1：使用環境變數（推薦）

複製 `config.example.env` 為 `.env` 並配置：

```env
# API Keys
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key  # 可選

# 每個 Role 的 LLM 類型
PRODUCT_MANAGER_LLM_TYPE=api      # 或 "local"
DESIGNER_LLM_TYPE=api
ARCHITECT_LLM_TYPE=api
DEVELOPER_LLM_TYPE=api
REVIEWER_LLM_TYPE=api
TECHNICAL_LLM_TYPE=local          # 技術支援使用本地模型（速度快）

# 重試配置（可選）
PRODUCT_MANAGER_RETRY_TIMES=3
PRODUCT_MANAGER_RETRY_DELAY=2.0
```

### 方法 2：修改配置檔案

編輯 `config/llm_config.py` 中的 `DEFAULT_LLM_CONFIG`：

```python
DEFAULT_LLM_CONFIG = {
    "product_manager": {
        "type": "api",  # 改為 "local" 使用本地模型
        "api_model": "gemini/gemini-2.5-flash",
        "local_model": "ollama/llama3.3:70b",
        "retry_times": 3,
        "retry_delay": 2.0,
    },
    # ... 其他配置
}
```

## 🎯 使用範例

### 範例 1：全部使用 API Model
```env
PRODUCT_MANAGER_LLM_TYPE=api
DESIGNER_LLM_TYPE=api
ARCHITECT_LLM_TYPE=api
DEVELOPER_LLM_TYPE=api
REVIEWER_LLM_TYPE=api
TECHNICAL_LLM_TYPE=api
```

### 範例 2：混合使用（推薦）
```env
# 關鍵 Role 使用 API（品質更好）
PRODUCT_MANAGER_LLM_TYPE=api
ARCHITECT_LLM_TYPE=api
DEVELOPER_LLM_TYPE=api

# 其他 Role 使用 Local（節省成本）
DESIGNER_LLM_TYPE=local
REVIEWER_LLM_TYPE=local
TECHNICAL_LLM_TYPE=local
```

### 範例 3：全部使用 Local Model（完全免費）
```env
PRODUCT_MANAGER_LLM_TYPE=local
DESIGNER_LLM_TYPE=local
ARCHITECT_LLM_TYPE=local
DEVELOPER_LLM_TYPE=local
REVIEWER_LLM_TYPE=local
TECHNICAL_LLM_TYPE=local
```

**注意：** 使用 Local Model 需要先安裝並運行 Ollama。

## 🔧 重試機制說明

### 自動重試的錯誤類型
- ✅ 503 (Service Unavailable) - 服務暫時不可用
- ✅ 429 (Rate Limit) - 請求過於頻繁
- ✅ "overloaded" - 模型過載
- ✅ "UNAVAILABLE" - 服務不可用

### 重試策略
- **初始延遲：** 2 秒（可配置）
- **退避策略：** 指數退避（每次重試延遲時間 × 1.5）
- **最大重試次數：** 3 次（可配置）

### 配置重試參數
```env
# 設定重試次數
PRODUCT_MANAGER_RETRY_TIMES=5

# 設定重試延遲（秒）
PRODUCT_MANAGER_RETRY_DELAY=3.0
```

## 📊 Role 與 LLM 建議配置

| Role | 推薦配置 | 原因 |
|------|---------|------|
| Product Manager | API (Gemini/GPT-4) | 需要高品質的分析和文檔生成 |
| Designer | Local (Llama 3.3) | 創意設計，本地模型足夠 |
| Architect | API (Gemini/GPT-4) | 技術架構設計需要高品質 |
| Developer | API (Gemini/GPT-4) | 程式碼生成需要高品質 |
| Reviewer | Local (Llama 3.3) | 分析任務，本地模型足夠 |
| Technical | Local (Llama 3.2 3B) | 快速回應，小模型即可 |

## 🚀 執行方式

### 使用進階版（推薦）
```bash
python main.py
# 或
python crew_advanced.py
```

### 使用標準版（所有 Role 相同 LLM）
```bash
python crew.py
```

## 📝 輸出說明

執行時會顯示：
1. 每個 Role 使用的 LLM 類型（API/Local）
2. 使用的模型名稱
3. 重試配置（次數/延遲）
4. 執行進度
5. 最終結果保存在 `output/result.txt`

## ⚠️ 注意事項

1. **Local Model 需要 Ollama**
   - 安裝：https://ollama.ai/download
   - 下載模型：`ollama pull llama3.3:70b`

2. **API Key 設定**
   - 至少需要一個 API Key（Google 或 OpenAI）
   - 如果全部使用 Local Model，則不需要 API Key

3. **重試機制**
   - CrewAI 內建重試機制
   - 我們的配置會增強重試邏輯
   - 遇到 503 錯誤會自動等待並重試

4. **效能考量**
   - Local Model 需要足夠的 RAM（70B 模型需要約 40GB）
   - API Model 需要穩定的網路連接

## 🔍 故障排除

### 問題：Local Model 無法連接
**解決：** 確保 Ollama 正在運行
```bash
# 檢查 Ollama 狀態
curl http://localhost:11434/api/tags
```

### 問題：API 持續返回 503
**解決：** 
1. 增加重試次數和延遲
2. 等待一段時間後重試
3. 檢查 API 額度是否用完

### 問題：模型名稱錯誤
**解決：** 檢查 `config/llm_config.py` 中的模型名稱是否正確
