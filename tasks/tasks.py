from crewai import Task
from agents import (
    SeniorPreSalesConsultantAgent,
    ProductManagerAgent,
    DesignerAgent,
    ArchitectAgent,
    DeveloperAgent,
    ReviewerAgent,
    TechnicalAgent,
)
from config.presales_questions import format_questions_for_agent

def create_tasks(
    pre_sales_consultant,
    product_manager,
    designer,
    architect,
    developer,
    reviewer,
    technical,
    user_requirements_text: str = None,
):
    """創建所有任務
    
    Args:
        pre_sales_consultant: SeniorPreSalesConsultantAgent 實例
        product_manager: ProductManagerAgent 實例
        designer: DesignerAgent 實例
        architect: ArchitectAgent 實例
        developer: DeveloperAgent 實例
        reviewer: ReviewerAgent 實例
        technical: TechnicalAgent 實例
        user_requirements_text: 用戶通過交互式問卷提供的需求文本（可選）
    """
    
    # 構建任務描述
    if user_requirements_text:
        # 如果用戶已提供需求，Agent 只需要整理和補充
        task_description = f"""作為資深售前顧問，你的任務是基於客戶已提供的需求回答，整理並補充完整的需求澄清文檔。

**客戶已提供的需求信息：**

{user_requirements_text}

**你的任務：**
1. 仔細閱讀客戶提供的所有需求回答
2. 識別需求中的模糊點、矛盾點和潛在風險
3. 對於不清楚或缺失的部分，進行合理的推斷和補充
4. 確認需求的優先級和重要性
5. 整理並總結所有澄清後的需求

**注意事項：**
- 要基於客戶提供的實際回答進行整理
- 對於客戶未回答的問題，可以根據上下文進行合理推斷
- 要識別並記錄技術約束、業務規則、整合需求等關鍵信息
- 要確認時程、預算、資源等專案約束條件
- 最終要產出一份清晰、完整的需求澄清文檔

**輸出要求：**
產出一份結構化的需求澄清文檔，包含：
- 業務背景與目標
- 用戶需求與使用場景
- 功能需求清單（含優先級）
- 非功能性需求
- 技術約束與限制
- 數據需求
- 整合需求
- UI/UX 需求
- 專案約束（時程、預算、資源）
- 成功標準與驗收條件"""
    else:
        # 如果用戶未提供需求，Agent 需要模擬對話
        task_description = f"""作為資深售前顧問，你的任務是與客戶（用戶）互動，通過結構化的問題澄清軟體需求。

{format_questions_for_agent()}

**互動流程：**
1. 根據上述問題清單，系統化地向客戶詢問需求
2. 根據客戶的回答，進一步深入詢問相關細節
3. 識別需求中的模糊點、矛盾點和潛在風險
4. 確認需求的優先級和重要性
5. 整理並總結所有澄清後的需求

**注意事項：**
- 要友善、專業地與客戶溝通
- 對於不清楚的地方，要主動追問
- 要識別並記錄技術約束、業務規則、整合需求等關鍵信息
- 要確認時程、預算、資源等專案約束條件
- 最終要產出一份清晰、完整的需求澄清文檔

**輸出要求：**
產出一份結構化的需求澄清文檔，包含：
- 業務背景與目標
- 用戶需求與使用場景
- 功能需求清單（含優先級）
- 非功能性需求
- 技術約束與限制
- 數據需求
- 整合需求
- UI/UX 需求
- 專案約束（時程、預算、資源）
- 成功標準與驗收條件"""
    
    # 任務 0: 資深售前顧問 - 需求澄清
    requirements_clarification_task = Task(
        description=task_description,
        agent=pre_sales_consultant,
        expected_output="完整的需求澄清文檔（Markdown 格式），包含所有澄清後的需求信息，結構清晰、內容詳盡，字數不少於 1500 字",
    )
    
    # 任務 1: 產品經理 - 產出 PRD
    prd_task = Task(
        description="""作為產品經理，你的任務是根據資深售前顧問提供的需求澄清文檔，產出完整的 PRD (Product Requirements Document) 需求規格書。

**輸入：** 需求澄清文檔（來自資深售前顧問）

**任務要求：**
請基於需求澄清文檔，撰寫結構化、詳細的 PRD 文檔，必須包含以下內容：

1. **產品概述與目標**
   - 產品定位與核心價值
   - 目標用戶群體
   - 產品願景與目標
   - 商業目標與成功指標

2. **用戶角色與使用場景**
   - 主要用戶角色定義（Persona）
   - 典型使用場景描述（User Story）
   - 用戶痛點分析
   - 用戶旅程地圖

3. **功能需求清單**
   - 核心功能模組
   - 功能優先級排序（Must Have / Should Have / Nice to Have）
   - 功能詳細描述（包含輸入、處理邏輯、輸出）
   - 功能之間的關聯性和依賴關係
   - 業務規則和特殊邏輯

4. **用戶流程圖**
   - 主要用戶操作流程
   - 異常處理流程
   - 用戶體驗路徑
   - 系統狀態轉換圖

5. **非功能性需求**
   - 效能要求（響應時間、吞吐量、並發用戶數）
   - 安全性要求（數據加密、權限控制、合規要求）
   - 可用性要求（系統可用率、容錯機制）
   - 擴展性要求（未來擴展計劃）
   - 可維護性要求

6. **技術約束條件**
   - 技術棧限制（必須使用的技術）
   - 整合要求（外部系統、第三方服務、API）
   - 部署環境要求（雲端、本地、混合）
   - 數據存儲和備份要求
   - 技術標準和規範

7. **數據需求**
   - 數據模型設計（實體、屬性、關係）
   - 數據來源和流向
   - 數據驗證規則
   - 數據遷移計劃（如適用）

8. **整合需求**
   - 外部系統整合清單
   - 整合方式和協議
   - 數據格式和接口規範
   - 整合的實時性要求

9. **UI/UX 需求**
   - 設計風格和品牌指南
   - 用戶介面要求
   - 響應式設計要求
   - 多語言支援（如適用）

10. **專案約束與風險**
    - 時程約束
    - 預算約束
    - 資源約束
    - 技術風險
    - 業務風險

**輸出格式：**
- 使用 Markdown 格式
- 結構清晰，層次分明
- 內容詳盡，便於開發團隊理解
- 包含必要的圖表描述（用文字描述）""",
        agent=product_manager,
        expected_output="完整的 PRD 需求規格書文件（Markdown 格式），包含所有功能點、用戶路徑、技術約束條件的詳細描述，結構清晰、內容完整，字數不少於 3000 字",
        context=[requirements_clarification_task],
    )
    
    # 任務 2: 設計師 - UI/UX 設計
    design_task = Task(
        description="""作為 UI/UX 設計師，你的任務是根據 PRD 文件設計軟體系統的用戶介面與用戶體驗。

請產出完整的 UI/UX 設計方案，必須包含以下內容：

1. **用戶介面設計稿**
   - 主要頁面佈局設計
   - 組件設計規範
   - 視覺層級設計

2. **用戶體驗流程圖**
   - 完整用戶操作流程
   - 頁面跳轉邏輯
   - 互動反饋設計

3. **互動設計說明**
   - 互動元素設計
   - 動畫與過渡效果
   - 用戶操作引導

4. **視覺設計規範**
   - 色彩系統定義
   - 字體系統定義
   - 圖標與插圖風格

5. **響應式設計方案**
   - 移動端適配方案
   - 平板端適配方案
   - 桌面端適配方案

請確保設計方案符合 PRD 中的功能需求和用戶體驗要求。""",
        agent=designer,
        expected_output="完整的 UI/UX 設計方案文件（Markdown 格式），包含設計稿描述、流程圖、設計規範和響應式方案，字數不少於 1500 字",
        context=[prd_task],
    )
    
    # 任務 3: 架構工程師 - 系統設計
    architecture_task = Task(
        description="""作為架構工程師，你的任務是根據 PRD 和設計方案，設計完整的系統架構。

請產出完整的系統設計文件，必須包含以下內容：

1. **系統架構圖**
   - 整體系統架構設計（分層架構、微服務架構等）
   - 模組劃分與職責
   - 技術棧選型說明（根據 PRD 中的技術約束）

2. **資料庫結構設計 (ER Diagram)**
   - 資料庫選型（PostgreSQL/MySQL/MongoDB/其他）
   - 資料表結構設計
   - 資料關係圖（ER Diagram）
   - 索引設計策略
   - 數據遷移計劃

3. **API 規格文件 (RESTful API 設計)**
   - API 端點設計（根據功能需求）
   - 請求/回應格式定義
   - 認證與授權機制
   - API 版本管理策略
   - 錯誤處理機制

4. **外部系統整合設計**
   - 整合架構設計（根據 PRD 中的整合需求）
   - 整合方式和協議
   - 數據格式和接口規範
   - 錯誤處理和重試機制

5. **系統部署架構**
   - 部署環境設計（雲端、本地、混合）
   - 容器化方案（Docker/Kubernetes）
   - 負載均衡策略
   - 監控與日誌方案
   - 備份與災難恢復方案

6. **資料流程圖**
   - 資料流向設計
   - 資料處理流程
   - 快取策略設計
   - 數據同步機制

7. **安全性設計**
   - 認證與授權機制
   - 數據加密方案
   - 安全防護措施
   - 合規性設計

請確保架構設計符合 PRD 中的技術約束、效能要求和整合需求。""",
        agent=architect,
        expected_output="完整的系統設計文件（Markdown 格式），包含架構圖描述、資料庫設計、API 規格、外部系統整合方案和部署架構，字數不少於 2500 字",
        context=[prd_task, design_task],
    )
    
    # 任務 4: 開發工程師 - 程式碼實作
    development_task = Task(
        description="""作為開發工程師，你的任務是根據系統設計文件，撰寫完整的程式碼實作。

請根據 PRD 和系統設計文件，實作以下內容：

1. **後端 API 實作**
   - 根據架構設計選擇的框架（Flask/FastAPI/Express/其他）
   - 實作所有 API 端點（根據 API 規格文件）
   - 錯誤處理與驗證邏輯
   - 認證與授權實作
   - 單元測試程式碼

2. **前端應用程式實作**
   - 根據 PRD 選擇的前端技術（React/Vue/Flutter/其他）
   - 主要頁面實作（根據 UI/UX 設計）
   - 狀態管理
   - API 整合程式碼
   - 用戶介面組件

3. **資料庫模型與遷移腳本**
   - ORM 模型定義（根據資料庫設計）
   - 資料庫遷移腳本
   - 種子資料腳本（如需要）

4. **外部系統整合實作**
   - 根據 PRD 中的整合需求實作整合邏輯
   - API 客戶端或 SDK 整合
   - 數據格式轉換
   - 錯誤處理和重試機制

5. **核心業務邏輯實作**
   - 根據 PRD 中的功能需求實作業務邏輯
   - 業務規則實作
   - 數據處理和計算邏輯
   - 歷史記錄和日誌功能

6. **必要的配置檔案和依賴管理**
   - 依賴管理檔案（requirements.txt / package.json / pubspec.yaml 等）
   - 環境配置檔案
   - Docker 配置檔案（如適用）
   - README 說明文件
   - API 文檔

請確保程式碼品質高、可讀性強、遵循最佳實踐，並符合 PRD 中的所有功能需求。""",
        agent=developer,
        expected_output="完整的程式碼實作，包含後端 API、前端應用、資料庫腳本、外部系統整合程式碼和配置檔案，所有程式碼必須可執行，並符合 PRD 中的所有功能需求",
        context=[architecture_task],
    )
    
    # 任務 5: 評審工程師 - Code Review
    review_task = Task(
        description="""對開發完成的程式碼進行 Code Review。
        產出代碼評審報告包括：
        1. 程式碼品質評估
        2. 安全性檢查結果
        3. 效能優化建議
        4. 程式碼風格檢查
        5. 潛在問題與改進建議
        6. 最佳實踐遵循情況""",
        agent=reviewer,
        expected_output="詳細的代碼評審報告，包含所有發現的問題和改進建議",
        context=[development_task],
    )
    
    # 任務 6: 測試工程師 - 產品測試
    test_task = Task(
        description="""對開發完成的產品進行全面測試。
        產出測試報告包括：
        1. 測試計劃與策略
        2. 單元測試結果
        3. 整合測試結果
        4. 端對端測試結果
        5. 效能測試結果
        6. 安全性測試結果
        7. 測試覆蓋率報告
        8. Bug 清單與修復建議""",
        agent=reviewer,
        expected_output="完整的測試報告，包含所有測試結果和 Bug 清單",
        context=[development_task],
    )
    
    return [
        requirements_clarification_task,
        prd_task,
        design_task,
        architecture_task,
        development_task,
        review_task,
        test_task,
    ]

