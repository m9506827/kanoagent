# Agent 協作方式與工作流程說明

## 🤝 Agent 協作方式

### 執行模式：順序執行（Sequential）

KanoAgent 使用 **`Process.sequential`** 模式，這意味著：

- ✅ **順序執行**：任務按順序一個接一個執行
- ✅ **有依賴關係**：後續任務依賴前面任務的輸出
- ❌ **不是並行**：不會同時執行多個任務
- ✅ **協作方式**：通過 `context` 參數傳遞前一個任務的輸出

### 工作流程圖

```
開始
  ↓
任務 0: 資深售前顧問 (pre_sales_consultant)
  ↓ 產出：需求澄清文檔
任務 1: 產品經理 (product_manager)
  ↓ 使用：需求澄清文檔
  ↓ 產出：PRD 需求規格書
任務 2: UI/UX 設計師 (designer)
  ↓ 使用：PRD 需求規格書
  ↓ 產出：UI/UX 設計方案
任務 3: 架構工程師 (architect)
  ↓ 使用：PRD + 設計方案
  ↓ 產出：系統設計文件
任務 4: 開發工程師 (developer)
  ↓ 使用：系統設計文件
  ↓ 產出：程式碼實作
任務 5: 評審工程師 (reviewer) - Code Review
  ↓ 使用：程式碼實作
  ↓ 產出：代碼評審報告
任務 6: 評審工程師 (reviewer) - 產品測試
  ↓ 使用：程式碼實作
  ↓ 產出：測試報告
結束
```

## 📋 任務執行時機與 API 調用

### 任務執行順序

| 順序 | Agent | 任務 | 執行時機 | API 調用時機 |
|------|-------|------|---------|-------------|
| 0 | `pre_sales_consultant` | 需求澄清 | **立即執行** | 開始時立即調用 |
| 1 | `product_manager` | PRD 生成 | 任務 0 完成後 | 收到需求澄清文檔後 |
| 2 | `designer` | UI/UX 設計 | 任務 1 完成後 | 收到 PRD 後 |
| 3 | `architect` | 系統設計 | 任務 1、2 完成後 | 收到 PRD + 設計方案後 |
| 4 | `developer` | 程式碼實作 | 任務 3 完成後 | 收到系統設計文件後 |
| 5 | `reviewer` | Code Review | 任務 4 完成後 | 收到程式碼實作後 |
| 6 | `reviewer` | 產品測試 | 任務 4 完成後 | 收到程式碼實作後 |

### Quality (Reviewer) Agent 的執行時機

**Reviewer Agent 有 2 個任務：**

1. **任務 5：Code Review**
   - **執行時機**：開發工程師完成程式碼實作後
   - **輸入**：開發工程師產出的程式碼
   - **API 調用**：收到程式碼後，分析程式碼品質、安全性、效能等
   - **輸出**：代碼評審報告

2. **任務 6：產品測試**
   - **執行時機**：開發工程師完成程式碼實作後（與 Code Review 並行，但順序執行）
   - **輸入**：開發工程師產出的程式碼
   - **API 調用**：收到程式碼後，設計測試計劃、執行測試、產出測試報告
   - **輸出**：測試報告

**重要：**
- Reviewer Agent **不會在開始時調用 API**
- 只有在收到 `development_task` 的輸出後才會執行
- 通常在第 4 個任務（開發）完成後才會執行

### Technical Agent 的問題

**⚠️ 目前 Technical Agent 沒有被分配任何任務！**

這意味著：
- Technical Agent 被創建了，但不會執行任何工作
- 不會調用任何 API
- 不會產出任何結果

**建議：**
- 可以為 Technical Agent 添加任務（如技術支援、文檔撰寫等）
- 或者暫時不使用 Technical Agent

## 🔄 協作機制詳解

### Context 傳遞機制

每個任務通過 `context` 參數接收前一個任務的輸出：

```python
# 任務 1 依賴任務 0
prd_task = Task(
    description="...",
    agent=product_manager,
    context=[requirements_clarification_task],  # 接收任務 0 的輸出
)

# 任務 2 依賴任務 1
design_task = Task(
    description="...",
    agent=designer,
    context=[prd_task],  # 接收任務 1 的輸出
)
```

### 執行流程示例

**假設執行時間：**

```
時間軸：
0:00 - 開始執行
0:01 - pre_sales_consultant 開始（調用 API）
0:05 - pre_sales_consultant 完成，產出需求澄清文檔
0:06 - product_manager 開始（調用 API，使用需求澄清文檔）
0:12 - product_manager 完成，產出 PRD
0:13 - designer 開始（調用 API，使用 PRD）
0:18 - designer 完成，產出設計方案
0:19 - architect 開始（調用 API，使用 PRD + 設計方案）
0:28 - architect 完成，產出系統設計
0:29 - developer 開始（調用 API，使用系統設計）
0:45 - developer 完成，產出程式碼
0:46 - reviewer (Code Review) 開始（調用 API，使用程式碼）← 這裡才開始
0:52 - reviewer (Code Review) 完成
0:53 - reviewer (測試) 開始（調用 API，使用程式碼）
1:00 - reviewer (測試) 完成
1:01 - 全部完成
```

## 💡 關鍵理解

### 1. 順序執行，不是並行

- 任務按順序執行，不會同時執行多個任務
- 每個任務必須等待前一個任務完成

### 2. Quality 和 Technical 不會在開始時調用 API

- **Quality (Reviewer)**：只在收到開發工程師的程式碼後才執行
- **Technical**：目前沒有任務，不會執行

### 3. API 調用時機

- 每個 Agent 只在**執行自己的任務時**才會調用 API
- 不會在初始化時調用 API
- 不會在等待時調用 API

## 🛠️ 優化建議

### 如果希望 Technical Agent 有任務

可以添加技術支援相關任務，例如：

```python
# 任務 7: 技術支援 - 撰寫技術文檔
technical_doc_task = Task(
    description="""根據開發完成的程式碼，撰寫技術文檔和使用手冊。""",
    agent=technical,
    expected_output="完整的技術文檔和使用手冊",
    context=[development_task],
)
```

### 如果希望並行執行

可以改用 `Process.hierarchical` 或自訂流程，但需要更複雜的配置。

## 📊 總結

- **協作方式**：順序執行（Sequential），通過 context 傳遞結果
- **Quality Agent**：在開發完成後才執行，不會在開始時調用 API
- **Technical Agent**：目前沒有任務，不會執行
- **API 調用**：每個 Agent 只在執行自己的任務時才調用 API
