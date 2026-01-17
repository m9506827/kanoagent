# API 使用分析與日誌記錄

## 🔍 問題分析

### 當前配置檢查

根據 `config/llm_config.py`，**所有 Agent 都配置為使用 `gemini-2.0-flash`**：

| Agent | 配置鍵 | LLM 類型 | API 模型 |
|-------|--------|---------|----------|
| 資深售前顧問 | `pre_sales_consultant` | `api` | `gemini/gemini-2.0-flash` |
| 產品經理 | `product_manager` | `api` | `gemini/gemini-2.0-flash` |
| 設計師 | `designer` | `api` | `gemini/gemini-2.0-flash` |
| 架構工程師 | `architect` | `api` | `gemini/gemini-2.0-flash` |
| 開發工程師 | `developer` | `api` | `gemini/gemini-2.0-flash` |
| 評審工程師 | `reviewer` | `api` | `gemini/gemini-2.0-flash` |
| 技術支援 | `technical` | `local` | `gemini/gemini-2.0-flash`（備用） |

**結論：除了 `technical` 使用 `local`，其他 6 個 Agent 都使用 `gemini-2.0-flash`！**

### 任務執行順序與 API 調用

| 順序 | Agent | 任務 | 是否調用 API | 執行時機 |
|------|-------|------|-------------|---------|
| 0 | `pre_sales_consultant` | 需求澄清 | ✅ **是** | **立即執行** |
| 1 | `product_manager` | PRD 生成 | ✅ **是** | 任務 0 完成後 |
| 2 | `designer` | UI/UX 設計 | ✅ **是** | 任務 1 完成後 |
| 3 | `architect` | 系統設計 | ✅ **是** | 任務 1、2 完成後 |
| 4 | `developer` | 程式碼實作 | ✅ **是** | 任務 3 完成後 |
| 5 | `reviewer` | Code Review | ✅ **是** | 任務 4 完成後 |
| 6 | `reviewer` | 產品測試 | ✅ **是** | 任務 4 完成後 |
| - | `technical` | 無任務 | ❌ **否** | 不會執行 |

**實際使用 gemini-2.0-flash 的 Agent：**
- ✅ `pre_sales_consultant` - 立即執行
- ✅ `product_manager` - 第 1 個任務
- ✅ `designer` - 第 2 個任務
- ✅ `architect` - 第 3 個任務
- ✅ `developer` - 第 4 個任務
- ✅ `reviewer` - 第 5、6 個任務（2 個任務）
- ❌ `technical` - 沒有任務，不會調用

**總計：6 個 Agent × 平均 2-3 次調用 = 約 12-18 次 API 調用**

## 📊 API 調用日誌

### 日誌記錄功能

已添加 API 調用日誌記錄器（`utils/api_logger.py`），會記錄：

1. **每次 API 調用**
   - Agent 名稱
   - 使用的模型
   - LLM 類型（api/local）
   - 調用狀態（success/error/retry）
   - 時間戳
   - 持續時間
   - Token 使用量（如果可用）

2. **統計信息**
   - 總調用次數
   - 按 Agent 統計
   - 按模型統計
   - 成功/失敗/重試次數

3. **日誌檔案**
   - `output/api_calls.log` - 每行一個 JSON 記錄
   - `output/api_calls.json` - 完整的 JSON 報告

### 查看 API 調用記錄

執行完成後，會自動顯示統計摘要：

```
======================================================================
API 調用統計摘要
======================================================================
總調用次數: 18
成功: 16
失敗: 1
重試: 1

按 Agent 統計:
  pre_sales_consultant:
    總計: 3
    成功: 3
    失敗: 0
    重試: 0
  product_manager:
    總計: 4
    成功: 4
    失敗: 0
    重試: 0
  ...

按模型統計:
  gemini/gemini-2.0-flash: 18 次

詳細日誌已保存至: output/api_calls.log
======================================================================
```

### 手動查看日誌

```bash
# 查看日誌檔案
cat output/api_calls.log

# 或查看 JSON 報告
cat output/api_calls.json
```

## 🔍 診斷配額用盡問題

### 檢查步驟

1. **查看配置**
   ```python
   from config import get_llm_config
   
   for role in ["pre_sales_consultant", "product_manager", "designer", 
                "architect", "developer", "reviewer", "technical"]:
       config = get_llm_config(role)
       print(f"{role}: type={config['type']}, model={config['api_model']}")
   ```

2. **查看 API 調用日誌**
   ```bash
   # 查看最近的 API 調用
   tail -n 50 output/api_calls.log
   
   # 統計每個 Agent 的調用次數
   cat output/api_calls.log | jq -r '.agent' | sort | uniq -c
   ```

3. **檢查是否有其他程序使用同一個 API Key**
   - 查看 Google AI Studio 的使用記錄
   - 檢查是否有其他應用程序使用同一個 API Key

## 💡 解決方案

### 方案 1：只讓 Quality 和 Technical 使用 Gemini（如果這是您的意圖）

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

### 方案 2：混合使用（推薦）

```env
# 關鍵 Role 使用 API
PRE_SALES_CONSULTANT_LLM_TYPE=api
PRODUCT_MANAGER_LLM_TYPE=api
ARCHITECT_LLM_TYPE=api
DEVELOPER_LLM_TYPE=api

# 其他 Role 使用 Local
DESIGNER_LLM_TYPE=local
REVIEWER_LLM_TYPE=local
TECHNICAL_LLM_TYPE=local
```

### 方案 3：全部使用 Local Model

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

## 📝 總結

### 發現的問題

1. **所有 Agent 都配置為使用 gemini-2.0-flash**（除了 technical 是 local）
2. **實際有 6 個 Agent 會調用 API**，不只是 quality 和 technical
3. **Technical Agent 沒有任務**，不會執行

### 已添加的功能

1. ✅ API 調用日誌記錄器
2. ✅ 統計信息顯示
3. ✅ JSON 報告導出
4. ✅ 按 Agent 和模型統計

### 下一步

1. 執行一次完整的流程
2. 查看 `output/api_calls.log` 和 `output/api_calls.json`
3. 確認哪些 Agent 實際調用了 API
4. 根據實際使用情況調整配置
