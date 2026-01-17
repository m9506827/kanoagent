# API 配額用盡處理指南

## 🔍 問題識別

### 配額用盡錯誤特徵

當您看到以下錯誤訊息時，表示 API 配額已用盡：

```
429 RESOURCE_EXHAUSTED
You exceeded your current quota, please check your plan and billing details.
Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_input_token_count, limit: 0
```

**關鍵指標：**
- 錯誤代碼：`429`
- 錯誤類型：`RESOURCE_EXHAUSTED`
- 關鍵字：`quota exceeded`、`exceeded your current quota`、`limit: 0`

### 與 API 過載的區別

| 錯誤類型 | 錯誤代碼 | 原因 | 解決方案 |
|---------|---------|------|---------|
| **配額用盡** | 429 + quota exceeded | 免費層級配額已用完 | 切換到 Local Model 或其他 API |
| **API 過載** | 503 或 429 rate limit | 服務器暫時過載 | 等待後重試 |
| **速率限制** | 429 rate limit | 請求過於頻繁 | 增加延遲後重試 |

## 🛠️ 解決方案

### 方案 1：切換到 Local Model（推薦，完全免費）

**優點：**
- ✅ 完全免費
- ✅ 無配額限制
- ✅ 本地運行，速度快
- ✅ 數據隱私

**設定步驟：**

1. **安裝 Ollama**
   ```bash
   # Windows
   winget install Ollama.Ollama
   
   # 或下載：https://ollama.ai/download
   ```

2. **下載模型**
   ```bash
   ollama pull llama3.3:70b
   ollama pull deepseek-coder:33b
   ollama pull llama3.2:3b
   ```

3. **在 .env 中設定**
   ```env
   # 所有 Role 使用 Local Model
   PRE_SALES_CONSULTANT_LLM_TYPE=local
   PRODUCT_MANAGER_LLM_TYPE=local
   DESIGNER_LLM_TYPE=local
   ARCHITECT_LLM_TYPE=local
   DEVELOPER_LLM_TYPE=local
   REVIEWER_LLM_TYPE=local
   TECHNICAL_LLM_TYPE=local
   ```

4. **啟動 Ollama 服務**
   ```bash
   # Ollama 會自動在背景運行
   # 或手動啟動：
   ollama serve
   ```

### 方案 2：切換到其他 API

#### 選項 A：使用 DeepSeek API

**優點：**
- ✅ 價格便宜
- ✅ 配額較多
- ✅ 程式碼能力強

**設定步驟：**

1. **申請 DeepSeek API Key**
   - 前往：https://platform.deepseek.com/api_keys
   - 登入並創建 API Key

2. **在 .env 中設定**
   ```env
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   ```

3. **修改 config/llm_config.py**
   ```python
   "product_manager": {
       "type": "api",
       "api_model": "deepseek/deepseek-chat",  # 改為 DeepSeek
       # ...
   }
   ```

#### 選項 B：使用 OpenAI API

**優點：**
- ✅ 品質高
- ✅ 穩定可靠

**缺點：**
- ❌ 價格較高
- ❌ 需要付費

**設定步驟：**

1. **申請 OpenAI API Key**
   - 前往：https://platform.openai.com/api-keys
   - 登入並創建 API Key

2. **在 .env 中設定**
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **修改 config/llm_config.py**
   ```python
   "product_manager": {
       "type": "api",
       "api_model": "gpt-4",  # 或 "gpt-3.5-turbo"
       # ...
   }
   ```

### 方案 3：升級到付費計劃

**適用於：**
- 需要繼續使用 Google Gemini API
- 有預算升級

**步驟：**
1. 前往：https://ai.google.dev/pricing
2. 選擇適合的付費計劃
3. 設定付款方式
4. 配額會立即增加

### 方案 4：等待配額重置

**適用於：**
- 免費層級配額通常每月重置一次
- 不急於使用

**查看配額使用情況：**
- 前往：https://ai.dev/rate-limit
- 查看當前使用量和重置時間

## 📊 混合使用策略（推薦）

**最佳實踐：** 關鍵 Role 使用 API，其他 Role 使用 Local Model

```env
# 關鍵 Role 使用 API（品質更好）
PRODUCT_MANAGER_LLM_TYPE=api
ARCHITECT_LLM_TYPE=api
DEVELOPER_LLM_TYPE=api

# 其他 Role 使用 Local Model（節省成本）
DESIGNER_LLM_TYPE=local
REVIEWER_LLM_TYPE=local
TECHNICAL_LLM_TYPE=local
```

**效果：**
- 減少 API 使用量約 43%
- 保持關鍵任務的品質
- 大幅降低 API 成本

## 🔄 自動切換機制

KanoAgent 已內建自動降級機制：

```python
# 在 config/llm_config.py 中
{
    "auto_fallback": True,  # 啟用自動降級
}
```

當 API 配額用盡時，系統會：
1. 自動重試（最多 5 次）
2. 如果持續失敗，自動切換到 Local Model（如果已配置）

## 📝 快速參考

### 立即切換到 Local Model

```env
# 在 .env 檔案中添加
PRE_SALES_CONSULTANT_LLM_TYPE=local
PRODUCT_MANAGER_LLM_TYPE=local
DESIGNER_LLM_TYPE=local
ARCHITECT_LLM_TYPE=local
DEVELOPER_LLM_TYPE=local
REVIEWER_LLM_TYPE=local
TECHNICAL_LLM_TYPE=local
```

### 檢查 Ollama 是否運行

```bash
# 檢查 Ollama 服務
curl http://localhost:11434/api/tags

# 或查看已下載的模型
ollama list
```

### 查看配額使用情況

- **Google Gemini：** https://ai.dev/rate-limit
- **DeepSeek：** https://platform.deepseek.com/usage
- **OpenAI：** https://platform.openai.com/usage

## ⚠️ 重要提醒

1. **配額用盡不可重試**
   - 配額用盡時，重試不會解決問題
   - 必須切換到其他方案

2. **免費層級限制**
   - Google Gemini 免費層級有嚴格的配額限制
   - 建議使用 Local Model 或升級到付費計劃

3. **Local Model 需要資源**
   - 需要足夠的 RAM（建議 16GB+）
   - 需要下載模型（可能數 GB）

## 🎯 總結

當遇到配額用盡錯誤時：

1. ✅ **立即切換到 Local Model**（最簡單、最經濟）
2. ✅ **或切換到其他 API**（如 DeepSeek）
3. ✅ **或升級到付費計劃**（如果需要繼續使用 Gemini）
4. ❌ **不要重試**（配額用盡時重試無效）

詳細的 Local Model 設定請參考：`LOCAL_LLM_RECOMMENDATIONS.md`
