"""
任務輸出保存模組
自動保存每個 Agent 任務的輸出到單獨的文件
"""
import os
from typing import Dict, Any
from datetime import datetime

def save_task_output(task_name: str, agent_name: str, output: Any, output_dir: str = "output"):
    """
    保存任務輸出到文件
    
    Args:
        task_name: 任務名稱（用於文件名）
        agent_name: Agent 名稱
        output: 任務輸出內容
        output_dir: 輸出目錄
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名（使用任務名稱，清理特殊字符）
    safe_task_name = task_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    filename = f"{output_dir}/{safe_task_name}.md"
    
    # 添加時間戳和 Agent 信息
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"""# {task_name}

**Agent:** {agent_name}
**生成時間:** {timestamp}

---

"""
    
    # 寫入文件
    with open(filename, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(str(output))
    
    return filename

def save_all_task_outputs(crew_result: Any, output_dir: str = "output"):
    """
    從 Crew 執行結果中提取並保存所有任務輸出
    
    Args:
        crew_result: Crew.kickoff() 的返回結果
        output_dir: 輸出目錄
    """
    saved_files = []
    
    # CrewAI 的結果結構可能不同，需要適配
    # 通常結果包含 tasks 列表，每個 task 有 output
    if hasattr(crew_result, 'tasks'):
        for task in crew_result.tasks:
            if hasattr(task, 'output') and task.output:
                task_name = getattr(task, 'description', 'Unknown Task')[:50]
                agent_name = getattr(task, 'agent', {}).get('role', 'Unknown Agent') if isinstance(getattr(task, 'agent', None), dict) else str(getattr(task, 'agent', 'Unknown Agent'))
                
                filename = save_task_output(
                    task_name=task_name,
                    agent_name=agent_name,
                    output=task.output,
                    output_dir=output_dir
                )
                saved_files.append(filename)
    
    # 如果結果是字符串或字典，嘗試解析
    elif isinstance(crew_result, str):
        # 嘗試從字符串中提取任務信息
        # 這取決於 CrewAI 的實際輸出格式
        filename = save_task_output(
            task_name="Complete_Result",
            agent_name="Crew",
            output=crew_result,
            output_dir=output_dir
        )
        saved_files.append(filename)
    
    return saved_files

def extract_and_save_task_outputs(crew_result: Any, crew: Any = None, output_dir: str = "output") -> Dict[str, str]:
    """
    從 Crew 結果中提取任務輸出並保存
    
    Args:
        crew_result: Crew.kickoff() 的返回結果
        crew: Crew 對象（可選，用於提取任務信息）
        output_dir: 輸出目錄
    
    Returns:
        Dict[str, str]: {task_name: file_path}
    """
    saved_outputs = {}
    
    # 方式 1: 從 crew 對象提取任務輸出（最可靠）
    if crew and hasattr(crew, 'tasks'):
        task_names = [
            "01_需求澄清文檔",
            "02_PRD需求規格書",
            "03_UIUX設計方案",
            "04_系統設計文件",
            "05_程式碼實作",
            "06_代碼評審報告",
            "07_測試報告",
        ]
        
        for i, task in enumerate(crew.tasks):
            if hasattr(task, 'output') and task.output:
                # 獲取 Agent 名稱
                agent_name = "Unknown"
                if hasattr(task, 'agent'):
                    agent = task.agent
                    if hasattr(agent, 'role'):
                        agent_name = agent.role
                    elif isinstance(agent, dict):
                        agent_name = agent.get('role', 'Unknown')
                    else:
                        agent_name = str(agent)
                
                # 使用預定義的任務名稱
                task_name = task_names[i] if i < len(task_names) else f"task_{i}"
                
                filename = save_task_output(
                    task_name=task_name,
                    agent_name=agent_name,
                    output=task.output,
                    output_dir=output_dir
                )
                saved_outputs[task_name] = filename
    
    # 方式 2: 從結果對象提取
    elif hasattr(crew_result, 'tasks'):
        for i, task in enumerate(crew_result.tasks):
            if hasattr(task, 'output') and task.output:
                task_name = f"task_{i}_{getattr(task, 'description', 'unknown')[:30]}"
                filename = save_task_output(
                    task_name=task_name,
                    agent_name=str(getattr(task, 'agent', 'Unknown')),
                    output=task.output,
                    output_dir=output_dir
                )
                saved_outputs[task_name] = filename
    
    # 方式 3: 如果結果是字符串，直接保存
    if not saved_outputs and isinstance(crew_result, str) and crew_result.strip():
        filename = save_task_output(
            task_name="Final_Result",
            agent_name="Crew",
            output=crew_result,
            output_dir=output_dir
        )
        saved_outputs["Final_Result"] = filename
    
    return saved_outputs
