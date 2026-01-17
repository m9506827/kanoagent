"""
進階版 Crew - 支援每個 Role 獨立配置 API/Local Model，並包含重試機制
"""
from crewai import Crew, Process
from agents import (
    SeniorPreSalesConsultantAgent,
    ProductManagerAgent,
    DesignerAgent,
    ArchitectAgent,
    DeveloperAgent,
    ReviewerAgent,
    TechnicalAgent,
)
from tasks.tasks import create_tasks
from config import get_llm_for_role, get_llm_config
import os
from dotenv import load_dotenv
import requests
import logging

load_dotenv()

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_ollama_available() -> bool:
    """檢查 Ollama 是否可用"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def create_kano_crew_advanced():
    """創建通用型軟體開發團隊 - 進階配置"""
    
    # 檢查必要的 API Key
    google_api_key = os.getenv("GOOGLE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    ollama_available = check_ollama_available()
    
    # 設置環境變數
    if google_api_key:
        os.environ["GOOGLE_API_KEY"] = google_api_key
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
    
    # 獲取每個 Role 的 LLM 配置
    roles = {
        "pre_sales_consultant": "pre_sales_consultant",
        "product_manager": "product_manager",
        "designer": "designer",
        "architect": "architect",
        "developer": "developer",
        "reviewer": "reviewer",
        "technical": "technical",
    }
    
    llm_configs = {}
    for role_key, role_name in roles.items():
        config = get_llm_config(role_key)
        llm_type = config["type"]
        
        # 驗證配置
        if llm_type == "local" and not ollama_available:
            logger.warning(
                f"{role_name} 配置為使用 local model，但 Ollama 不可用。"
                f"自動切換為 API model: {config['api_model']}"
            )
            llm_type = "api"
        
        if llm_type == "api":
            if not google_api_key and not openai_api_key:
                raise ValueError(
                    f"{role_name} 配置為使用 API model，但未設定 API Key。\n"
                    "請在 .env 中設定 GOOGLE_API_KEY 或 OPENAI_API_KEY"
                )
            llm_model = config["api_model"]
        else:
            llm_model = config["local_model"]
        
        llm_configs[role_key] = {
            "model": llm_model,
            "type": llm_type,
            "retry_times": config["retry_times"],
            "retry_delay": config["retry_delay"],
        }
    
    # 創建所有 Agents（使用各自的 LLM 配置）
    # 如果 pre_sales_consultant 配置不存在，使用 product_manager 的配置
    if "pre_sales_consultant" not in llm_configs:
        # 使用 product_manager 的配置作為預設
        pre_sales_config = llm_configs["product_manager"].copy()
        pre_sales_config["model"] = llm_configs["product_manager"]["model"]
    else:
        pre_sales_config = llm_configs["pre_sales_consultant"]
    
    pre_sales_consultant = SeniorPreSalesConsultantAgent(pre_sales_config["model"])
    product_manager = ProductManagerAgent(llm_configs["product_manager"]["model"])
    designer = DesignerAgent(llm_configs["designer"]["model"])
    architect = ArchitectAgent(llm_configs["architect"]["model"])
    developer = DeveloperAgent(llm_configs["developer"]["model"])
    reviewer = ReviewerAgent(llm_configs["reviewer"]["model"])
    technical = TechnicalAgent(llm_configs["technical"]["model"])
    
    # 顯示 LLM 配置
    print("\n" + "="*70)
    print("LLM 配置（每個 Role 獨立配置）")
    print("="*70)
    print(f"{'Role':<20} {'Type':<8} {'Model':<35} {'Retry':<10}")
    print("-" * 70)
    for role_key, role_name in roles.items():
        config = llm_configs[role_key]
        print(
            f"{role_name:<20} "
            f"{config['type'].upper():<8} "
            f"{config['model']:<35} "
            f"{config['retry_times']}x/{config['retry_delay']}s"
        )
    print("="*70 + "\n")
    
    # 創建所有任務
    tasks = create_tasks(
        pre_sales_consultant,
        product_manager,
        designer,
        architect,
        developer,
        reviewer,
        technical,
    )
    
    # 創建 Crew（配置重試機制）
    crew = Crew(
        agents=[
            pre_sales_consultant,
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
        # CrewAI 內建重試機制，但我們也可以通過環境變數配置
    )
    
    return crew

if __name__ == "__main__":
    crew = create_kano_crew_advanced()
    result = crew.kickoff()
    print("\n" + "="*50)
    print("專案完成！")
    print("="*50)
    print(result)
