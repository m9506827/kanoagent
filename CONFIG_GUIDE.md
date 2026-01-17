# KanoAgent 配置指南

## 📍 模型設定位置

### 主要配置檔案

1. **`.env` 檔案**（專案根目錄）- 推薦使用
   - 環境變數配置
   - 優先級最高
   - 不會被提交到 Git

2. **`config/llm_config.py`** - Python 配置檔案
   - 預設配置值
   - 可作為備選方案

## 🔧 配置方式

### 方法 1：使用 .env 檔案（推薦）

在專案根目錄創建或編輯 `.env` 檔案：

```env
# API Keys
GOOGLE_API_KEY=your_google_api_key_here

# 每個 Role 的 LLM 類型（api 或 local）
PRODUCT_MANAGER_LLM_TYPE=api
DESIGNER_LLM_TYPE=api
ARCHITECT_LLM_TYPE=api
DEVELOPER_LLM_TYPE=api
REVIEWER_LLM_TYPE=api
TECHNICAL_LLM_TYPE=local

# 自訂模型名稱（可選）
PRODUCT_MANAGER_API_MODEL=gemini/gemini-2.0-flash
ARCHITECT_API_MODEL=gemini/gemini-2.0-flash
```

### 方法 2：修改 config/llm_config.py

編輯 `config/llm_config.py` 中的 `DEFAULT_LLM_CONFIG`：

```python
DEFAULT_LLM_CONFIG = {
    "product_manager": {
        "type": "api",  # 改為 "local" 使用本地模型
        "api_model": "gemini/gemini-2.0-flash",
        "local_model": "ollama/llama3.3:70b",
        "retry_times": 3,
        "retry_delay": 2.0,
    },
    # ... 其他配置
}
```

## 📋 Role 與配置鍵對應表

| Agent 檔案 | Agent 函數 | 配置鍵名稱 |
|-----------|-----------|-----------|
| `product.py` | ProductManagerAgent | `product_manager` |
| `product.py` | DesignerAgent | `designer` |
| `engineer.py` | ArchitectAgent | `architect` |
| `engineer.py` | DeveloperAgent | `developer` |
| `quality.py` | ReviewerAgent | `reviewer` |
| `technical.py` | TechnicalAgent | `technical` |

## 🎯 可用的 Gemini 模型

根據測試，以下模型可用：

### 穩定版本（推薦）
- `gemini/gemini-2.0-flash` ⭐ 推薦（最穩定）
- `gemini/gemini-2.0-flash-001`
- `gemini/gemini-2.0-flash-lite`

### 最新版本（可能不穩定）
- `gemini/gemini-2.5-flash`
- `gemini/gemini-2.5-flash-preview-09-2025`

### 實驗版本
- `gemini/gemini-2.0-flash-exp`
- `gemini/gemini-3-flash-preview`

**建議：** 使用 `gemini-2.0-flash` 作為預設，因為它更穩定且廣泛支援。

## ⚙️ 環境變數命名規則

### LLM 類型
```
{ROLE}_LLM_TYPE=api 或 local
```

範例：
```env
PRODUCT_MANAGER_LLM_TYPE=api
DESIGNER_LLM_TYPE=local
```

### 模型名稱
```
{ROLE}_API_MODEL=模型名稱
{ROLE}_LOCAL_MODEL=模型名稱
```

範例：
```env
PRODUCT_MANAGER_API_MODEL=gemini/gemini-2.0-flash
ARCHITECT_LOCAL_MODEL=ollama/deepseek-coder:33b
```

### 重試配置
```
{ROLE}_RETRY_TIMES=次數
{ROLE}_RETRY_DELAY=延遲秒數
```

範例：
```env
PRODUCT_MANAGER_RETRY_TIMES=5
PRODUCT_MANAGER_RETRY_DELAY=3.0
```

## 🔍 配置優先順序

1. **環境變數**（`.env` 檔案）- 最高優先級
2. **`config/llm_config.py` 中的預設值** - 備選

## 📝 快速參考

### 全部使用 API Model
```env
PRODUCT_MANAGER_LLM_TYPE=api
DESIGNER_LLM_TYPE=api
ARCHITECT_LLM_TYPE=api
DEVELOPER_LLM_TYPE=api
REVIEWER_LLM_TYPE=api
TECHNICAL_LLM_TYPE=api
```

### 全部使用 Local Model
```env
PRODUCT_MANAGER_LLM_TYPE=local
DESIGNER_LLM_TYPE=local
ARCHITECT_LLM_TYPE=local
DEVELOPER_LLM_TYPE=local
REVIEWER_LLM_TYPE=local
TECHNICAL_LLM_TYPE=local
```

### 混合使用（推薦）
```env
# 關鍵 Role 使用 API
PRODUCT_MANAGER_LLM_TYPE=api
ARCHITECT_LLM_TYPE=api
DEVELOPER_LLM_TYPE=api

# 其他 Role 使用 Local
DESIGNER_LLM_TYPE=local
REVIEWER_LLM_TYPE=local
TECHNICAL_LLM_TYPE=local
```
