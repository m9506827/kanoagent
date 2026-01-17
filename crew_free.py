"""
使用免費 LLM 的 Crew 配置
支援 Ollama (本地免費) 和 Hugging Face (免費額度)
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

def create_plant_diagnosis_crew_free():
    """創建植物診斷系統開發團隊 - 使用免費 LLM"""
    
    # 選項 1: 使用 Ollama (本地免費，需要先安裝 Ollama)
    try:
        from langchain_community.llms import Ollama
        llm = Ollama(
            model="llama3.2",  # 或其他模型如 "mistral", "qwen2.5"
            base_url="http://localhost:11434",  # Ollama 預設地址
        )
        print("使用 Ollama 本地模型")
    except ImportError:
        print("Ollama 未安裝，嘗試其他選項...")
        llm = None
    
    # 選項 2: 使用 Hugging Face (免費額度)
    if llm is None:
        try:
            from langchain_huggingface import HuggingFaceEndpoint
            hf_token = os.getenv("HUGGINGFACE_API_KEY")
            if hf_token:
                llm = HuggingFaceEndpoint(
                    repo_id="meta-llama/Llama-3.2-3B-Instruct",
                    huggingface_api_token=hf_token,
                    temperature=0.7,
                )
                print("使用 Hugging Face 模型")
            else:
                raise ValueError("需要設定 HUGGINGFACE_API_KEY")
        except (ImportError, ValueError) as e:
            print(f"Hugging Face 不可用: {e}")
            llm = None
    
    # 選項 3: 使用 Google Gemini (免費 tier)
    if llm is None:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            gemini_key = os.getenv("GOOGLE_API_KEY")
            if gemini_key:
                llm = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=gemini_key,
                    temperature=0.7,
                )
                print("使用 Google Gemini 模型")
            else:
                raise ValueError("需要設定 GOOGLE_API_KEY")
        except (ImportError, ValueError) as e:
            print(f"Google Gemini 不可用: {e}")
            llm = None
    
    # 如果都沒有，使用 OpenAI (需要付費)
    if llm is None:
        from langchain_openai import ChatOpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            raise ValueError(
                "請設定以下其中一個 API Key:\n"
                "1. 安裝 Ollama (https://ollama.ai) 並運行本地模型\n"
                "2. 設定 HUGGINGFACE_API_KEY (免費申請: https://huggingface.co)\n"
                "3. 設定 GOOGLE_API_KEY (免費申請: https://makersuite.google.com/app/apikey)\n"
                "4. 設定 OPENAI_API_KEY (需要付費)"
            )
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",  # 使用較便宜的模型
            temperature=0.7,
            openai_api_key=api_key,
        )
        print("使用 OpenAI 模型")
    
    # 創建所有 Agents
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
        process=Process.sequential,
        verbose=True,
    )
    
    return crew

if __name__ == "__main__":
    crew = create_plant_diagnosis_crew_free()
    result = crew.kickoff()
    print("\n" + "="*50)
    print("專案完成！")
    print("="*50)
    print(result)
