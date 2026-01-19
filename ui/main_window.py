"""
KanoAgent 主視窗 GUI
提供模型配置、執行監控和狀態顯示
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import queue
from typing import Dict, Optional, Callable
from datetime import datetime
import os
import sys

# 添加父目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_llm_config, get_all_roles
from utils.logger_config import get_logger

logger = get_logger()

class MainWindow:
    """主視窗類"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("KanoAgent - 通用型軟體開發團隊")
        self.root.geometry("1200x800")
        
        # 執行狀態
        self.is_running = False
        self.current_agent = None
        self.current_task = None
        self.task_progress = 0
        self.total_tasks = 7
        
        # 配置數據
        self.config_data = {}
        self.load_config()
        
        # 用戶需求
        self.user_requirements_text = None
        
        # 創建界面
        self.create_widgets()
        
        # 消息隊列（用於線程間通信）
        self.message_queue = queue.Queue()
        self.check_queue()
        
    def load_config(self):
        """載入當前配置"""
        roles = get_all_roles()
        for role_key in roles:
            config = get_llm_config(role_key)
            self.config_data[role_key] = {
                "type": config["type"],
                "api_model": config["api_model"],
                "local_model": config["local_model"],
            }
    
    def create_widgets(self):
        """創建界面組件"""
        # 創建 Notebook（標籤頁）
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 標籤頁1: 模型配置（默認顯示）
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="模型配置（請先確認）", padding=10)
        self.create_config_tab()
        
        # 標籤頁2: 需求收集
        self.requirements_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.requirements_frame, text="需求收集（可選）")
        self.create_requirements_tab()
        
        # 標籤頁3: 執行監控
        self.monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.monitor_frame, text="執行監控")
        self.create_monitor_tab()
        
        # 狀態欄
        self.create_status_bar()
        
        # 按鈕欄
        self.create_button_bar()
        
        # 默認顯示配置頁面
        self.notebook.select(0)
    
    def create_config_tab(self):
        """創建模型配置標籤頁"""
        # 檢查 Ollama 可用性
        from crew_advanced import check_ollama_available
        ollama_available = check_ollama_available()
        
        # 顯示 Ollama 狀態
        status_frame = ttk.LabelFrame(self.config_frame, text="Ollama 狀態")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        if ollama_available:
            status_label = ttk.Label(status_frame, text="✓ Ollama 可用，可以使用 Local Model", foreground="green")
        else:
            status_label = ttk.Label(
                status_frame, 
                text="⚠ Ollama 不可用，配置為 Local Model 的角色將自動切換為 API Model", 
                foreground="orange"
            )
        status_label.pack(padx=10, pady=5)
        
        if not ollama_available:
            help_label = ttk.Label(
                status_frame,
                text="提示：要使用 Local Model，請先安裝並啟動 Ollama（https://ollama.ai/download）",
                foreground="gray",
                font=("Arial", 8)
            )
            help_label.pack(padx=10, pady=2)
        
        # 創建滾動框架
        canvas = tk.Canvas(self.config_frame)
        scrollbar = ttk.Scrollbar(self.config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 配置表格
        headers = ["Role", "類型", "API 模型", "Local 模型", "狀態"]
        for col, header in enumerate(headers):
            label = ttk.Label(scrollable_frame, text=header, font=("Arial", 10, "bold"))
            label.grid(row=0, column=col, padx=5, pady=5, sticky="w")
        
        # 角色配置
        roles = get_all_roles()
        self.config_vars = {}
        
        for row, role_key in enumerate(roles, 1):
            role_name = roles[role_key]
            config = self.config_data[role_key]
            
            # Role 名稱
            ttk.Label(scrollable_frame, text=role_name).grid(row=row, column=0, padx=5, pady=2)
            
            # 類型選擇
            type_var = tk.StringVar(value=config["type"])
            type_combo = ttk.Combobox(scrollable_frame, textvariable=type_var, 
                                     values=["api", "local"], width=10, state="readonly")
            type_combo.grid(row=row, column=1, padx=5, pady=2)
            
            # 綁定類型變更事件，檢查 Local Model 可用性
            def on_type_change(event=None, rk=role_key, tv=type_var, sl=None):
                if tv.get() == "local" and not ollama_available:
                    if sl:
                        sl.config(text="⚠ 將切換為 API", foreground="orange")
                    messagebox.showwarning(
                        "Ollama 不可用",
                        f"{roles[rk]} 配置為 Local Model，但 Ollama 不可用。\n"
                        "系統將自動切換為 API Model。\n\n"
                        "要使用 Local Model，請先安裝並啟動 Ollama。"
                    )
                elif sl:
                    sl.config(text="✓ 正常", foreground="green")
            
            # API 模型
            api_var = tk.StringVar(value=config["api_model"])
            api_entry = ttk.Entry(scrollable_frame, textvariable=api_var, width=30)
            api_entry.grid(row=row, column=2, padx=5, pady=2)
            
            # Local 模型
            local_var = tk.StringVar(value=config["local_model"])
            local_entry = ttk.Entry(scrollable_frame, textvariable=local_var, width=30)
            local_entry.grid(row=row, column=3, padx=5, pady=2)
            
            # 狀態標籤
            if config["type"] == "local" and not ollama_available:
                status_text = "⚠ 將切換為 API"
                status_color = "orange"
            else:
                status_text = "✓ 正常"
                status_color = "green"
            
            status_label = ttk.Label(scrollable_frame, text=status_text, foreground=status_color)
            status_label.grid(row=row, column=4, padx=5, pady=2)
            
            # 綁定事件
            type_combo.bind("<<ComboboxSelected>>", lambda e, rk=role_key, tv=type_var, sl=status_label: on_type_change(e, rk, tv, sl))
            
            # 保存變數引用
            self.config_vars[role_key] = {
                "type": type_var,
                "api_model": api_var,
                "local_model": local_var,
                "status_label": status_label,
            }
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_monitor_tab(self):
        """創建執行監控標籤頁"""
        # Role 列表
        roles_frame = ttk.LabelFrame(self.monitor_frame, text="Roles")
        roles_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.roles_tree = ttk.Treeview(roles_frame, columns=("status", "agent", "progress"), show="tree headings")
        self.roles_tree.heading("#0", text="Role")
        self.roles_tree.heading("status", text="狀態")
        self.roles_tree.heading("agent", text="當前 Agent")
        self.roles_tree.heading("progress", text="進度")
        self.roles_tree.column("#0", width=200)
        self.roles_tree.column("status", width=100)
        self.roles_tree.column("agent", width=200)
        self.roles_tree.column("progress", width=100)
        self.roles_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 初始化 Role 列表
        roles = get_all_roles()
        for role_key, role_name in roles.items():
            self.roles_tree.insert("", "end", role_key, text=role_name, 
                                  values=("等待中", "-", "0%"))
        
        # 日誌顯示區域
        log_frame = ttk.LabelFrame(self.monitor_frame, text="執行日誌")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)
    
    def create_status_bar(self):
        """創建狀態欄"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        
        # 狀態標籤
        self.status_label = ttk.Label(self.status_bar, text="就緒", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 進度條
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.status_bar, variable=self.progress_var, 
                                           maximum=100, length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
        
        # 進度標籤
        self.progress_label = ttk.Label(self.status_bar, text="0%")
        self.progress_label.pack(side=tk.RIGHT, padx=5)
    
    def create_button_bar(self):
        """創建按鈕欄"""
        button_frame = ttk.Frame(self.root)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        # 左側按鈕組
        left_frame = ttk.Frame(button_frame)
        left_frame.pack(side=tk.LEFT)
        
        # 保存配置按鈕
        ttk.Button(left_frame, text="保存配置", command=self.save_config).pack(side=tk.LEFT, padx=5)
        
        # 確認配置並開始執行按鈕（主要按鈕）
        self.confirm_and_start_button = ttk.Button(
            left_frame, 
            text="✓ 確認配置並開始執行", 
            command=self.confirm_and_start,
            style="Accent.TButton" if hasattr(ttk.Style(), 'configure') else None
        )
        self.confirm_and_start_button.pack(side=tk.LEFT, padx=5)
        
        # 右側按鈕組
        right_frame = ttk.Frame(button_frame)
        right_frame.pack(side=tk.RIGHT)
        
        # 停止執行按鈕
        self.stop_button = ttk.Button(right_frame, text="停止執行", command=self.stop_execution, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 清空日誌按鈕
        ttk.Button(right_frame, text="清空日誌", command=self.clear_log).pack(side=tk.LEFT, padx=5)
    
    def save_config(self):
        """保存配置到環境變數"""
        try:
            for role_key, vars_dict in self.config_vars.items():
                # 設置環境變數
                os.environ[f"{role_key.upper()}_LLM_TYPE"] = vars_dict["type"].get()
                os.environ[f"{role_key.upper()}_API_MODEL"] = vars_dict["api_model"].get()
                os.environ[f"{role_key.upper()}_LOCAL_MODEL"] = vars_dict["local_model"].get()
            
            messagebox.showinfo("成功", "配置已保存到環境變數！\n\n注意：此配置僅在本次運行中有效。\n如需永久保存，請編輯 .env 文件。")
            logger.info("用戶保存了模型配置")
        except Exception as e:
            messagebox.showerror("錯誤", f"保存配置失敗：{e}")
            logger.error(f"保存配置失敗：{e}")
    
    def confirm_and_start(self):
        """確認配置並開始執行"""
        # 先保存配置
        self.save_config()
        
        # 顯示配置摘要
        config_summary = "當前配置摘要：\n\n"
        roles = get_all_roles()
        for role_key, vars_dict in self.config_vars.items():
            role_name = roles.get(role_key, role_key)
            llm_type = vars_dict["type"].get()
            if llm_type == "api":
                model = vars_dict["api_model"].get()
            else:
                model = vars_dict["local_model"].get()
            config_summary += f"  • {role_name}: {llm_type} - {model}\n"
        
        config_summary += "\n是否確認並開始執行？"
        
        # 確認對話框
        result = messagebox.askyesno(
            "確認配置",
            config_summary,
            icon="question"
        )
        
        if result:
            # 切換到監控標籤頁
            self.notebook.select(2)
            # 開始執行
            self.start_execution()
    
    def start_execution(self):
        """開始執行"""
        if self.is_running:
            messagebox.showwarning("警告", "執行已在進行中")
            return
        
        # 確保按鈕狀態正確
        if self.confirm_and_start_button['state'] == tk.DISABLED:
            # 如果按鈕被禁用，先恢復
            self.confirm_and_start_button.config(state=tk.NORMAL)
            self.is_running = False
        
        # 更新狀態
        self.is_running = True
        self.confirm_and_start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.update_status("執行中...")
        self.update_progress(0)
        
        # 在新線程中執行
        thread = threading.Thread(target=self.run_kano_agent, daemon=True)
        thread.start()
        
        logger.info("開始執行 KanoAgent")
    
    def stop_execution(self):
        """停止執行"""
        if not self.is_running:
            return
        
        # 確認停止
        if not messagebox.askyesno("確認停止", "確定要停止執行嗎？"):
            return
        
        self.is_running = False
        self.confirm_and_start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.update_status("已停止")
        logger.info("用戶停止執行")
        
        # 注意：由於執行在後台線程中，無法立即停止
        # 只能設置標誌，實際停止需要等待當前任務完成
        self.add_log("用戶請求停止執行（將在當前任務完成後停止）", "WARNING")
    
    def create_requirements_tab(self):
        """創建需求收集標籤頁"""
        info_frame = ttk.LabelFrame(self.requirements_frame, text="說明")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(
            info_frame, 
            text="您可以通過此界面快速收集用戶需求，或直接開始執行讓 Agent 自動收集。",
            wraplength=800
        ).pack(padx=10, pady=5)
        
        # 需求收集按鈕
        button_frame = ttk.Frame(self.requirements_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            button_frame, 
            text="打開需求收集界面", 
            command=self.open_requirements_ui
        ).pack(side=tk.LEFT, padx=5)
        
        # 顯示已收集的需求
        self.requirements_text = scrolledtext.ScrolledText(
            self.requirements_frame, 
            height=20, 
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.requirements_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def open_requirements_ui(self):
        """打開需求收集界面"""
        from ui.requirements_ui import RequirementsUI
        req_ui = RequirementsUI(self.root)
        result = req_ui.show()
        
        if result:
            # 顯示收集到的需求
            self.requirements_text.config(state=tk.NORMAL)
            self.requirements_text.delete(1.0, tk.END)
            self.requirements_text.insert(1.0, result)
            self.requirements_text.config(state=tk.DISABLED)
            
            # 保存到變數供執行時使用
            self.user_requirements_text = result
            logger.info("用戶通過 UI 收集了需求")
            
            # 更新狀態標籤
            self.requirements_status_label.config(
                text="✓ 需求已收集",
                foreground="green"
            )
            
            # 詢問用戶是否立即開始執行
            response = messagebox.askyesno(
                "需求收集完成",
                "需求已收集並保存！\n\n是否立即開始執行？\n\n"
                "選擇「是」：將切換到配置頁面，確認配置後開始執行\n"
                "選擇「否」：稍後手動點擊「確認配置並開始執行」按鈕",
                icon="question"
            )
            
            if response:
                # 切換到配置標籤頁
                self.notebook.select(0)
                # 高亮提示用戶點擊確認按鈕
                messagebox.showinfo(
                    "準備執行",
                    "請確認模型配置，然後點擊「✓ 確認配置並開始執行」按鈕開始執行。\n\n"
                    "提示：如果配置已正確，可以直接點擊確認按鈕。"
                )
            else:
                messagebox.showinfo(
                    "需求已保存",
                    "需求已保存！\n\n"
                    "下一步：\n"
                    "1. 切換到「模型配置」標籤頁確認配置\n"
                    "2. 點擊「✓ 確認配置並開始執行」按鈕開始執行"
                )
        else:
            self.user_requirements_text = None
            self.requirements_status_label.config(
                text="尚未收集需求",
                foreground="gray"
            )
    
    def run_kano_agent(self):
        """在後台線程中運行 KanoAgent"""
        try:
            # 導入主程式
            from crew_advanced import create_kano_crew_advanced
            from utils.output_saver import extract_and_save_task_outputs
            import os
            
            # 使用收集到的需求
            user_requirements = self.user_requirements_text
            
            # 創建並執行 Crew
            self.message_queue.put(("log", "正在創建 Crew...", "INFO"))
            crew = create_kano_crew_advanced(user_requirements_text=user_requirements)
            
            # 執行任務
            self.message_queue.put(("log", "開始執行任務...", "INFO"))
            result = crew.kickoff()
            
            # 保存結果
            os.makedirs("output", exist_ok=True)
            with open("output/result.txt", "w", encoding="utf-8") as f:
                f.write(str(result))
            
            # 保存各任務輸出
            extract_and_save_task_outputs(result, crew=crew, output_dir="output")
            
            self.message_queue.put(("log", "執行完成！", "INFO"))
            logger.info("執行完成")
            
        except KeyboardInterrupt:
            # 用戶中斷
            self.message_queue.put(("log", "執行被用戶中斷", "WARNING"))
            logger.warning("執行被用戶中斷")
            self.message_queue.put(("error", "執行被用戶中斷"))
        except Exception as e:
            error_msg = str(e)
            error_type = self._classify_error(error_msg)
            self.message_queue.put(("error", error_msg, error_type))
            logger.error(f"執行錯誤：{error_msg}", exc_info=True)
        finally:
            # 無論成功或失敗，都要恢復按鈕狀態
            self.message_queue.put(("finished", None))
    
    def _classify_error(self, error_msg: str) -> str:
        """分類錯誤類型"""
        error_lower = error_msg.lower()
        
        # 配額用盡錯誤
        if "429" in error_msg and ("quota exceeded" in error_lower or "resource_exhausted" in error_lower):
            return "quota_exceeded"
        
        # API 過載錯誤
        if "503" in error_msg or ("429" in error_msg and "rate limit" in error_lower):
            return "api_overload"
        
        # 模型不存在
        if "404" in error_msg or "not_found" in error_lower:
            return "model_not_found"
        
        # 認證錯誤
        if "401" in error_msg or "unauthorized" in error_lower or "invalid api key" in error_lower:
            return "auth_error"
        
        # 網絡錯誤
        if "connection" in error_lower or "timeout" in error_lower or "network" in error_lower:
            return "network_error"
        
        return "unknown"
    
    def on_agent_start(self, agent_name: str, role_key: str):
        """Agent 開始執行回調"""
        self.message_queue.put(("agent_start", (agent_name, role_key)))
    
    def on_agent_end(self, agent_name: str, role_key: str):
        """Agent 結束執行回調"""
        self.message_queue.put(("agent_end", (agent_name, role_key)))
    
    def on_task_start(self, task_name: str, task_num: int, total: int):
        """任務開始回調"""
        self.message_queue.put(("task_start", (task_name, task_num, total)))
    
    def on_task_end(self, task_name: str, task_num: int, total: int):
        """任務結束回調"""
        self.message_queue.put(("task_end", (task_name, task_num, total)))
    
    def on_log(self, message: str, level: str = "INFO"):
        """日誌回調"""
        self.message_queue.put(("log", (message, level)))
    
    def on_error(self, error: str):
        """錯誤回調"""
        self.message_queue.put(("error", error))
    
    def check_queue(self):
        """檢查消息隊列並更新界面"""
        try:
            while True:
                msg_type, data = self.message_queue.get_nowait()
                
                if msg_type == "agent_start":
                    agent_name, role_key = data
                    self.update_role_status(role_key, "執行中", agent_name)
                    self.add_log(f"Agent 開始：{agent_name} ({role_key})", "INFO")
                
                elif msg_type == "agent_end":
                    agent_name, role_key = data
                    self.update_role_status(role_key, "完成", agent_name)
                    self.add_log(f"Agent 完成：{agent_name} ({role_key})", "INFO")
                
                elif msg_type == "task_start":
                    task_name, task_num, total = data
                    self.current_task = task_name
                    self.task_progress = int((task_num - 1) / total * 100)
                    self.update_progress(self.task_progress)
                    self.add_log(f"任務開始：{task_name} ({task_num}/{total})", "INFO")
                
                elif msg_type == "task_end":
                    task_name, task_num, total = data
                    self.task_progress = int(task_num / total * 100)
                    self.update_progress(self.task_progress)
                    self.add_log(f"任務完成：{task_name} ({task_num}/{total})", "INFO")
                
                elif msg_type == "log":
                    message, level = data
                    self.add_log(message, level)
                
                elif msg_type == "error":
                    if isinstance(data, tuple):
                        error_msg, error_type = data
                    else:
                        error_msg = data
                        error_type = "unknown"
                    
                    self.add_log(f"錯誤：{error_msg[:200]}...", "ERROR")
                    self.has_error = True
                    
                    # 根據錯誤類型提供解決方案
                    if error_type == "quota_exceeded":
                        self.add_log("💡 解決方案：切換到 Local Model 或使用其他 API", "INFO")
                    elif error_type == "api_overload":
                        self.add_log("💡 解決方案：等待後重試或切換到 Local Model", "INFO")
                    elif error_type == "model_not_found":
                        self.add_log("💡 解決方案：檢查模型名稱是否正確", "INFO")
                    elif error_type == "auth_error":
                        self.add_log("💡 解決方案：檢查 API Key 是否正確", "INFO")
                
                elif msg_type == "finished":
                    self.is_running = False
                    # 無論如何都要恢復按鈕狀態
                    self.confirm_and_start_button.config(state=tk.NORMAL)
                    self.stop_button.config(state=tk.DISABLED)
                    
                    # 根據是否有錯誤顯示不同的消息
                    if self.has_error:
                        self.update_status("執行失敗")
                        # 獲取最後的錯誤消息
                        last_error = None
                        for msg in list(self.message_queue.queue):
                            if isinstance(msg, tuple) and msg[0] == "error":
                                if isinstance(msg[1], tuple):
                                    last_error = msg[1][0]
                                else:
                                    last_error = msg[1]
                        
                        error_solution = self._get_error_solution(last_error)
                        messagebox.showerror(
                            "執行失敗",
                            f"執行過程中發生錯誤。\n\n"
                            f"錯誤詳情：{last_error[:200] if last_error else '未知錯誤'}...\n\n"
                            f"{error_solution}\n\n"
                            f"請查看日誌了解完整詳情。"
                        )
                        self.has_error = False  # 重置錯誤標記
                    else:
                        self.update_status("執行完成")
                        self.update_progress(100)
                        messagebox.showinfo("完成", "執行已完成！\n\n結果已保存至 output/ 目錄")
    
    def _get_error_solution(self, error_msg: str) -> str:
        """根據錯誤消息返回解決方案"""
        if not error_msg:
            return "請檢查日誌文件了解詳情。"
        
        error_lower = error_msg.lower()
        
        # 配額用盡
        if "429" in error_msg and ("quota exceeded" in error_lower or "resource_exhausted" in error_lower):
            return (
                "💡 解決方案：\n"
                "1. 切換到 Local Model（推薦）：\n"
                "   - 安裝 Ollama：https://ollama.ai/download\n"
                "   - 在配置界面將類型改為 'local'\n"
                "2. 切換到其他 API（如 DeepSeek）\n"
                "3. 等待配額重置或升級付費計劃"
            )
        
        # API 過載
        if "503" in error_msg or ("429" in error_msg and "rate limit" in error_lower):
            return (
                "💡 解決方案：\n"
                "1. 等待 5-10 分鐘後重試\n"
                "2. 切換到 Local Model\n"
                "3. 增加重試配置"
            )
        
        # 模型不存在
        if "404" in error_msg or "not_found" in error_lower:
            return (
                "💡 解決方案：\n"
                "1. 檢查模型名稱是否正確\n"
                "2. 確認 API Key 有權限使用該模型\n"
                "3. 嘗試使用其他模型"
            )
        
        # 認證錯誤
        if "401" in error_msg or "unauthorized" in error_lower or "invalid api key" in error_lower:
            return (
                "💡 解決方案：\n"
                "1. 檢查 API Key 是否正確\n"
                "2. 確認 API Key 是否已啟用\n"
                "3. 檢查 .env 文件中的配置"
            )
        
        return "請查看日誌文件了解詳情，或聯繫技術支援。"
                
        except queue.Empty:
            pass
        
        # 每100ms檢查一次
        self.root.after(100, self.check_queue)
    
    def update_role_status(self, role_key: str, status: str, agent: str):
        """更新 Role 狀態"""
        item = self.roles_tree.item(role_key)
        if item:
            self.roles_tree.item(role_key, values=(status, agent, f"{self.task_progress}%"))
    
    def update_status(self, status: str):
        """更新狀態欄"""
        self.status_label.config(text=f"狀態：{status}")
    
    def update_progress(self, progress: int):
        """更新進度條"""
        self.progress_var.set(progress)
        self.progress_label.config(text=f"{progress}%")
    
    def add_log(self, message: str, level: str = "INFO"):
        """添加日誌"""
        self.log_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] [{level}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def clear_log(self):
        """清空日誌"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def on_closing(self):
        """窗口關閉時的處理"""
        if self.is_running:
            if messagebox.askyesno("確認退出", "執行正在進行中，確定要退出嗎？"):
                self.is_running = False
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    """啟動 GUI 應用"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
