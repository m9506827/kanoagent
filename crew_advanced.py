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
from utils.api_logger import get_api_logger
import os
from dotenv import load_dotenv
import requests
import logging
import time

load_dotenv()

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化 API 日誌記錄器
api_logger = get_api_logger()

def check_ollama_available() -> bool:
    """檢查 Ollama 是否可用（包括服務運行和模組可導入）"""
    # 檢查模組是否可導入
    try:
        from langchain_community.llms import Ollama
    except ImportError:
        logger.debug("langchain_community 模組不可用")
        return False
    
    # 檢查服務是否運行
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        logger.debug("Ollama 服務不可用")
        return False

def create_llm_instance(model_name: str, llm_type: str, agent_name: str = "unknown"):
    """
    根據模型名稱和類型創建 LLM 實例
    
    Args:
        model_name: 模型名稱（如 "gemini/gemini-2.0-flash" 或 "ollama/llama3.2:3b"）
        llm_type: LLM 類型（"api" 或 "local"）
        agent_name: Agent 名稱（用於日誌記錄）
    
    Returns:
        LLM 實例或模型名稱字串（如果 CrewAI 支援）
    """
    if llm_type == "local":
        # Local model (Ollama)
        if model_name.startswith("ollama/"):
            model_name = model_name.replace("ollama/", "")
        try:
            from langchain_community.llms import Ollama
            # 檢查 Ollama 服務是否可用
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code != 200:
                    raise ConnectionError("Ollama 服務不可用")
            except:
                raise ConnectionError("Ollama 服務不可用")
            
            return Ollama(
                model=model_name,
                base_url="http://localhost:11434",
                temperature=0.7,
            )
        except (ImportError, ConnectionError) as e:
            # 如果無法使用 Ollama，不應該返回字串，而是拋出錯誤
            # 因為這應該在 create_kano_crew_advanced 中已經處理了
            raise ValueError(
                f"無法使用 Local model ({model_name})：{str(e)}\n"
                "請確保 Ollama 已安裝並運行，或將配置改為使用 API model。"
            )
    
    elif llm_type == "api":
        # API model
        if model_name.startswith("gemini/"):
            # Google Gemini
            model = model_name.replace("gemini/", "")
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                google_api_key = os.getenv("GOOGLE_API_KEY")
                if not google_api_key:
                    raise ValueError("未設定 GOOGLE_API_KEY")
                llm_instance = ChatGoogleGenerativeAI(
                    model=model,
                    google_api_key=google_api_key,
                    temperature=0.7,
                )
                # 記錄 API 實例創建（實際調用會在任務執行時發生）
                api_logger.log_call(
                    agent_name=agent_name,
                    model=model_name,
                    llm_type=llm_type,
                    status="initialized",
                    duration=0,
                )
                return llm_instance
            except ImportError:
                logger.warning(f"無法導入 ChatGoogleGenerativeAI，使用字串格式: {model_name}")
                # 嘗試使用 CrewAI 支援的格式
                return model  # 移除 "gemini/" 前綴，使用 "gemini-2.0-flash"
        
        elif model_name.startswith("gpt-") or model_name.startswith("openai/"):
            # OpenAI
            model = model_name.replace("openai/", "")
            try:
                from langchain_openai import ChatOpenAI
                openai_api_key = os.getenv("OPENAI_API_KEY")
                if not openai_api_key:
                    raise ValueError("未設定 OPENAI_API_KEY")
                llm_instance = ChatOpenAI(
                    model=model,
                    openai_api_key=openai_api_key,
                    temperature=0.7,
                )
                # 記錄 API 實例創建
                api_logger.log_call(
                    agent_name=agent_name,
                    model=model_name,
                    llm_type=llm_type,
                    status="initialized",
                    duration=0,
                )
                return llm_instance
            except ImportError:
                logger.warning(f"無法導入 ChatOpenAI，使用字串格式: {model_name}")
                return model_name
        
        elif model_name.startswith("deepseek/") or model_name.startswith("deepseek-"):
            # DeepSeek API（與 OpenAI API 兼容）
            # 重要：只移除 "deepseek/" 前綴，保留完整的模型名稱（如 "deepseek-chat"）
            if model_name.startswith("deepseek/"):
                model = model_name.replace("deepseek/", "")  # deepseek/deepseek-chat -> deepseek-chat
            else:
                model = model_name  # deepseek-chat -> deepseek-chat（保持原樣）
            try:
                # 重要：根據測試，CrewAI 的 OpenAICompletion 支持 base_url 參數
                # 但不會從環境變數讀取，所以我們直接使用 OpenAICompletion
                from crewai.llms.providers.openai.completion import OpenAICompletion
                deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
                if not deepseek_api_key:
                    raise ValueError("未設定 DEEPSEEK_API_KEY")
                
                # 直接創建 OpenAICompletion 實例，明確設置 base_url
                # 這樣可以確保 CrewAI 使用正確的 DeepSeek 端點
                llm_instance = OpenAICompletion(
                    model=model,
                    api_key=deepseek_api_key,
                    base_url="https://api.deepseek.com/v1",  # DeepSeek API endpoint
                    temperature=0.7,
                )
                
                # 驗證實例配置
                try:
                    params = llm_instance._get_client_params()
                    logger.info(f"✓ DeepSeek LLM 實例已創建: model={model}")
                    logger.info(f"  Client params: base_url={params.get('base_url', 'N/A')}, api_key={params.get('api_key', '')[:20] if params.get('api_key') else 'N/A'}...")
                    
                    # 檢查實際的 client
                    if hasattr(llm_instance, 'client'):
                        client = llm_instance.client
                        if hasattr(client, 'base_url'):
                            actual_url = str(client.base_url)
                            logger.info(f"  Client base_url: {actual_url}")
                            if "api.deepseek.com" not in actual_url:
                                logger.error(f"✗ 錯誤：client.base_url 不是 DeepSeek 端點！實際值: {actual_url}")
                        
                        # 檢查模型名稱
                        if hasattr(llm_instance, 'model'):
                            logger.info(f"  LLM model 屬性: {llm_instance.model}")
                except Exception as e:
                    logger.warning(f"⚠ 無法驗證 client 配置: {e}")
                
                # 記錄 API 實例創建
                api_logger.log_call(
                    agent_name=agent_name,
                    model=model_name,
                    llm_type=llm_type,
                    status="initialized",
                    duration=0,
                )
                return llm_instance
            except ImportError:
                # 如果無法導入 OpenAICompletion，回退到 ChatOpenAI
                try:
                    from langchain_openai import ChatOpenAI
                    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
                    if not deepseek_api_key:
                        raise ValueError("未設定 DEEPSEEK_API_KEY")
                    
                    # 設置環境變數（以防萬一）
                    os.environ["OPENAI_API_BASE"] = "https://api.deepseek.com/v1"
                    os.environ["OPENAI_API_KEY"] = deepseek_api_key
                    
                    llm_instance = ChatOpenAI(
                        model=model,
                        openai_api_key=deepseek_api_key,
                        base_url="https://api.deepseek.com/v1",
                        temperature=0.7,
                    )
                    
                    api_logger.log_call(
                        agent_name=agent_name,
                        model=model_name,
                        llm_type=llm_type,
                        status="initialized",
                        duration=0,
                    )
                    return llm_instance
                except ImportError:
                    logger.warning(f"無法導入 ChatOpenAI（用於 DeepSeek），使用字串格式: {model_name}")
                    return model_name
    
    # 預設返回原始模型名稱（讓 CrewAI 自行處理）
    return model_name

