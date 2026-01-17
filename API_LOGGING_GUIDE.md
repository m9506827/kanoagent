# API 調用日誌記錄指南

## 📊 當前配置分析

### 重要發現

**所有 Agent 都配置為使用 `gemini-2.0-flash`，不只是 quality 和 technical！**

| Agent | 配置 | 是否會調用 API |
|-------|------|---------------|
| 資深售前顧問 | `api` + `gemini-2.0-flash` | ✅ **是**（任務 0） |
| 產品經理 | `api` + `gemini-2.0-flash` | ✅ **是**（任務 1） |
| 設計師 | `api` + `gemini-2.0-flash` | ✅ **是**（任務 2） |
| 架構工程師 | `api` + `gemini-2.0-flash` | ✅ **是**（任務 3） |
| 開發工程師 | `api` + `gemini-2.0-flash` | ✅ **是**（任務 4） |
| 評審工程師 | `api` + `gemini-2.0-flash` | ✅ **是**（任務 5、6） |
| 技術支援 | `local` | ❌ **否**（無任務） |

**結論：有 6 個 Agent 會調用 API，總共約 12-18 次 API 調用！**

## 🔍 為什麼會用完配額？

### 原因分析

1. **所有 Agent 都使用 API**（除了 technical）
   - 6 個 Agent × 平均 2-3 次調用 = **12-18 次 API 調用**
   - 如果每次調用使用大量 tokens，很容易用完免費配額

2. **任務執行順序**
   - 任務 0-4 會立即執行（pre_sales → product → designer → architect → developer）
   - 這些任務都會調用 API
   - 任務 5-6（reviewer）在開發完成後才執行

3. **免費層級配額限制**
   - Google Gemini 免費層級有嚴格的 token 限制
   - 如果任務複雜，單次調用可能使用大量 tokens

## 📝 API 日誌記錄

### 已添加的功能

已創建 `utils/api_logger.py`，會記錄：

1. **每次 API 調用**
   - Agent 名稱
   - 模型名稱
   - 調用時間
   - 狀態（success/error/retry）
   - 持續時間

2. **日誌檔案**
   - `output/api_calls.log` - 每行一個 JSON 記錄
   - `output/api_calls.json` - 完整的 JSON 報告

### 查看日誌

執行完成後，會自動顯示統計摘要。也可以手動查看：

```bash
# 查看日誌檔案
cat output/api_calls.log

# 查看 JSON 報告
cat output/api_calls.json

# 統計每個 Agent 的調用次數（需要 jq）
cat output/api_calls.log | jq -r '.agent' | sort | uniq -c
```

## 🛠️ 解決方案

### 方案 1：只讓 Quality 和 Technical 使用 Gemini

在 `.env` 中設定：

```env
# 其他 Agent 使用 Local Model
PRE_SALES_CONSULTANT_LLM_TYPE=local
PRODUCT_MANAGER_LLM_TYPE=local
DESIGNER_LLM_TYPE=local
ARCHITECT_LLM_TYPE=local
DEVELOPER_LLM_TYPE=local

# 只有 Quality 和 Technical 使用 API
REVIEWER_LLM_TYPE=api
TECHNICAL_LLM_TYPE=api
```

**注意：** Technical Agent 目前沒有任務，所以實際上只有 Reviewer 會使用 API。

### 方案 2：混合使用（推薦）

```env
# 關鍵 Role 使用 API（品質更好）
PRE_SALES_CONSULTANT_LLM_TYPE=api
PRODUCT_MANAGER_LLM_TYPE=api
ARCHITECT_LLM_TYPE=api
DEVELOPER_LLM_TYPE=api

# 其他 Role 使用 Local（節省配額）
DESIGNER_LLM_TYPE=local
REVIEWER_LLM_TYPE=local
TECHNICAL_LLM_TYPE=local
```

### 方案 3：全部使用 Local Model

```env
# 所有 Role 使用 Local Model（完全免費）
PRE_SALES_CONSULTANT_LLM_TYPE=local
PRODUCT_MANAGER_LLM_TYPE=local
DESIGNER_LLM_TYPE=local
ARCHITECT_LLM_TYPE=local
DEVELOPER_LLM_TYPE=local
REVIEWER_LLM_TYPE=local
TECHNICAL_LLM_TYPE=local
```

## 📊 預期 API 調用次數

### 當前配置（所有 Agent 使用 API）

| Agent | 任務 | 預估 API 調用次數 |
|-------|------|-----------------|
| pre_sales_consultant | 需求澄清 | 2-3 次 |
| product_manager | PRD 生成 | 3-5 次 |
| designer | UI/UX 設計 | 2-3 次 |
| architect | 系統設計 | 3-4 次 |
| developer | 程式碼實作 | 4-6 次 |
| reviewer | Code Review | 2-3 次 |
| reviewer | 產品測試 | 2-3 次 |
| **總計** | | **18-27 次** |

### 如果只讓 Quality 使用 API

| Agent | 任務 | 預估 API 調用次數 |
|-------|------|-----------------|
| reviewer | Code Review | 2-3 次 |
| reviewer | 產品測試 | 2-3 次 |
| **總計** | | **4-6 次** |

## 🔍 診斷步驟

1. **檢查當前配置**
   ```python
   from config import get_llm_config
   
   for role in ["pre_sales_consultant", "product_manager", "designer", 
                "architect", "developer", "reviewer", "technical"]:
       config = get_llm_config(role)
       print(f"{role}: type={config['type']}, api_model={config['api_model']}")
   ```

2. **執行一次並查看日誌**
   ```bash
   python main.py
   # 執行完成後查看 output/api_calls.json
   ```

3. **分析 API 使用情況**
   - 查看哪些 Agent 實際調用了 API
   - 查看每次調用的時間和狀態
   - 確認是否有意外的 API 調用

## 📝 總結

### 關鍵發現

1. ✅ **所有 Agent 都配置為使用 gemini-2.0-flash**（除了 technical）
2. ✅ **實際有 6 個 Agent 會調用 API**，不只是 quality 和 technical
3. ✅ **Technical Agent 沒有任務**，不會執行
4. ✅ **已添加 API 日誌記錄功能**，可以追蹤每個 API 調用

### 建議

1. **立即檢查配置**：確認哪些 Agent 應該使用 API
2. **查看日誌**：執行一次後查看 `output/api_calls.json`
3. **調整配置**：根據實際需求調整 `.env` 中的配置
4. **監控使用**：定期查看 API 使用情況
