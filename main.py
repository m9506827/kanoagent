"""
KanoAgent - 通用型軟體開發團隊主程式
使用 CrewAI 實作的智能開發團隊
支援每個 Role 獨立配置 API/Local Model，並包含重試機制
"""
import os
import sys
from dotenv import load_dotenv
from crew_advanced import create_kano_crew_advanced
from utils.api_logger import get_api_logger
from utils.logger_config import setup_logger
import logging

# 設置統一日誌系統
logger = setup_logger("KanoAgent", logging.INFO)

# 設置 UTF-8 編碼（解決 Windows 終端編碼問題）
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass  # Python < 3.7 不支援 reconfigure

import logging

def run_with_gui(
    on_agent_start=None,
    on_agent_end=None,
    on_task_start=None,
    on_task_end=None,
    on_log=None,
    on_error=None,
):
    """在 GUI 模式下運行（帶回調函數）"""
    logger.info("開始執行 KanoAgent（GUI 模式）")
    
    try:
        # 載入環境變數
        load_dotenv()
        
        # 收集用戶需求（如果已通過 UI 收集，這裡可以跳過）
        user_requirements_text = None
        
        # 創建並執行 Crew
        crew = create_kano_crew_advanced(user_requirements_text=user_requirements_text)
        
        # 執行任務（這裡需要監控執行過程）
        result = crew.kickoff()
        
        # 保存結果
        os.makedirs("output", exist_ok=True)
        with open("output/result.txt", "w", encoding="utf-8") as f:
            f.write(str(result))
        
        # 保存各任務輸出
        from utils.output_saver import extract_and_save_task_outputs
        extract_and_save_task_outputs(result, crew=crew, output_dir="output")
        
        logger.info("執行完成")
        return result
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"執行錯誤：{error_msg}", exc_info=True)
        if on_error:
            on_error(error_msg)
        raise

