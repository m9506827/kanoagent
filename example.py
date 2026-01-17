"""
使用範例：如何自訂 Crew 和 Agents
"""
from crewai import Crew, Process
from langchain_openai import ChatOpenAI
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

def custom_crew_example():
    """自訂 Crew 範例"""
    
    # 使用不同的 LLM 模型
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("請在 .env 檔案中設定 OPENAI_API_KEY")
    
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",  # 可以改用 gpt-3.5-turbo 以節省成本
        temperature=0.5,  # 降低溫度以獲得更一致的輸出
        openai_api_key=api_key,  # 明確傳遞 API key
    )
    
    # 創建 Agents
    product_manager = ProductManagerAgent(llm)
    designer = DesignerAgent(llm)
    architect = ArchitectAgent(llm)
    developer = DeveloperAgent(llm)
    reviewer = ReviewerAgent(llm)
    technical = TechnicalAgent(llm)
    
    # 創建任務
    tasks = create_tasks(
        product_manager,
        designer,
        architect,
        developer,
        reviewer,
        technical,
    )
    
    # 創建自訂 Crew
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
        process=Process.sequential,  # 或使用 Process.hierarchical 進行階層式協作
        verbose=True,
        # 可以添加更多自訂選項
        # max_iter=15,  # 最大迭代次數
        # memory=True,  # 啟用記憶功能
    )
    
    return crew

if __name__ == "__main__":
    print("自訂 Crew 範例")
    crew = custom_crew_example()
    result = crew.kickoff()
    print("\n執行結果：")
    print(result)
