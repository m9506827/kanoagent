# KanoAgent 更新日誌

## 🎉 最新更新

### ✅ 已完成的功能

#### 1. 每個 Role 獨立配置 LLM
- ✅ 每個 Role 可以選擇使用 **API Model** 或 **Local Model**
- ✅ 支援混合使用（部分 Role 用 API，部分用 Local）
- ✅ 通過環境變數或配置檔案靈活配置
- ✅ 自動檢測 Ollama 可用性，智能切換

#### 2. 自動重試機制
- ✅ 可配置重試次數（預設 3 次）
- ✅ 可配置重試延遲（預設 2 秒）
- ✅ 指數退避策略（每次重試延遲 × 1.5）
- ✅ 智能錯誤識別（503、429 等自動重試）

#### 3. 優化的 Role 和 Task
- ✅ 更詳細的任務描述
- ✅ 更明確的產出要求
- ✅ 更好的上下文傳遞
- ✅ 明確的字數和品質要求

#### 4. 配置管理系統
- ✅ 統一的配置管理（`config/llm_config.py`）
- ✅ 環境變數支援
- ✅ 配置範例檔案（`config.example.env`）

## 📁 新增檔案

### 核心檔案
- `crew_advanced.py` - 進階版 Crew（推薦使用）
- `config/llm_config.py` - LLM 配置管理
- `utils/retry_handler.py` - 重試機制工具
- `config.example.env` - 環境變數配置範例

### 文檔檔案
- `README_ADVANCED.md` - 進階功能說明
- `QUICK_START.md` - 快速開始指南
- `LLM_RECOMMENDATIONS.md` - LLM 選擇建議
- `LOCAL_LLM_RECOMMENDATIONS.md` - 本地 LLM 建議
- `CHANGELOG.md` - 更新日誌（本檔案）

## 🔧 修改的檔案

### 主要修改
- `main.py` - 更新為使用進階版 Crew，增強錯誤處理
- `crew.py` - 更新為使用配置系統
- `tasks/tasks.py` - 優化任務描述，更詳細明確
- `requirements.txt` - 新增 requests 依賴
- `README.md` - 更新使用說明

### Agent 檔案
- 所有 Agent 檔案移除 `ChatOpenAI` 類型提示，支援靈活配置

## 🎯 配置範例

### 範例 1：全部使用 API
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
PRODUCT_MANAGER_LLM_TYPE=api
ARCHITECT_LLM_TYPE=api
DEVELOPER_LLM_TYPE=api
DESIGNER_LLM_TYPE=local
REVIEWER_LLM_TYPE=local
TECHNICAL_LLM_TYPE=local
```

### 範例 3：全部使用 Local（完全免費）
```env
PRODUCT_MANAGER_LLM_TYPE=local
DESIGNER_LLM_TYPE=local
ARCHITECT_LLM_TYPE=local
DEVELOPER_LLM_TYPE=local
REVIEWER_LLM_TYPE=local
TECHNICAL_LLM_TYPE=local
```

## 🚀 使用方式

### 快速開始
```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 配置環境變數
cp config.example.env .env
# 編輯 .env 填入 API Key

# 3. 執行
python main.py
```

## 📊 效能優化

### 重試機制
- **預設重試次數：** 3 次
- **預設延遲：** 2 秒
- **退避策略：** 指數退避（×1.5）
- **可配置：** 每個 Role 獨立配置

### 錯誤處理
- 自動識別可重試錯誤（503、429）
- 自動識別不可重試錯誤（404）
- 友好的錯誤訊息
- 智能建議解決方案

## 🔮 未來計劃

- [ ] 支援更多 LLM 提供者（Anthropic Claude、Azure OpenAI 等）
- [ ] 並行執行任務（如果硬體允許）
- [ ] 任務結果快取機制
- [ ] Web UI 介面
- [ ] 任務進度追蹤和報告

## 📝 注意事項

1. **Local Model 需要 Ollama**
   - 安裝：https://ollama.ai/download
   - 下載模型：`ollama pull llama3.3:70b`

2. **API Key 設定**
   - 至少需要一個 API Key（Google 或 OpenAI）
   - 如果全部使用 Local Model，則不需要 API Key

3. **硬體需求**
   - Local Model（70B）：需要約 40GB RAM
   - Local Model（3B）：需要約 4GB RAM
   - API Model：需要穩定的網路連接
