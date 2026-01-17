"""
使用本地開源 LLM 的 Crew 配置
不考慮成本，追求最佳開源模型配置
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

def create_plant_diagnosis_crew_local_llm():
    """創建植物診斷系統開發團隊 - 使用本地開源 LLM（最佳配置）"""
    
    # ============================================
    # 本地開源 LLM 配置（通過 Ollama）
    # ============================================
    
    # 檢查 Ollama 是否運行
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code != 200:
            raise ConnectionError("Ollama 未運行")
    except:
        raise ValueError(
            "請先啟動 Ollama 服務：\n"
            "1. 安裝 Ollama: https://ollama.ai/download\n"
            "2. 下載模型（見下方建議）\n"
            "3. 確保 Ollama 正在運行"
        )
    
    # ============================================
    # 根據 Role 配置最佳開源 LLM
    # ============================================
    
    # 1. Product Manager - 需要分析、規劃、文檔生成
    # 推薦：Llama 3.3 70B 或 Qwen2.5 72B（文檔生成能力強）
    pm_llm = "ollama/llama3.3:70b"  # 最佳：分析能力強，適合 PRD
    # 備選：ollama/qwen2.5:72b（中文能力更強）
    
    # 2. Designer - 需要創意、視覺設計思維
    # 推薦：Llama 3.3 70B 或 Mistral Large（創意能力強）
    designer_llm = "ollama/llama3.3:70b"  # 最佳：創意設計能力佳
    # 備選：ollama/mistral-large（創意能力也不錯）
    
    # 3. Architect - 需要技術深度、系統設計
    # 推薦：DeepSeek Coder 或 CodeLlama 70B（技術能力最強）
    architect_llm = "ollama/deepseek-coder:33b"  # 最佳：技術架構設計能力強
    # 備選：ollama/codellama:70b
    
    # 4. Developer - 需要程式碼生成能力
    # 推薦：DeepSeek Coder 或 CodeLlama 70B（程式碼能力最強）
    developer_llm = "ollama/deepseek-coder:33b"  # 最佳：程式碼生成能力最強
    # 備選：ollama/codellama:70b
    
    # 5. Reviewer - 需要分析、批判性思維
    # 推薦：Llama 3.3 70B 或 Qwen2.5 72B（分析能力強）
    reviewer_llm = "ollama/llama3.3:70b"  # 最佳：分析能力強，適合 Code Review
    # 備選：ollama/qwen2.5:72b
    
    # 6. Technical - 需要快速回應、問題解決
    # 推薦：Llama 3.2 3B 或 Phi-3（速度快）
    technical_llm = "ollama/llama3.2:3b"  # 最佳：速度快，回應品質足夠
    # 備選：ollama/phi3:14b
    
    # 創建所有 Agents（使用不同的本地 LLM）
    product_manager = ProductManagerAgent(pm_llm)
    designer = DesignerAgent(designer_llm)
    architect = ArchitectAgent(architect_llm)
    developer = DeveloperAgent(developer_llm)
    reviewer = ReviewerAgent(reviewer_llm)
    technical = TechnicalAgent(technical_llm)
    
    # 顯示使用的 LLM 配置
    print("\n" + "="*60)
    print("本地開源 LLM 配置（最佳配置）")
    print("="*60)
    print(f"Product Manager: {pm_llm}")
    print(f"Designer:        {designer_llm}")
    print(f"Architect:       {architect_llm}")
    print(f"Developer:       {developer_llm}")
    print(f"Reviewer:        {reviewer_llm}")
    print(f"Technical:       {technical_llm}")
    print("="*60)
    print("\n💡 提示：確保已下載所有需要的模型")
    print("   使用命令：ollama pull <model_name>\n")
    
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
    crew = create_plant_diagnosis_crew_local_llm()
    result = crew.kickoff()
    print("\n" + "="*50)
    print("專案完成！")
    print("="*50)
    print(result)
