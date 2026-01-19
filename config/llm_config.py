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

# 預設配置：每個 Agent 的 LLM 設定
# 
# ============================================================================
# Role 與 Agent 層級結構
# ============================================================================
# 
# 【Role 層級】（4 個檔案，對應 agents/ 目錄下的檔案）
# 1. product   (agents/product.py)   -> 包含 3 個 Agent
# 2. engineer  (agents/engineer.py)  -> 包含 2 個 Agent
# 3. quality   (agents/quality.py)   -> 包含 1 個 Agent
# 4. technical (agents/technical.py) -> 包含 1 個 Agent
#
# 【Agent 層級】（7 個 Agent 函數，每個都有獨立的配置）
# Role: product
#   - pre_sales_consultant -> SeniorPreSalesConsultantAgent (資深售前顧問)
#   - product_manager       -> ProductManagerAgent (產品經理)
#   - designer              -> DesignerAgent (UI/UX 設計師)
#
# Role: engineer
#   - architect            -> ArchitectAgent (架構工程師)
#   - developer            -> DeveloperAgent (開發工程師)
#
# Role: quality
#   - reviewer             -> ReviewerAgent (代碼評審與測試工程師)
#
# Role: technical
#   - technical            -> TechnicalAgent (技術支援工程師)
#
# 【配置鍵命名規則】
# 配置鍵使用 Agent 函數名稱轉換（PascalCase -> snake_case）：
# - SeniorPreSalesConsultantAgent -> pre_sales_consultant
# - ProductManagerAgent           -> product_manager
# - DesignerAgent                 -> designer
# - ArchitectAgent                -> architect
# - DeveloperAgent                -> developer
# - ReviewerAgent                 -> reviewer
# - TechnicalAgent                -> technical
#
# 【環境變數命名規則】
# 使用配置鍵（大寫）作為前綴：
# - {CONFIG_KEY}_LLM_TYPE        -> 例如: PRE_SALES_CONSULTANT_LLM_TYPE
# - {CONFIG_KEY}_API_MODEL       -> 例如: PRE_SALES_CONSULTANT_API_MODEL
# - {CONFIG_KEY}_LOCAL_MODEL     -> 例如: PRE_SALES_CONSULTANT_LOCAL_MODEL
# - {CONFIG_KEY}_RETRY_TIMES     -> 例如: PRE_SALES_CONSULTANT_RETRY_TIMES
# - {CONFIG_KEY}_RETRY_DELAY     -> 例如: PRE_SALES_CONSULTANT_RETRY_DELAY
# ============================================================================
DEFAULT_LLM_CONFIG: Dict[str, Dict] = {
    "pre_sales_consultant": {
        "type": "api",  # "api" 或 "local"
        "api_model": "deepseek/deepseek-chat",  # DeepSeek API 模型
        "local_model": "ollama/deepseek-coder:33b",  # Local 模型（需要良好的溝通能力）
        "retry_times": 5,  # 重試次數（增加以應對 API 過載）
        "retry_delay": 3,  # 重試延遲（秒）
        "retry_backoff": 1.5,  # 指數退避倍數
        "max_retry_delay": 60,  # 最大重試延遲（秒）
        "auto_fallback": True,  # 自動降級到 local model
    },
    "product_manager": {
        "type": "api",  # "api" 或 "local"
        "api_model": "deepseek/deepseek-chat",  # DeepSeek API 模型
        "local_model": "ollama/deepseek-coder:33b",  # Local 模型
        "retry_times": 5,  # 重試次數（增加以應對 API 過載）
        "retry_delay": 3,  # 重試延遲（秒）
        "retry_backoff": 1.5,  # 指數退避倍數
        "max_retry_delay": 60,  # 最大重試延遲（秒）
        "auto_fallback": True,  # 自動降級到 local model
    },
    "designer": {
        "type": "api",
        "api_model": "deepseek/deepseek-chat",  # DeepSeek API 模型
        "local_model": "ollama/deepseek-coder:33b",
        "retry_times": 5,
        "retry_delay": 3,
        "retry_backoff": 1.5,
        "max_retry_delay": 60,
        "auto_fallback": True,
    },
    "architect": {
        "type": "api",
        "api_model": "deepseek/deepseek-chat",  # DeepSeek API 模型
        "local_model": "ollama/deepseek-coder:33b",
        "retry_times": 5,
        "retry_delay": 3,
        "retry_backoff": 1.5,
        "max_retry_delay": 60,
        "auto_fallback": True,
    },
    "developer": {
        "type": "api",
        "api_model": "deepseek/deepseek-chat",  # DeepSeek API 模型
        "local_model": "ollama/deepseek-coder:33b",
        "retry_times": 5,
        "retry_delay": 3,
        "retry_backoff": 1.5,
        "max_retry_delay": 60,
        "auto_fallback": True,
    },
    "reviewer": {
        "type": "local",  # 使用 local model
        "api_model": "gemini/gemini-2.0-flash",  # 備用 API 模型
        "local_model": "ollama/gemma3:4b",  # 使用 gemma3:4b
        "retry_times": 3,
        "retry_delay": 1,  # 較短的延遲
        "retry_backoff": 1.5,
        "max_retry_delay": 30,
        "auto_fallback": False,  # Local model 不需要降級
    },
    "technical": {
        "type": "local",  # 使用 local model
        "api_model": "gemini/gemini-2.0-flash",  # 備用 API 模型
        "local_model": "ollama/gemma3:4b",  # 使用 gemma3:4b
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

# ============================================================================
# Role 定義驗證
# ============================================================================

# ============================================================================
# Role 與 Agent 映射定義
# ============================================================================

# 定義 4 個 Role（檔案層級）
ALL_ROLES = ["product", "engineer", "quality", "technical"]

# Role 到 Agent 的映射（每個 Role 包含哪些 Agent）
ROLE_TO_AGENTS = {
    "product": [
        "SeniorPreSalesConsultantAgent",
        "ProductManagerAgent",
        "DesignerAgent",
    ],
    "engineer": [
        "ArchitectAgent",
        "DeveloperAgent",
    ],
    "quality": [
        "ReviewerAgent",
    ],
    "technical": [
        "TechnicalAgent",
    ],
}

# 定義所有 Agent 函數名稱（用於驗證）
ALL_AGENT_FUNCTIONS = [
    "SeniorPreSalesConsultantAgent",  # Role: product, 配置鍵: pre_sales_consultant
    "ProductManagerAgent",            # Role: product, 配置鍵: product_manager
    "DesignerAgent",                   # Role: product, 配置鍵: designer
    "ArchitectAgent",                  # Role: engineer, 配置鍵: architect
    "DeveloperAgent",                  # Role: engineer, 配置鍵: developer
    "ReviewerAgent",                   # Role: quality, 配置鍵: reviewer
    "TechnicalAgent",                  # Role: technical, 配置鍵: technical
]

# 定義所有配置鍵（用於驗證）
ALL_CONFIG_KEYS = list(DEFAULT_LLM_CONFIG.keys())

# Agent 函數名稱到配置鍵的映射
AGENT_TO_CONFIG_KEY = {
    "SeniorPreSalesConsultantAgent": "pre_sales_consultant",
    "ProductManagerAgent": "product_manager",
    "DesignerAgent": "designer",
    "ArchitectAgent": "architect",
    "DeveloperAgent": "developer",
    "ReviewerAgent": "reviewer",
    "TechnicalAgent": "technical",
}

# 配置鍵到 Agent 函數名稱的映射
CONFIG_KEY_TO_AGENT = {v: k for k, v in AGENT_TO_CONFIG_KEY.items()}

# Agent 函數名稱到 Role 的映射
AGENT_TO_ROLE = {}
for role, agents in ROLE_TO_AGENTS.items():
    for agent in agents:
        AGENT_TO_ROLE[agent] = role

# Role 到配置鍵的映射（每個 Role 包含哪些配置鍵）
ROLE_TO_CONFIG_KEYS = {}
for role, agents in ROLE_TO_AGENTS.items():
    ROLE_TO_CONFIG_KEYS[role] = [AGENT_TO_CONFIG_KEY[agent] for agent in agents]

def validate_role_mapping():
    """
    驗證 Role 定義與配置的映射關係是否正確
    
    驗證內容：
    1. 4 個 Role 都有定義
    2. 每個 Role 下的 Agent 都有對應的配置
    3. 每個配置鍵都有對應的 Agent
    
    Returns:
        tuple: (is_valid, missing_configs, missing_agents, role_issues)
    """
    missing_configs = []
    missing_agents = []
    role_issues = []
    
    # 檢查每個 Role 下的 Agent 是否有對應的配置
    for role, agents in ROLE_TO_AGENTS.items():
        for agent_name in agents:
            if agent_name not in AGENT_TO_CONFIG_KEY:
                role_issues.append(f"Role '{role}' 的 Agent '{agent_name}' 沒有配置鍵映射")
                missing_agents.append(agent_name)
            else:
                config_key = AGENT_TO_CONFIG_KEY[agent_name]
                if config_key not in DEFAULT_LLM_CONFIG:
                    missing_configs.append((role, agent_name, config_key))
                    role_issues.append(f"Role '{role}' 的 Agent '{agent_name}' (配置鍵: {config_key}) 沒有配置")
    
    # 檢查每個配置鍵是否有對應的 Agent
    for config_key in ALL_CONFIG_KEYS:
        if config_key not in CONFIG_KEY_TO_AGENT:
            missing_agents.append(f"Config key '{config_key}' has no corresponding agent")
            role_issues.append(f"配置鍵 '{config_key}' 沒有對應的 Agent")
    
    # 檢查 Role 數量是否正確（應該是 4 個）
    if len(ALL_ROLES) != 4:
        role_issues.append(f"Role 數量不正確：期望 4 個，實際 {len(ALL_ROLES)} 個")
    
    is_valid = len(missing_configs) == 0 and len(missing_agents) == 0 and len(role_issues) == 0
    
    return is_valid, missing_configs, missing_agents, role_issues

def get_config_key_for_agent(agent_name: str) -> str:
    """
    根據 Agent 函數名稱獲取對應的配置鍵
    
    Args:
        agent_name: Agent 函數名稱（如 "ProductManagerAgent"）
    
    Returns:
        配置鍵（如 "product_manager"）
    
    Raises:
        ValueError: 如果 Agent 名稱不存在
    """
    if agent_name not in AGENT_TO_CONFIG_KEY:
        raise ValueError(
            f"未知的 Agent 名稱: {agent_name}\n"
            f"可用的 Agent: {', '.join(ALL_AGENT_FUNCTIONS)}"
        )
    return AGENT_TO_CONFIG_KEY[agent_name]

def get_agent_name_for_config(config_key: str) -> str:
    """
    根據配置鍵獲取對應的 Agent 函數名稱
    
    Args:
        config_key: 配置鍵（如 "product_manager"）
    
    Returns:
        Agent 函數名稱（如 "ProductManagerAgent"）
    
    Raises:
        ValueError: 如果配置鍵不存在
    """
    if config_key not in CONFIG_KEY_TO_AGENT:
        raise ValueError(
            f"未知的配置鍵: {config_key}\n"
            f"可用的配置鍵: {', '.join(ALL_CONFIG_KEYS)}"
        )
    return CONFIG_KEY_TO_AGENT[config_key]

def get_all_roles() -> Dict[str, str]:
    """
    獲取所有 Role 及其顯示名稱
    
    Returns:
        Dict[str, str]: {role_key: role_display_name}
    """
    role_names = {
        "pre_sales_consultant": "資深售前顧問",
        "product_manager": "產品經理",
        "designer": "UI/UX 設計師",
        "architect": "架構工程師",
        "developer": "開發工程師",
        "reviewer": "代碼評審工程師",
        "technical": "技術支援工程師",
    }
    return role_names
