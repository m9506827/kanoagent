"""
需求收集 UI
提供快速勾選界面讓用戶選擇需求
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List
import os
import sys

# 添加父目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.presales_questions import PRESALES_QUESTION_CATEGORIES
from utils.logger_config import get_logger

logger = get_logger()

class RequirementsUI:
    """需求收集界面"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.result = None
        
        # 創建窗口
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            self.window = tk.Tk()
        
        self.window.title("需求收集 - 快速勾選")
        self.window.geometry("900x700")
        
        # 用戶選擇的答案
        self.answers = {}
        
        # 創建界面
        self.create_widgets()
        
        # 居中顯示
        self.window.update_idletasks()
        if parent:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.window.winfo_width() // 2)
            y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.window.winfo_height() // 2)
            self.window.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """創建界面組件"""
        # 說明文字
        info_frame = ttk.Frame(self.window)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(info_frame, text="請勾選符合您需求的项目，或直接輸入自定義答案", 
                 font=("Arial", 10)).pack()
        
        # 創建 Notebook（標籤頁）
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 為每個類別創建標籤頁
        for category_key, category_data in PRESALES_QUESTION_CATEGORIES.items():
            self.create_category_tab(category_key, category_data)
        
        # 按鈕欄
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="確認", command=self.confirm).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.cancel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="全選", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="全不選", command=self.deselect_all).pack(side=tk.LEFT, padx=5)
    
    def create_category_tab(self, category_key: str, category_data: dict):
        """為每個類別創建標籤頁"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=category_data["name"])
        
        # 創建滾動框架
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 問題列表
        self.answers[category_key] = {}
        
        for i, question in enumerate(category_data["questions"]):
            # 問題框架
            q_frame = ttk.LabelFrame(scrollable_frame, text=f"問題 {i+1}")
            q_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # 問題文字
            ttk.Label(q_frame, text=question, wraplength=700).pack(anchor=tk.W, padx=5, pady=2)
            
            # 快速選項（如果有預設選項）
            options_frame = ttk.Frame(q_frame)
            options_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # 常見選項（根據問題類型提供）
            common_options = self.get_common_options(question)
            
            var = tk.StringVar()
            self.answers[category_key][question] = {
                "var": var,
                "options": []
            }
            
            if common_options:
                for option in common_options:
                    rb = ttk.Radiobutton(options_frame, text=option, variable=var, value=option)
                    rb.pack(side=tk.LEFT, padx=5)
                    self.answers[category_key][question]["options"].append(rb)
            
            # 自定義輸入
            custom_frame = ttk.Frame(q_frame)
            custom_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(custom_frame, text="自定義答案：").pack(side=tk.LEFT)
            custom_entry = ttk.Entry(custom_frame, width=50)
            custom_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # 綁定自定義輸入到變數
            custom_entry.bind("<KeyRelease>", lambda e, v=var: v.set(e.widget.get()))
            self.answers[category_key][question]["entry"] = custom_entry
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def get_common_options(self, question: str) -> List[str]:
        """根據問題返回常見選項"""
        question_lower = question.lower()
        
        # 平台選項
        if "平台" in question or "platform" in question_lower:
            return ["Web", "移動端", "桌面應用", "多平台"]
        
        # 用戶數量選項
        if "用戶數量" in question or "用戶數" in question:
            return ["< 100", "100-1000", "1000-10000", "> 10000"]
        
        # 響應時間選項
        if "響應時間" in question or "response" in question_lower:
            return ["< 1秒", "1-3秒", "3-5秒", "> 5秒"]
        
        # 可用性選項
        if "可用性" in question or "availability" in question_lower:
            return ["99%", "99.9%", "99.99%", "99.999%"]
        
        # 預算選項
        if "預算" in question or "budget" in question_lower:
            return ["< 10萬", "10-50萬", "50-100萬", "> 100萬"]
        
        # 時程選項
        if "時程" in question or "timeline" in question_lower:
            return ["< 1個月", "1-3個月", "3-6個月", "> 6個月"]
        
        # 技術棧選項
        if "技術" in question or "technology" in question_lower:
            return ["Python", "Java", "JavaScript/Node.js", "其他"]
        
        # 部署選項
        if "部署" in question or "deploy" in question_lower:
            return ["雲端", "本地", "混合"]
        
        return []
    
    def select_all(self):
        """全選所有快速選項"""
        for category_key in self.answers:
            for question in self.answers[category_key]:
                answer_data = self.answers[category_key][question]
                if answer_data["options"]:
                    answer_data["options"][0].invoke()
    
    def deselect_all(self):
        """全不選"""
        for category_key in self.answers:
            for question in self.answers[category_key]:
                self.answers[category_key][question]["var"].set("")
                self.answers[category_key][question]["entry"].delete(0, tk.END)
    
    def confirm(self):
        """確認並收集答案"""
        collected_requirements = {}
        
        for category_key, category_data in PRESALES_QUESTION_CATEGORIES.items():
            category_answers = []
            
            for question in category_data["questions"]:
                if question in self.answers[category_key]:
                    answer_data = self.answers[category_key][question]
                    answer = answer_data["var"].get() or answer_data["entry"].get()
                    
                    if answer:
                        category_answers.append({
                            "question": question,
                            "answer": answer
                        })
            
            if category_answers:
                collected_requirements[category_key] = {
                    "category_name": category_data["name"],
                    "answers": category_answers
                }
        
        if not collected_requirements:
            messagebox.showwarning("警告", "請至少選擇一個需求項目")
            return
        
        # 格式化為文本
        from utils.user_interaction import format_requirements_for_agent
        self.result = format_requirements_for_agent(collected_requirements)
        
        logger.info(f"用戶通過UI收集了 {len(collected_requirements)} 個類別的需求")
        
        # 顯示收集摘要
        summary = f"已收集 {len(collected_requirements)} 個類別的需求：\n\n"
        for category_key, category_data in collected_requirements.items():
            summary += f"  • {category_data['category_name']} ({len(category_data['answers'])} 個回答)\n"
        
        # 關閉窗口
        self.window.destroy()
    
    def cancel(self):
        """取消"""
        self.result = None
        self.window.destroy()
    
    def show(self) -> str:
        """顯示窗口並返回結果"""
        if not self.parent:
            self.window.mainloop()
        else:
            self.window.wait_window()
        
        return self.result