def main():
    """主程式入口（命令行模式）"""
    logger.info("="*70)
    logger.info("KanoAgent 啟動（命令行模式）")
    logger.info("="*70)
    
    # 載入環境變數
    load_dotenv()
    
    # 重要：如果有 DEEPSEEK_API_KEY，強制清除並重新設置 OPENAI_API_KEY
    # 這可以防止系統使用錯誤的 OpenAI API key
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        # 檢查配置是否使用 DeepSeek
        from config import get_llm_config
        roles_using_deepseek = []
        for role_key in ["pre_sales_consultant", "product_manager", "designer", "architect", "developer"]:
            config = get_llm_config(role_key)
            if config["type"] == "api" and config["api_model"].startswith("deepseek/"):
                roles_using_deepseek.append(role_key)
        
        if roles_using_deepseek:
            # 強制清除可能存在的錯誤 OPENAI_API_KEY
            if "OPENAI_API_KEY" in os.environ:
                old_key = os.environ["OPENAI_API_KEY"]
                if old_key != deepseek_key:
                    del os.environ["OPENAI_API_KEY"]
                    print(f"⚠️  已清除錯誤的 OPENAI_API_KEY（原值: {old_key[:15]}...）")
            
            # 強制設置 DeepSeek 相關環境變數（覆蓋任何現有值）
            os.environ["OPENAI_API_BASE"] = "https://api.deepseek.com/v1"
            os.environ["OPENAI_API_KEY"] = deepseek_key
            os.environ["DEEPSEEK_API_KEY"] = deepseek_key
            
            # 驗證設置
            actual_key = os.getenv("OPENAI_API_KEY")
            actual_base = os.getenv("OPENAI_API_BASE")
            if actual_key == deepseek_key and actual_base == "https://api.deepseek.com/v1":
                print(f"✓ 已設置 DeepSeek API 環境變數（用於 {len(roles_using_deepseek)} 個角色）")
                print(f"  OPENAI_API_BASE = {actual_base}")
                print(f"  OPENAI_API_KEY = {actual_key[:15]}...")
            else:
                print(f"✗ 錯誤：環境變數設置失敗！")
                print(f"  OPENAI_API_KEY 應該是 {deepseek_key[:15]}...，實際是 {actual_key[:15] if actual_key else 'None'}...")
                print(f"  OPENAI_API_BASE 應該是 https://api.deepseek.com/v1，實際是 {actual_base}")
    
    print("="*70)
    print("通用型軟體開發團隊 - KanoAgent (進階版)")
    print("="*70)
    print("\n功能特色：")
    print("  ✓ 資深售前顧問：與客戶互動，澄清軟體需求")
    print("  ✓ 產品經理：根據澄清後的需求產出 PRD")
    print("  ✓ 每個 Role 可獨立配置使用 API 或 Local Model")
    print("  ✓ 自動重試機制（可配置重試次數和延遲）")
    print("  ✓ 指數退避策略處理 API 過載")
    print("  ✓ 智能錯誤處理")
    
    # 步驟 1: 收集用戶需求（交互式問卷）
    print("\n" + "="*70)
    print("步驟 1: 需求收集（客戶問卷）")
    print("="*70)
    from utils.user_interaction import interactive_requirements_collection
    user_requirements_text = interactive_requirements_collection()
    
    if not user_requirements_text:
        print("\n⚠️  未收集到用戶需求，將使用 Agent 模擬對話模式")
        user_requirements_text = None
    else:
        print("\n✓ 用戶需求已收集完成，將傳遞給資深售前顧問進行整理")
    
    print("\n" + "="*70)
    print("步驟 2: 開始執行開發流程...")
    print("="*70 + "\n")
    
    # 創建並執行 Crew（傳遞用戶需求）
    crew = create_kano_crew_advanced(user_requirements_text=user_requirements_text)
    
    try:
        result = crew.kickoff()
        
        print("\n" + "="*60)
        print("專案完成！")
        print("="*60)
        print("\n執行結果：")
        print(result)
        
        # 保存完整結果到檔案
        with open("output/result.txt", "w", encoding="utf-8") as f:
            f.write(str(result))
        
        print("\n結果已保存至 output/result.txt")
        
        # 保存各個任務的輸出到單獨文件
        print("\n正在保存各任務輸出...")
        from utils.output_saver import extract_and_save_task_outputs
        saved_outputs = extract_and_save_task_outputs(result, crew=crew, output_dir="output")
        
        if saved_outputs:
            print("\n✓ 已保存以下任務輸出：")
            for task_name, filepath in saved_outputs.items():
                print(f"  - {task_name}: {filepath}")
        else:
            print("\n⚠️  無法自動提取任務輸出，完整結果已保存在 output/result.txt")
            print("   提示：請檢查 crew.tasks 是否包含 output 屬性")
        
        # 顯示 API 調用統計
        api_logger = get_api_logger()
        api_logger.print_summary()
        
        # 導出 JSON 報告
        json_file = api_logger.export_to_json()
        print(f"API 調用詳細記錄已導出至: {json_file}")
        
    except Exception as e:
        error_msg = str(e)
        
        # 檢查是否為配額用盡錯誤（429 + quota exceeded）
        quota_exceeded_indicators = ["quota exceeded", "exceeded your current quota", "limit: 0"]
        is_quota_exceeded = "429" in error_msg and any(indicator in error_msg.lower() for indicator in quota_exceeded_indicators)
        
        # 檢查是否為 API 過載錯誤（503 或 429 rate limit）
        overload_indicators = ["503", "overloaded", "rate limit", "UNAVAILABLE", "SERVICE_UNAVAILABLE"]
        is_overload = any(indicator in error_msg.upper() for indicator in overload_indicators) or ("429" in error_msg and not is_quota_exceeded)
        
        if is_quota_exceeded:
            print("\n" + "="*70)
            print("⚠️  API 配額已用盡")
            print("="*70)
            print("\n您的 Google Gemini API 免費層級配額已用盡。")
            print("\n📋 錯誤詳情：")
            print("  - 錯誤代碼：429 RESOURCE_EXHAUSTED")
            print("  - 原因：免費層級的輸入 token 配額已用完")
            print("  - 模型：gemini-2.0-flash")
            print("\n💡 解決方案：")
            print("1. 【切換到 Local Model】（推薦，完全免費）")
            print("   在 .env 檔案中設定：")
            print("   PRODUCT_MANAGER_LLM_TYPE=local")
            print("   DESIGNER_LLM_TYPE=local")
            print("   ARCHITECT_LLM_TYPE=local")
            print("   DEVELOPER_LLM_TYPE=local")
            print("   REVIEWER_LLM_TYPE=local")
            print("   TECHNICAL_LLM_TYPE=local")
            print("\n2. 【切換到其他 API】（需要 API Key）")
            print("   使用 DeepSeek API（在 .env 中設定）：")
            print("   DEEPSEEK_API_KEY=your_deepseek_api_key")
            print("   然後在 config/llm_config.py 中將 api_model 改為：")
            print("   \"api_model\": \"deepseek/deepseek-chat\"")
            print("\n3. 【升級到付費計劃】")
            print("   前往：https://ai.google.dev/pricing")
            print("   升級到付費計劃以獲得更多配額")
            print("\n4. 【等待配額重置】")
            print("   免費層級配額通常每月重置一次")
            print("   查看配額使用情況：https://ai.dev/rate-limit")
            print("\n錯誤詳情：")
            print(error_msg[:500])  # 只顯示前 500 字元
        elif is_overload:
            print("\n" + "="*70)
            print("⚠️  API 暫時過載")
            print("="*70)
            print("\n系統已自動重試多次，但仍遇到 API 過載問題。")
            print("\n📋 已執行的應對措施：")
            print("  ✓ 自動重試（指數退避策略）")
            print("  ✓ 智能延遲（避免過度請求）")
            print("  ✓ 隨機抖動（防止雷群效應）")
            print("\n💡 建議解決方案：")
            print("1. 【立即】等待 5-10 分鐘後重新執行")
            print("2. 【檢查】查看 API 服務狀態和額度使用情況")
            print("3. 【切換】使用 Local Model（編輯 .env 設定）：")
            print("   PRODUCT_MANAGER_LLM_TYPE=local")
            print("   DESIGNER_LLM_TYPE=local")
            print("   # ... 其他 Role 同理")
            print("4. 【增強】增加重試配置（編輯 .env）：")
            print("   PRODUCT_MANAGER_RETRY_TIMES=10")
            print("   PRODUCT_MANAGER_RETRY_DELAY=5")
            print("   PRODUCT_MANAGER_MAX_RETRY_DELAY=120")
            print("5. 【查看】詳細指南：API_OVERLOAD_GUIDE.md")
            print("\n錯誤詳情：")
            print(error_msg[:500])  # 只顯示前 500 字元
        elif "404" in error_msg or "NOT_FOUND" in error_msg:
            print("\n" + "="*70)
            print("⚠️  模型不存在")
            print("="*70)
            print("\n指定的模型不存在或不可用。")
            print("\n建議：")
            print("1. 檢查 config/llm_config.py 中的模型名稱")
            print("2. 確認 API Key 有效且有權限使用該模型")
            print("3. 嘗試使用其他模型（如 gemini-2.5-flash）")
        else:
            print(f"\n執行過程中發生錯誤：{e}")
            import traceback
            traceback.print_exc()

def main_gui():
    """GUI 模式入口"""
    try:
        from ui.main_window import MainWindow
        import tkinter as tk
        
        root = tk.Tk()
        app = MainWindow(root)
        root.mainloop()
    except ImportError as e:
        logger.error(f"無法導入 GUI 模組：{e}")
        print("錯誤：無法啟動 GUI 模式，請確保 tkinter 已安裝")
        print("Windows/macOS 通常已包含 tkinter")
        print("Linux: sudo apt-get install python3-tk")

if __name__ == "__main__":
    # 默認使用 GUI 模式，除非指定 --cli 參數
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        main()
    else:
        main_gui()
