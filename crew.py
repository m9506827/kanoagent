"""
標準版 Crew - 所有 Role 使用相同的 LLM
保留此檔案以向後相容
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
from config import get_llm_for_role
import os
from dotenv import load_dotenv

load_dotenv()

def create_plant_diagnosis_crew():
    """創建植物診斷系統開發團隊 - 標準版（所有 Role 使用相同 LLM）"""
    
    # 使用配置系統獲取預設 LLM
    # 預設使用 product_manager 的配置
    # 注意：配置鍵名稱對應 Agent 函數名稱（小寫加底線）
    llm = get_llm_for_role("product_manager")
    
    # 確保環境變數已設定（如果是 API model）
    if llm.startswith("gemini/") or llm.startswith("gpt-"):
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "請在 .env 檔案中設定 API Key\n"
                "- GOOGLE_API_KEY (用於 Gemini)\n"
                "- OPENAI_API_KEY (用於 GPT)"
            )
    
    # 創建所有 Agents（使用相同的 LLM）
    product_manager = ProductManagerAgent(llm)
    designer = DesignerAgent(llm)
    architect = ArchitectAgent(llm)
    developer = DeveloperAgent(llm)
    reviewer = ReviewerAgent(llm)
    technical = TechnicalAgent(llm)
    
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
        process=Process.sequential,  # 順序執行任務
        verbose=True,
    )
    
    return crew

if __name__ == "__main__":
    crew = create_plant_diagnosis_crew()
    result = crew.kickoff()
    print("\n" + "="*50)
    print("專案完成！")
    print("="*50)
    print(result)