def create_kano_crew_advanced():
    """創建通用型軟體開發團隊 - 進階配置"""
    
    # 檢查必要的 API Key
    google_api_key = os.getenv("GOOGLE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    ollama_available = check_ollama_available()
    
    # 檢查哪些角色需要使用 DeepSeek API
    roles_using_deepseek = []
    for role_key in ["pre_sales_consultant", "product_manager", "designer", "architect", "developer"]:
        config = get_llm_config(role_key)
        if config["type"] == "api" and config["api_model"].startswith("deepseek/"):
            roles_using_deepseek.append(role_key)
    
    # 設置環境變數
    if google_api_key:
        os.environ["GOOGLE_API_KEY"] = google_api_key
    
    # 如果有角色使用 DeepSeek API，強制設置 DeepSeek 相關環境變數
    if roles_using_deepseek and deepseek_api_key:
        # 重要：必須在創建 LLM 實例之前設置環境變數
        # 強制覆蓋任何現有的 OPENAI_API_KEY 和 OPENAI_API_BASE
        os.environ["OPENAI_API_BASE"] = "https://api.deepseek.com/v1"
        os.environ["OPENAI_API_KEY"] = deepseek_api_key
        os.environ["DEEPSEEK_API_KEY"] = deepseek_api_key
        logger.info(f"✓ 檢測到使用 DeepSeek API 的角色: {', '.join(roles_using_deepseek)}")
        logger.info(f"✓ 已設置 OPENAI_API_BASE = https://api.deepseek.com/v1")
        logger.info(f"✓ 已設置 OPENAI_API_KEY = DEEPSEEK_API_KEY")
        # 驗證環境變數設置
        actual_base = os.getenv("OPENAI_API_BASE")
        actual_key_prefix = os.getenv("OPENAI_API_KEY", "")[:15] + "..." if len(os.getenv("OPENAI_API_KEY", "")) > 15 else os.getenv("OPENAI_API_KEY", "")
        logger.info(f"✓ 驗證: OPENAI_API_BASE = {actual_base}")
        logger.info(f"✓ 驗證: OPENAI_API_KEY = {actual_key_prefix}")
    else:
        # 如果沒有使用 DeepSeek，則使用原本的設置
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
        if deepseek_api_key:
            os.environ["DEEPSEEK_API_KEY"] = deepseek_api_key
    
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
            if not google_api_key and not openai_api_key and not deepseek_api_key:
                raise ValueError(
                    f"{role_name} 配置為使用 API model，但未設定 API Key。\n"
                    "請在 .env 中設定 GOOGLE_API_KEY、OPENAI_API_KEY 或 DEEPSEEK_API_KEY"
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
    
    # 重要：在創建 LLM 實例之前，確保環境變數已設置（特別是 DeepSeek）
    # CrewAI 的 OpenAICompletion 會在創建時讀取環境變數
    if roles_using_deepseek and deepseek_api_key:
        # 再次確保環境變數已設置（以防在創建實例時被覆蓋）
        os.environ["OPENAI_API_BASE"] = "https://api.deepseek.com/v1"
        os.environ["OPENAI_API_KEY"] = deepseek_api_key
        logger.info("✓ 在創建 LLM 實例前，已確保環境變數設置正確")
    
    # 為每個 Agent 創建 LLM 實例（記錄 Agent 名稱用於日誌）
    pre_sales_llm = create_llm_instance(pre_sales_config["model"], pre_sales_config["type"], "pre_sales_consultant")
    product_manager_llm = create_llm_instance(llm_configs["product_manager"]["model"], llm_configs["product_manager"]["type"], "product_manager")
    designer_llm = create_llm_instance(llm_configs["designer"]["model"], llm_configs["designer"]["type"], "designer")
    architect_llm = create_llm_instance(llm_configs["architect"]["model"], llm_configs["architect"]["type"], "architect")
    developer_llm = create_llm_instance(llm_configs["developer"]["model"], llm_configs["developer"]["type"], "developer")
    reviewer_llm = create_llm_instance(llm_configs["reviewer"]["model"], llm_configs["reviewer"]["type"], "reviewer")
    technical_llm = create_llm_instance(llm_configs["technical"]["model"], llm_configs["technical"]["type"], "technical")
    
    # 重要：在創建 Agent 之前，再次確保環境變數已設置
    # 因為 CrewAI 的 OpenAICompletion 會在 Agent 創建時重新讀取環境變數
    if roles_using_deepseek and deepseek_api_key:
        os.environ["OPENAI_API_BASE"] = "https://api.deepseek.com/v1"
        os.environ["OPENAI_API_KEY"] = deepseek_api_key
        logger.info("✓ 在創建 Agent 前，已確保環境變數設置正確")
    
    pre_sales_consultant = SeniorPreSalesConsultantAgent(pre_sales_llm)
    product_manager = ProductManagerAgent(product_manager_llm)
    designer = DesignerAgent(designer_llm)
    architect = ArchitectAgent(architect_llm)
    developer = DeveloperAgent(developer_llm)
    reviewer = ReviewerAgent(reviewer_llm)
    technical = TechnicalAgent(technical_llm)
    
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
    
    # 顯示 API 調用統計（執行前）
    logger.info("API 日誌記錄器已初始化，將記錄所有 API 調用")
    logger.info(f"日誌檔案：{api_logger.log_file}")
    
    return crew

if __name__ == "__main__":
    crew = create_kano_crew_advanced()
    result = crew.kickoff()
    print("\n" + "="*50)
    print("專案完成！")
    print("="*50)
    print(result)
