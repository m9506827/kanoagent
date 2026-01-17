# KanoAgent - 通用型軟體開發團隊

使用 CrewAI 實作的智能開發團隊，負責軟體專案的完整開發流程，從需求澄清到程式碼實作。

## 專案結構

```
KanoAgent/
├── agents/                  # Agent 定義
│   ├── __init__.py
│   ├── product.py          # 資深售前顧問、產品經理 & UI/UX 設計師 Agent
│   ├── engineer.py          # 架構工程師 & 開發工程師 Agent
│   ├── quality.py          # 評審與測試工程師 Agent
│   └── technical.py         # 技術支援 Agent
├── tasks/                   # 任務定義
│   ├── __init__.py
│   └── tasks.py
├── config/                  # 配置管理
│   ├── __init__.py
│   ├── llm_config.py        # LLM 配置
│   └── presales_questions.py # 售前顧問問題清單
├── utils/                   # 工具函數
│   ├── __init__.py
│   └── retry_handler.py     # 重試機制
├── output/                  # 輸出目錄
├── crew.py                  # 標準版 Crew
├── crew_advanced.py         # 進階版 Crew（推薦）
├── main.py                  # 主程式入口
├── config.example.env       # 環境變數範例
├── .gitignore
└── requirements.txt
```

## 安裝

```bash
pip install -r requirements.txt
```

## 環境設定

### 1. 創建 `.env` 檔案

在專案根目錄創建 `.env` 檔案並填入您的 Google AI API Key：

**Windows (PowerShell):**
```powershell
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

**或手動創建 `.env` 檔案：**
```
GOOGLE_API_KEY=your_google_api_key_here
```

**申請 Google AI API Key：**
- 前往：https://makersuite.google.com/app/apikey
- 登入 Google 帳號
- 點擊 "Create API Key"
- 複製 API Key 並貼到 `.env` 檔案中

**進階配置（可選）：**
- 複製 `config.example.env` 為 `.env` 進行詳細配置
- 每個 Role 可獨立設定使用 API 或 Local Model
- 可配置重試次數和延遲時間

### 2. 確認 Python 版本

CrewAI 需要 Python >= 3.10 且 < 3.14。建議使用 Python 3.12。

檢查版本：
```bash
python --version
```

### 3. 安裝依賴

```bash
pip install -r requirements.txt
```

**注意：** 如果使用 Python 3.13，可能會遇到一些相容性問題。建議使用 Python 3.12。

### 4. 進階配置（可選）

複製 `config.example.env` 為 `.env` 進行詳細配置：
```bash
cp config.example.env .env
```

在 `.env` 中可以配置：
- 每個 Role 使用 API 或 Local Model
- 重試次數和延遲時間
- 自訂模型名稱

詳細說明請查看 `README_ADVANCED.md`

## 使用方式

### 標準版（所有 Role 使用相同 LLM）
```bash
python main.py
```

### 進階版（每個 Role 可獨立配置）
```bash
python main.py  # 已更新為進階版
# 或
python crew_advanced.py
```

**進階功能：**
- ✅ 每個 Role 可獨立配置使用 API 或 Local Model
- ✅ 自動重試機制（可配置重試次數和延遲）
- ✅ 指數退避策略處理 API 過載
- ✅ 智能錯誤處理

詳細說明請查看 `README_ADVANCED.md`

## Agents 說明

### 1. Senior Pre-sales Consultant (資深售前顧問)
- **職責**：與客戶（用戶）互動，通過結構化問題澄清軟體需求
- **產出**：需求澄清文檔（Requirements Clarification Document）
- **背景**：擁有豐富的軟體專案需求分析經驗，擅長與客戶溝通
- **問題類別**：
  - 業務背景與目標
  - 用戶需求與使用場景
  - 功能需求
  - 非功能性需求
  - 技術約束與限制
  - 數據需求
  - 整合需求
  - UI/UX 需求
  - 專案約束（時程、預算、資源）
  - 成功標準

### 2. Product Manager (產品經理)
- **職責**：根據澄清後的需求，產出完整的 PRD (Product Requirements Document)
- **產出**：PRD 需求規格書（Markdown 格式）
- **背景**：將用戶需求轉化為可執行的產品規格
- **PRD 包含**：
  - 產品概述與目標
  - 用戶角色與使用場景
  - 功能需求清單（含優先級）
  - 用戶流程圖
  - 非功能性需求
  - 技術約束條件
  - 數據需求
  - 整合需求
  - UI/UX 需求
  - 專案約束與風險

### 3. Designer (UI/UX 設計師)
- **職責**：根據 PRD 設計用戶介面與用戶體驗
- **產出**：UI/UX 設計方案
- **背景**：創建直觀且美觀的用戶介面

### 4. Architect Engineer (架構工程師)
- **職責**：設計完整的系統架構，包括資料庫、API 和外部系統整合
- **產出**：System Design (系統設計文件)
- **背景**：設計可擴展且高效的系統架構

### 5. Developer (開發工程師)
- **職責**：根據系統設計撰寫程式碼並實作業務邏輯
- **產出**：Source Code (程式碼實作)
- **背景**：全端開發，能夠根據需求選擇合適的技術棧

### 6. Reviewer Testor (評審與測試工程師)
- **職責**：Code Review 和產品測試
- **產出**：Review Report (代碼評審報告) 和 Test Report (測試報告)
- **背景**：確保程式碼品質與安全性

### 7. Technical (技術支援)
- **職責**：技術支援與客戶服務
- **背景**：協助解決技術問題和用戶疑問

## 工作流程

1. **Senior Pre-sales Consultant** 與客戶互動，澄清需求並產出需求澄清文檔
2. **Product Manager** 根據需求澄清文檔產出 PRD
3. **Designer** 根據 PRD 設計 UI/UX
4. **Architect** 根據 PRD 和設計方案產出系統設計
5. **Developer** 根據系統設計實作程式碼
6. **Reviewer** 進行 Code Review 和測試
7. **Technical** 提供技術支援（可選）

所有任務按順序執行，每個 Agent 可以參考前續任務的產出。
