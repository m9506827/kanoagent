# API 過載應對指南

## 📋 目錄

1. [問題識別](#問題識別)
2. [自動應對機制](#自動應對機制)
3. [手動配置](#手動配置)
4. [最佳實踐](#最佳實踐)
5. [故障排除](#故障排除)

## 🔍 問題識別

### API 過載的常見錯誤訊息

- `503 UNAVAILABLE` - 服務暫時不可用
- `429 Too Many Requests` - 請求過於頻繁
- `overloaded` - 模型過載
- `rate limit` - 達到速率限制
- `RESOURCE_EXHAUSTED` - 資源耗盡
- `SERVICE_UNAVAILABLE` - 服務不可用

### 錯誤特徵

- **暫時性**：通常是暫時的，等待一段時間後會恢復
- **可重試**：這些錯誤通常可以通過重試解決
- **非致命**：不會導致永久性失敗

## 🛡️ 自動應對機制

KanoAgent 已內建多層防護機制：

### 1. 智能重試機制

```python
# 自動重試配置（config/llm_config.py）
{
    "retry_times": 5,          # 最多重試 5 次
    "retry_delay": 3,          # 初始延遲 3 秒
    "retry_backoff": 1.5,      # 指數退避（每次延遲 × 1.5）
    "max_retry_delay": 60,     # 最大延遲 60 秒
}
```

**重試時間表：**
- 第 1 次重試：等待 3 秒
- 第 2 次重試：等待 4.5 秒（3 × 1.5）
- 第 3 次重試：等待 6.75 秒（4.5 × 1.5）
- 第 4 次重試：等待 10.125 秒（6.75 × 1.5）
- 第 5 次重試：等待 15.1875 秒（10.125 × 1.5）

### 2. 指數退避策略

避免同時發送大量請求，減少對 API 的壓力：

```
延遲時間 = min(基礎延遲 × (退避倍數 ^ 嘗試次數), 最大延遲)
```

### 3. 隨機抖動（Jitter）

添加 ±20% 的隨機抖動，避免多個請求同時重試（雷群效應）：

```
實際延遲 = 計算延遲 ± (計算延遲 × 0.2 × 隨機數)
```

### 4. 自動降級（Auto Fallback）

當 API 持續過載時，自動切換到本地模型：

```python
{
    "auto_fallback": True,  # 啟用自動降級
    "local_model": "ollama/llama3.3:70b"  # 降級目標
}
```

## ⚙️ 手動配置

### 方法 1：修改 `.env` 檔案（推薦）

```env
# 增加重試次數
PRODUCT_MANAGER_RETRY_TIMES=10
DESIGNER_RETRY_TIMES=10
ARCHITECT_RETRY_TIMES=10

# 增加初始延遲
PRODUCT_MANAGER_RETRY_DELAY=5
DESIGNER_RETRY_DELAY=5

# 調整退避倍數（更大的值 = 更長的等待）
PRODUCT_MANAGER_RETRY_BACKOFF=2.0

# 設定最大延遲（防止等待過久）
PRODUCT_MANAGER_MAX_RETRY_DELAY=120

# 啟用/停用自動降級
PRODUCT_MANAGER_AUTO_FALLBACK=true
```

### 方法 2：修改 `config/llm_config.py`

```python
DEFAULT_LLM_CONFIG = {
    "product_manager": {
        "type": "api",
        "api_model": "gemini/gemini-2.0-flash",
        "local_model": "ollama/llama3.3:70b",
        "retry_times": 10,        # 增加到 10 次
        "retry_delay": 5,          # 增加到 5 秒
        "retry_backoff": 2.0,      # 更激進的退避
        "max_retry_delay": 120,    # 最大 2 分鐘
        "auto_fallback": True,     # 啟用自動降級
    },
    # ... 其他配置
}
```

### 方法 3：直接切換到 Local Model

如果 API 持續過載，直接使用本地模型：

```env
# 全部切換到 Local Model
PRODUCT_MANAGER_LLM_TYPE=local
DESIGNER_LLM_TYPE=local
ARCHITECT_LLM_TYPE=local
DEVELOPER_LLM_TYPE=local
REVIEWER_LLM_TYPE=local
TECHNICAL_LLM_TYPE=local
```

## 💡 最佳實踐

### 1. 分層防護策略

```
API Model (主要)
    ↓ (過載時)
自動重試（5 次，指數退避）
    ↓ (仍失敗)
自動降級到 Local Model
    ↓ (仍失敗)
手動切換配置
```

### 2. 關鍵 Role 優先

對於關鍵的 Role（如 `architect`、`developer`），使用更保守的重試策略：

```env
# 關鍵 Role：更多重試、更長延遲
ARCHITECT_RETRY_TIMES=10
ARCHITECT_RETRY_DELAY=5
ARCHITECT_MAX_RETRY_DELAY=180

# 非關鍵 Role：較少重試、較短延遲
DESIGNER_RETRY_TIMES=3
DESIGNER_RETRY_DELAY=2
DESIGNER_MAX_RETRY_DELAY=30
```

### 3. 混合使用策略

部分 Role 使用 API，部分使用 Local：

```env
# 關鍵決策使用 API（重試更多）
PRODUCT_MANAGER_LLM_TYPE=api
PRODUCT_MANAGER_RETRY_TIMES=10

ARCHITECT_LLM_TYPE=api
ARCHITECT_RETRY_TIMES=10

# 其他使用 Local（避免 API 壓力）
DESIGNER_LLM_TYPE=local
REVIEWER_LLM_TYPE=local
TECHNICAL_LLM_TYPE=local
```

### 4. 監控和日誌

啟用詳細日誌以監控重試行為：

```python
# 在 main.py 中
import logging
logging.basicConfig(level=logging.INFO)
```

## 🔧 故障排除

### 問題 1：持續收到 503 錯誤

**可能原因：**
- API 額度已用完
- API 服務暫時中斷
- 請求頻率過高

**解決方案：**

1. **檢查 API 額度**
   ```bash
   # 查看 Google AI Studio 的額度使用情況
   # https://aistudio.google.com/app/apikey
   ```

2. **增加重試配置**
   ```env
   PRODUCT_MANAGER_RETRY_TIMES=15
   PRODUCT_MANAGER_RETRY_DELAY=10
   PRODUCT_MANAGER_MAX_RETRY_DELAY=300
   ```

3. **切換到 Local Model**
   ```env
   PRODUCT_MANAGER_LLM_TYPE=local
   ```

### 問題 2：重試時間過長

**解決方案：**

1. **減少最大延遲**
   ```env
   PRODUCT_MANAGER_MAX_RETRY_DELAY=30
   ```

2. **減少重試次數**
   ```env
   PRODUCT_MANAGER_RETRY_TIMES=3
   ```

3. **啟用自動降級**
   ```env
   PRODUCT_MANAGER_AUTO_FALLBACK=true
   ```

### 問題 3：自動降級不工作

**檢查項目：**

1. **確認 Ollama 運行中**
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **確認 Local Model 已下載**
   ```bash
   ollama list
   ```

3. **檢查配置**
   ```env
   PRODUCT_MANAGER_AUTO_FALLBACK=true
   PRODUCT_MANAGER_LOCAL_MODEL=ollama/llama3.3:70b
   ```

### 問題 4：所有重試都失敗

**最終解決方案：**

1. **等待一段時間後重試**（5-10 分鐘）
2. **檢查 API 服務狀態**
3. **切換到完全使用 Local Model**
4. **檢查網路連接**
5. **驗證 API Key 有效性**

## 📊 配置建議表

| 場景 | 重試次數 | 初始延遲 | 退避倍數 | 最大延遲 | 自動降級 |
|------|---------|---------|---------|---------|---------|
| **正常使用** | 5 | 3秒 | 1.5 | 60秒 | ✅ |
| **API 不穩定** | 10 | 5秒 | 1.5 | 120秒 | ✅ |
| **高頻請求** | 3 | 2秒 | 2.0 | 30秒 | ✅ |
| **關鍵任務** | 15 | 5秒 | 1.5 | 180秒 | ✅ |
| **測試環境** | 2 | 1秒 | 1.2 | 10秒 | ❌ |

## 🎯 快速參考

### 立即應對 API 過載

```env
# 1. 增加重試次數和延遲
PRODUCT_MANAGER_RETRY_TIMES=10
PRODUCT_MANAGER_RETRY_DELAY=5
PRODUCT_MANAGER_MAX_RETRY_DELAY=120

# 2. 啟用自動降級
PRODUCT_MANAGER_AUTO_FALLBACK=true

# 3. 或直接切換到 Local
PRODUCT_MANAGER_LLM_TYPE=local
```

### 檢查當前配置

```python
from config import get_llm_config

config = get_llm_config("product_manager")
print(f"重試次數: {config['retry_times']}")
print(f"初始延遲: {config['retry_delay']}秒")
print(f"自動降級: {config.get('auto_fallback', False)}")
```

## 📝 總結

KanoAgent 已內建完善的 API 過載應對機制：

✅ **自動重試** - 最多 5 次，指數退避  
✅ **智能延遲** - 避免過度請求  
✅ **隨機抖動** - 防止雷群效應  
✅ **自動降級** - 切換到本地模型  
✅ **可配置** - 根據需求調整  

當遇到 API 過載時，系統會自動處理，無需手動干預。如果持續失敗，可以通過配置調整或切換到 Local Model 來解決。
