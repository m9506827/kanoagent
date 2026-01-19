"""
用戶交互模組
提供命令行界面讓客戶回答售前顧問的問題
"""
import sys
from typing import Dict, List, Optional

def print_header(title: str):
    """打印標題"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def print_question(category: str, question_num: int, total: int, question: str):
    """打印問題"""
    print(f"\n[{category}] 問題 {question_num}/{total}")
    print(f"❓ {question}")
    print("-" * 70)

def get_user_input(prompt: str = "請輸入您的回答（直接按 Enter 跳過，輸入 'done' 完成此類別）：") -> Optional[str]:
    """獲取用戶輸入"""
    try:
        answer = input(f"\n{prompt}\n> ").strip()
        if answer.lower() == 'done':
            return None
        return answer if answer else None
    except (EOFError, KeyboardInterrupt):
        print("\n\n⚠️  用戶中斷輸入")
        return None

def collect_user_requirements() -> Dict[str, List[Dict[str, str]]]:
    """
    收集用戶需求
    返回結構化的需求字典
    """
    from config.presales_questions import PRESALES_QUESTION_CATEGORIES
    
    print_header("資深售前顧問 - 需求澄清問卷")
    print("歡迎！我是資深售前顧問，將通過一系列問題來了解您的軟體需求。")
    print("您可以：")
    print("  - 直接輸入答案")
    print("  - 按 Enter 跳過問題")
    print("  - 輸入 'done' 完成當前類別")
    print("  - 按 Ctrl+C 中斷並使用已收集的答案")
    
    user_requirements = {}
    
    for category_key, category_data in PRESALES_QUESTION_CATEGORIES.items():
        category_name = category_data["name"]
        questions = category_data["questions"]
        
        print_header(f"類別：{category_name}")
        print(f"本類別共有 {len(questions)} 個問題。")
        
        category_answers = []
        
        for i, question in enumerate(questions, 1):
            print_question(category_name, i, len(questions), question)
            
            answer = get_user_input()
            
            if answer is None:
                # 用戶選擇跳過或完成
                if i == 1:
                    # 第一個問題就跳過，可能想跳過整個類別
                    skip = input("是否跳過整個類別？(y/n): ").strip().lower()
                    if skip == 'y':
                        print(f"✓ 已跳過類別：{category_name}\n")
                        break
                else:
                    # 後續問題跳過，繼續下一個
                    print("✓ 已跳過此問題\n")
                    continue
            
            category_answers.append({
                "question": question,
                "answer": answer
            })
            print(f"✓ 已記錄：{answer[:50]}{'...' if len(answer) > 50 else ''}\n")
        
        if category_answers:
            user_requirements[category_key] = {
                "category_name": category_name,
                "answers": category_answers
            }
    
    return user_requirements

def format_requirements_for_agent(user_requirements: Dict) -> str:
    """
    將用戶回答格式化為 Agent 可用的文本
    """
    formatted = "# 客戶需求澄清結果\n\n"
    formatted += "以下是客戶對各類問題的回答：\n\n"
    
    for category_key, category_data in user_requirements.items():
        category_name = category_data["category_name"]
        answers = category_data["answers"]
        
        formatted += f"## {category_name}\n\n"
        
        for answer_data in answers:
            formatted += f"**問題：** {answer_data['question']}\n"
            formatted += f"**回答：** {answer_data['answer']}\n\n"
        
        formatted += "\n"
    
    return formatted

def save_requirements_to_file(user_requirements: Dict, filename: str = "output/user_requirements.md"):
    """保存用戶需求到文件"""
    import os
    os.makedirs("output", exist_ok=True)
    
    formatted = format_requirements_for_agent(user_requirements)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(formatted)
    
    return filename

def interactive_requirements_collection() -> str:
    """
    交互式收集用戶需求
    返回格式化後的需求文本（供 Agent 使用）
    """
    try:
        user_requirements = collect_user_requirements()
        
        if not user_requirements:
            print("\n⚠️  未收集到任何需求信息")
            return ""
        
        # 保存到文件
        filename = save_requirements_to_file(user_requirements)
        print(f"\n✓ 需求已保存至：{filename}")
        
        # 格式化供 Agent 使用
        formatted = format_requirements_for_agent(user_requirements)
        
        print_header("需求收集完成")
        print("已收集以下類別的需求：")
        for category_key, category_data in user_requirements.items():
            print(f"  ✓ {category_data['category_name']} ({len(category_data['answers'])} 個回答)")
        
        return formatted
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用戶中斷需求收集")
        return ""
    except Exception as e:
        print(f"\n❌ 收集需求時發生錯誤：{e}")
        import traceback
        traceback.print_exc()
        return ""
