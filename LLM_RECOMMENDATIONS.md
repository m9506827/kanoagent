# KanoAgent LLM 配置建議

根據不同 Role 的特性，建議使用不同的 LLM 以獲得最佳效果。

## 📊 Role 與 LLM 對應表

| Role | 主要需求 | 推薦 LLM | 備選 LLM | 原因 |
|------|---------|---------|---------|------|
| **Product Manager** | 分析、規劃、文檔生成 | GPT-4 | Gemini Pro / Claude | 分析能力強，適合生成詳細的 PRD 文檔 |
| **Designer** | 創意、視覺設計 | Gemini Pro | GPT-4 | 多模態能力強，創意設計能力佳 |
| **Architect** | 技術深度、系統設計 | GPT-4 | Claude / Gemini Pro | 技術架構設計能力強，邏輯清晰 |
| **Developer** | 程式碼生成 | GPT-4 | CodeLlama / Gemini Pro | 程式碼生成能力最強，支援多種語言 |
| **Reviewer** | 分析、批判性思維 | GPT-4 | Claude / Gemini Pro | 分析能力強，能發現程式碼問題 |
| **Technical** | 快速回應、問題解決 | GPT-3.5-turbo | Gemini Flash | 速度快、成本低，適合快速回應 |

## 🎯 詳細說明

### 1. Product Manager (產品經理)
**任務特性：**
- 分析用戶需求
- 規劃產品功能
- 生成詳細的 PRD 文檔

**推薦 LLM：**
- **GPT-4** ⭐⭐⭐⭐⭐
  - 分析能力強
  - 文檔生成品質高
  - 邏輯清晰

- **Claude** ⭐⭐⭐⭐
  - 長文本處理能力強
  - 適合生成詳細文檔

- **Gemini Pro** ⭐⭐⭐
  - 免費額度
  - 文檔生成能力不錯

### 2. Designer (設計師)
**任務特性：**
- 創意設計
- 視覺設計思維
- UI/UX 設計方案

**推薦 LLM：**
- **Gemini Pro** ⭐⭐⭐⭐⭐
  - 多模態能力強
  - 創意設計能力佳
  - 免費額度

- **GPT-4** ⭐⭐⭐⭐
  - 創意能力也不錯
  - 但需要付費

### 3. Architect (架構工程師)
**任務特性：**
- 系統架構設計
- 技術深度要求高
- 資料庫、API 設計

**推薦 LLM：**
- **GPT-4** ⭐⭐⭐⭐⭐
  - 技術架構設計能力強
  - 邏輯清晰
  - 能處理複雜的系統設計

- **Claude** ⭐⭐⭐⭐
  - 技術能力強
  - 長文本處理

- **Gemini Pro** ⭐⭐⭐
  - 技術能力不錯
  - 免費額度

### 4. Developer (開發工程師)
**任務特性：**
- 程式碼生成
- 多語言支援（Python、Flutter）
- 程式碼品質要求高

**推薦 LLM：**
- **GPT-4** ⭐⭐⭐⭐⭐
  - 程式碼生成能力最強
  - 支援多種程式語言
  - 程式碼品質高

- **CodeLlama** ⭐⭐⭐⭐
  - 專門為程式碼設計
  - 開源免費

- **Gemini Pro** ⭐⭐⭐
  - 程式碼能力不錯
  - 免費額度

### 5. Reviewer (評審工程師)
**任務特性：**
- Code Review
- 發現問題和安全漏洞
- 分析能力要求高

**推薦 LLM：**
- **GPT-4** ⭐⭐⭐⭐⭐
  - 分析能力強
  - 能發現程式碼問題
  - 安全性檢查能力佳

- **Claude** ⭐⭐⭐⭐
  - 分析能力強
  - 能提供詳細的改進建議

- **Gemini Pro** ⭐⭐⭐
  - 分析能力不錯
  - 免費額度

### 6. Technical (技術支援)
**任務特性：**
- 快速回應
- 問題解決
- 成本考量

**推薦 LLM：**
- **GPT-3.5-turbo** ⭐⭐⭐⭐⭐
  - 速度快
  - 成本低
  - 回應品質足夠

- **Gemini Flash** ⭐⭐⭐⭐
  - 速度快
  - 免費額度
  - 適合快速回應

## 💰 成本考量

### 免費方案（推薦）
- 所有 Role 使用 **Gemini 2.5 Flash**
- 優點：完全免費，速度不錯
- 缺點：某些複雜任務可能品質略低

### 混合方案（平衡）
- Product Manager, Architect, Developer, Reviewer → **GPT-4**
- Designer → **Gemini Pro**
- Technical → **GPT-3.5-turbo**
- 優點：關鍵任務使用高品質模型，成本可控
- 缺點：需要 OpenAI API Key

### 高品質方案（最佳效果）
- 所有 Role 使用 **GPT-4**
- 優點：最佳品質
- 缺點：成本較高

## 🚀 使用方式

### 使用優化版本（推薦）
```bash
python crew_optimized.py
```

### 使用標準版本（所有 Role 使用相同 LLM）
```bash
python main.py
```

## 📝 環境變數設定

在 `.env` 檔案中設定：

```env
# Google Gemini（免費）
GOOGLE_API_KEY=your_google_api_key

# OpenAI（付費，但品質更好）
OPENAI_API_KEY=your_openai_api_key
```

## 🔧 自訂配置

可以修改 `crew_optimized.py` 中的 LLM 配置，根據您的需求調整。
