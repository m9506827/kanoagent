"""
優化版 Crew - 根據不同 Role 使用不同的 LLM
"""
from crewai import Crew, Process
from agents import (
    ProductManagerAgent,
    DesignerAgent,
    ArchitectAgent,
    DeveloperAgent,
    ReviewerAgent,
    TechnicalAgent,
)
from tasks.tasks import create_tasks
import os
from dotenv import load_dotenv

load_dotenv()

def create_plant_diagnosis_crew_optimized():
    """創建植物診斷系統開發團隊 - 根據 Role 優化 LLM 配置"""
    
    # 確保環境變數已設定
    google_api_key = os.getenv("GOOGLE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not google_api_key and not openai_api_key:
        raise ValueError(
            "請在 .env 檔案中設定至少一個 API Key:\n"
            "- GOOGLE_API_KEY (推薦)\n"
            "- OPENAI_API_KEY\n"
        )
    
    # 設置環境變數
    if google_api_key:
        os.environ["GOOGLE_API_KEY"] = google_api_key
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
    
    # ============================================
    # 根據 Role 特性配置不同的 LLM
    # ============================================
    
    # 1. Product Manager - 需要分析、規劃、文檔生成
    # 推薦：GPT-4 或 Claude（長文本、分析能力強）
    # 備選：Gemini Pro（如果沒有 OpenAI/Anthropic）
    if openai_api_key:
        pm_llm = "gpt-4"  # 最佳：分析能力強，適合 PRD 生成
    elif google_api_key:
        pm_llm = "gemini/gemini-2.5-flash"  # 備選：快速且免費
    else:
        pm_llm = "gemini/gemini-2.5-flash"
    
    # 2. Designer - 需要創意、視覺設計思維
    # 推薦：Gemini Pro（多模態、創意能力強）
    # 備選：GPT-4（創意能力也不錯）
    if google_api_key:
        designer_llm = "gemini/gemini-2.5-flash"  # 最佳：創意和多模態能力
    elif openai_api_key:
        designer_llm = "gpt-4"  # 備選
    else:
        designer_llm = "gemini/gemini-2.5-flash"
    
    # 3. Architect - 需要技術深度、系統設計
    # 推薦：GPT-4 或 Claude（技術能力強、邏輯清晰）
    # 備選：Gemini Pro
    if openai_api_key:
        architect_llm = "gpt-4"  # 最佳：技術架構設計能力強
    elif google_api_key:
        architect_llm = "gemini/gemini-2.5-flash"  # 備選
    else:
        architect_llm = "gemini/gemini-2.5-flash"
    
    # 4. Developer - 需要程式碼生成能力
    # 推薦：GPT-4 或 CodeLlama（程式碼能力最強）
    # 備選：Gemini Pro（程式碼能力也不錯）
    if openai_api_key:
        developer_llm = "gpt-4"  # 最佳：程式碼生成能力最強
    elif google_api_key:
        developer_llm = "gemini/gemini-2.5-flash"  # 備選：程式碼能力不錯
    else:
        developer_llm = "gemini/gemini-2.5-flash"
    
    # 5. Reviewer - 需要分析、批判性思維
    # 推薦：GPT-4 或 Claude（分析能力強、能發現問題）
    # 備選：Gemini Pro
    if openai_api_key:
        reviewer_llm = "gpt-4"  # 最佳：分析能力強，適合 Code Review
    elif google_api_key:
        reviewer_llm = "gemini/gemini-2.5-flash"  # 備選
    else:
        reviewer_llm = "gemini/gemini-2.5-flash"
    
    # 6. Technical - 需要快速回應、問題解決
    # 推薦：GPT-3.5 或 Gemini Flash（速度快、成本低）
    # 備選：Gemini Flash
    if openai_api_key:
        technical_llm = "gpt-3.5-turbo"  # 最佳：速度快、成本低
    elif google_api_key:
        technical_llm = "gemini/gemini-2.5-flash"  # 備選：快速且免費
    else:
        technical_llm = "gemini/gemini-2.5-flash"
    
    # 創建所有 Agents（使用不同的 LLM）
    product_manager = ProductManagerAgent(pm_llm)
    designer = DesignerAgent(designer_llm)
    architect = ArchitectAgent(architect_llm)
    developer = DeveloperAgent(developer_llm)
    reviewer = ReviewerAgent(reviewer_llm)
    technical = TechnicalAgent(technical_llm)
    
    # 顯示使用的 LLM 配置
    print("\n" + "="*60)
    print("LLM 配置（根據 Role 優化）")
    print("="*60)
    print(f"Product Manager: {pm_llm}")
    print(f"Designer:        {designer_llm}")
    print(f"Architect:       {architect_llm}")
    print(f"Developer:       {developer_llm}")
    print(f"Reviewer:        {reviewer_llm}")
    print(f"Technical:       {technical_llm}")
    print("="*60 + "\n")
    
    # 創建所有任務
    tasks = create_tasks(
        product_manager,
        designer,
        architect,
        developer,
        reviewer,
        technical,
    )
    
    # 創建 Crew
    crew = Crew(
        agents=[
            product_manager,
            designer,
            architect,
            developer,
            reviewer,
            technical,
        ],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )
    
    return crew

if __name__ == "__main__":
    crew = create_plant_diagnosis_crew_optimized()
    result = crew.kickoff()
    print("\n" + "="*50)
    print("專案完成！")
    print("="*50)
    print(result)
