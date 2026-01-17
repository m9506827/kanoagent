"""
資深售前顧問問題清單
用於與客戶互動，澄清軟體需求
"""

# 核心問題類別
PRESALES_QUESTION_CATEGORIES = {
    "business_context": {
        "name": "業務背景與目標",
        "questions": [
            "請描述您的業務背景和行業領域？",
            "這個軟體專案要解決的核心業務問題是什麼？",
            "專案的商業目標和預期成果是什麼？",
            "這個專案對您的業務有什麼戰略意義？",
            "專案成功後，您期望看到什麼樣的業務指標改善？",
        ]
    },
    "user_requirements": {
        "name": "用戶需求與使用場景",
        "questions": [
            "主要使用者是誰？（角色、職責、技術背景）",
            "使用者會在什麼場景下使用這個系統？",
            "使用者目前是如何處理這些需求的？（現有流程或工具）",
            "使用者在使用現有解決方案時遇到的主要痛點是什麼？",
            "使用者對新系統的期望和優先級是什麼？",
        ]
    },
    "functional_requirements": {
        "name": "功能需求",
        "questions": [
            "系統需要實現哪些核心功能？",
            "每個功能的詳細需求是什麼？（輸入、處理、輸出）",
            "功能之間的關聯性和依賴關係是什麼？",
            "哪些功能是必須的（Must Have），哪些是重要的（Should Have），哪些是可有可無的（Nice to Have）？",
            "是否有特殊業務規則或邏輯需要實現？",
            "系統需要與哪些外部系統或服務整合？",
        ]
    },
    "non_functional_requirements": {
        "name": "非功能性需求",
        "questions": [
            "預期的用戶數量是多少？（並發用戶數、總用戶數）",
            "系統需要處理的資料量級是多少？（數據量、交易量）",
            "對系統響應時間有什麼要求？",
            "系統的可用性要求是什麼？（99.9%？）",
            "對系統安全性有什麼特殊要求？（數據加密、權限控制、合規要求）",
            "系統需要支援哪些平台？（Web、移動端、桌面應用）",
            "是否需要離線功能？",
        ]
    },
    "technical_constraints": {
        "name": "技術約束與限制",
        "questions": [
            "是否有偏好的技術棧或必須使用的技術？（程式語言、框架、資料庫）",
            "是否有必須整合的現有系統或第三方服務？",
            "是否有技術標準或規範需要遵循？（API 標準、數據格式）",
            "對系統架構有什麼要求？（微服務、單體、混合）",
            "是否有雲端或本地部署的偏好？",
            "是否有特殊的效能或擴展性要求？",
        ]
    },
    "data_requirements": {
        "name": "數據需求",
        "questions": [
            "系統需要處理哪些類型的數據？",
            "數據的來源是什麼？（用戶輸入、外部系統、文件導入）",
            "數據的格式和結構是什麼？",
            "是否需要數據遷移或歷史數據導入？",
            "對數據的存儲、備份、歸檔有什麼要求？",
            "是否需要數據分析或報表功能？",
        ]
    },
    "integration_requirements": {
        "name": "整合需求",
        "questions": [
            "系統需要與哪些外部系統整合？（ERP、CRM、支付系統等）",
            "整合的方式是什麼？（API、文件交換、數據庫直連）",
            "整合的數據格式和協議是什麼？",
            "整合的實時性要求是什麼？（實時、批次、定時）",
            "是否有現有的 API 或接口文檔？",
        ]
    },
    "ui_ux_requirements": {
        "name": "用戶介面與體驗",
        "questions": [
            "對用戶介面的風格有什麼偏好？（簡潔、專業、現代、傳統）",
            "是否有參考的設計風格或競品？",
            "對用戶體驗有什麼特殊要求？（易用性、可訪問性）",
            "是否需要多語言支援？",
            "是否需要響應式設計（適配不同設備）？",
        ]
    },
    "project_constraints": {
        "name": "專案約束",
        "questions": [
            "專案的預算範圍是多少？",
            "專案的時程要求是什麼？（開始時間、里程碑、上線時間）",
            "專案團隊的規模和技能背景是什麼？",
            "是否有必須遵守的法規或合規要求？",
            "專案的風險和挑戰是什麼？",
        ]
    },
    "success_criteria": {
        "name": "成功標準",
        "questions": [
            "如何定義專案成功？（關鍵指標、驗收標準）",
            "專案上線後的維護和支援需求是什麼？",
            "是否需要培訓或文檔？",
            "專案後續的擴展計劃是什麼？",
        ]
    }
}

def get_all_questions() -> list:
    """獲取所有問題的扁平化列表"""
    all_questions = []
    for category in PRESALES_QUESTION_CATEGORIES.values():
        all_questions.extend(category["questions"])
    return all_questions

def get_questions_by_category(category_key: str) -> list:
    """根據類別獲取問題"""
    if category_key in PRESALES_QUESTION_CATEGORIES:
        return PRESALES_QUESTION_CATEGORIES[category_key]["questions"]
    return []

def format_questions_for_agent() -> str:
    """格式化問題供 Agent 使用"""
    formatted = "資深售前顧問需要向客戶詢問以下問題，以全面了解軟體需求：\n\n"
    
    for category_key, category_data in PRESALES_QUESTION_CATEGORIES.items():
        formatted += f"## {category_data['name']}\n\n"
        for i, question in enumerate(category_data["questions"], 1):
            formatted += f"{i}. {question}\n"
        formatted += "\n"
    
    return formatted