# 個別任務函數（方便單獨使用）
def create_requirements_clarification_task(pre_sales_consultant):
    """創建需求澄清任務"""
    from config.presales_questions import format_questions_for_agent
    return Task(
        description=f"""與客戶互動，通過結構化問題澄清軟體需求。

{format_questions_for_agent()}

產出完整的需求澄清文檔。""",
        agent=pre_sales_consultant,
        expected_output="完整的需求澄清文檔（Markdown 格式）",
    )

def create_prd_task(product_manager, requirements_clarification_task):
    """創建 PRD 任務"""
    return Task(
        description="""根據需求澄清文檔，產出完整的 PRD (Product Requirements Document) 需求規格書。""",
        agent=product_manager,
        expected_output="完整的 PRD 需求規格書文件（Markdown 格式）",
        context=[requirements_clarification_task],
    )

def create_design_task(designer, prd_task):
    """創建設計任務"""
    return Task(
        description="""根據 PRD 文件設計軟體系統的 UI/UX 介面。""",
        agent=designer,
        expected_output="完整的 UI/UX 設計方案",
        context=[prd_task],
    )

def create_architecture_task(architect, prd_task, design_task):
    """創建架構設計任務"""
    return Task(
        description="""根據 PRD 和設計方案，設計完整的系統架構，包括資料庫、API 和外部系統整合。""",
        agent=architect,
        expected_output="完整的系統設計文件",
        context=[prd_task, design_task],
    )

def create_development_task(developer, architecture_task):
    """創建開發任務"""
    return Task(
        description="""根據系統設計文件，撰寫完整的 Python/Flutter 程式碼實作。""",
        agent=developer,
        expected_output="完整的程式碼實作",
        context=[architecture_task],
    )

def create_review_task(reviewer, development_task):
    """創建代碼評審任務"""
    return Task(
        description="""對開發完成的程式碼進行 Code Review，產出代碼評審報告。""",
        agent=reviewer,
        expected_output="詳細的代碼評審報告",
        context=[development_task],
    )

def create_test_task(reviewer, development_task):
    """創建測試任務"""
    return Task(
        description="""對開發完成的產品進行全面測試，產出測試報告。""",
        agent=reviewer,
        expected_output="完整的測試報告",
        context=[development_task],
    )
