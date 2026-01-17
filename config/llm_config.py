"""
LLM 配置管理
支援每個 Role 獨立配置使用 API 或 Local Model
"""
import os
from typing import Dict, Literal
from dotenv import load_dotenv

load_dotenv()

# LLM 類型
LLMType = Literal["api", "local"]

# 預設配置：每個 Role 的 LLM 設定
# 
# 檔案結構對應：
# - product.py: ProductManagerAgent, DesignerAgent
# - engineer.py: ArchitectAgent, DeveloperAgent
# - quality.py: ReviewerAgent
# - technical.py: TechnicalAgent
#
# 配置鍵名稱對應 Agent 函數名稱（小寫加底線）：
# - pre_sales_consultant -> SeniorPreSalesConsultantAgent
# - product_manager -> ProductManagerAgent
# - designer -> DesignerAgent
# - architect -> ArchitectAgent
# - developer -> DeveloperAgent
# - reviewer -> ReviewerAgent
# - technical -> TechnicalAgent
DEFAULT_LLM_CONFIG: Dict[str, Dict] = {
    "pre_sales_consultant": {
        "type": "api",  # "api" 或 "local"
        "api_model": "gemini/gemini-2.0-flash",  # API 模型（使用更穩定的 2.0 版本）
        "local_model": "ollama/llama3.3:70b",  # Local 模型（需要良好的溝通能力）
        "retry_times": 5,  # 重試次數（增加以應對 API 過載）
        "retry_delay": 3,  # 重試延遲（秒）
        "retry_backoff": 1.5,  # 指數退避倍數
        "max_retry_delay": 60,  # 最大重試延遲（秒）
        "auto_fallback": True,  # 自動降級到 local model
    },
    "product_manager": {
        "type": "api",  # "api" 或 "local"
        "api_model": "gemini/gemini-2.0-flash",  # API 模型（使用更穩定的 2.0 版本）
        "local_model": "ollama/llama3.3:70b",  # Local 模型
        "retry_times": 5,  # 重試次數（增加以應對 API 過載）
        "retry_delay": 3,  # 重試延遲（秒）
        "retry_backoff": 1.5,  # 指數退避倍數
        "max_retry_delay": 60,  # 最大重試延遲（秒）
        "auto_fallback": True,  # 自動降級到 local model
    },
    "designer": {
        "type": "api",
        "api_model": "gemini/gemini-2.0-flash",  # 使用 gemini-2.0-flash（更穩定）
        "local_model": "ollama/llama3.3:70b",
        "retry_times": 5,
        "retry_delay": 3,
        "retry_backoff": 1.5,
        "max_retry_delay": 60,
        "auto_fallback": True,
    },
    "architect": {
        "type": "api",
        "api_model": "gemini/gemini-2.0-flash",  # 使用 gemini-2.0-flash（更穩定）
        "local_model": "ollama/deepseek-coder:33b",
        "retry_times": 5,
        "retry_delay": 3,
        "retry_backoff": 1.5,
        "max_retry_delay": 60,
        "auto_fallback": True,
    },
    "developer": {
        "type": "api",
        "api_model": "gemini/gemini-2.0-flash",  # 使用 gemini-2.0-flash（更穩定）
        "local_model": "ollama/deepseek-coder:33b",
        "retry_times": 5,
        "retry_delay": 3,
        "retry_backoff": 1.5,
        "max_retry_delay": 60,
        "auto_fallback": True,
    },
    "reviewer": {
        "type": "api",
        "api_model": "gemini/gemini-2.0-flash",  # 使用 gemini-2.0-flash（更穩定）
        "local_model": "ollama/llama3.3:70b",
        "retry_times": 5,
        "retry_delay": 3,
        "retry_backoff": 1.5,
        "max_retry_delay": 60,
        "auto_fallback": True,
    },
    "technical": {
        "type": "local",  # 預設使用 local（速度快）
        "api_model": "gemini/gemini-2.0-flash",  # 使用 gemini-2.0-flash（更穩定）
        "local_model": "ollama/llama3.2:3b",
        "retry_times": 3,
        "retry_delay": 1,  # 較短的延遲
        "retry_backoff": 1.5,
        "max_retry_delay": 30,
        "auto_fallback": False,  # Local model 不需要降級
    },
}

def get_llm_config(role: str) -> Dict:
    """獲取指定 Role 的 LLM 配置"""
    # 從環境變數讀取配置（優先）
    env_key = f"{role.upper()}_LLM_TYPE"
    llm_type = os.getenv(env_key, DEFAULT_LLM_CONFIG[role]["type"])
    
    config = DEFAULT_LLM_CONFIG[role].copy()
    config["type"] = llm_type
    
    # 允許從環境變數覆蓋模型名稱
    if llm_type == "api":
        api_model_key = f"{role.upper()}_API_MODEL"
        if os.getenv(api_model_key):
            config["api_model"] = os.getenv(api_model_key)
    else:
        local_model_key = f"{role.upper()}_LOCAL_MODEL"
        if os.getenv(local_model_key):
            config["local_model"] = os.getenv(local_model_key)
    
    # 允許從環境變數覆蓋重試設定
    retry_key = f"{role.upper()}_RETRY_TIMES"
    if os.getenv(retry_key):
        config["retry_times"] = int(os.getenv(retry_key))
    
    delay_key = f"{role.upper()}_RETRY_DELAY"
    if os.getenv(delay_key):
        config["retry_delay"] = float(os.getenv(delay_key))
    
    backoff_key = f"{role.upper()}_RETRY_BACKOFF"
    if os.getenv(backoff_key):
        config["retry_backoff"] = float(os.getenv(backoff_key))
    elif "retry_backoff" not in config:
        config["retry_backoff"] = 1.5  # 預設值
    
    max_delay_key = f"{role.upper()}_MAX_RETRY_DELAY"
    if os.getenv(max_delay_key):
        config["max_retry_delay"] = float(os.getenv(max_delay_key))
    elif "max_retry_delay" not in config:
        config["max_retry_delay"] = 60.0  # 預設值
    
    fallback_key = f"{role.upper()}_AUTO_FALLBACK"
    if os.getenv(fallback_key):
        config["auto_fallback"] = os.getenv(fallback_key).lower() == "true"
    elif "auto_fallback" not in config:
        config["auto_fallback"] = True  # 預設啟用自動降級
    
    return config

def get_llm_for_role(role: str) -> str:
    """獲取指定 Role 的 LLM 模型名稱"""
    config = get_llm_config(role)
    if config["type"] == "api":
        return config["api_model"]
    else:
        return config["local_model"]

def get_retry_config(role: str) -> Dict:
    """獲取指定 Role 的重試配置"""
    config = get_llm_config(role)
    return {
        "retry_times": config["retry_times"],
        "retry_delay": config["retry_delay"],
    }
