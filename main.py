"""
KanoAgent - 通用型軟體開發團隊主程式
使用 CrewAI 實作的智能開發團隊
支援每個 Role 獨立配置 API/Local Model，並包含重試機制
"""
import os
from dotenv import load_dotenv
from crew_advanced import create_kano_crew_advanced

def main():
    """主程式入口"""
    # 載入環境變數
    load_dotenv()
    
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
    print("\n開始執行開發流程...\n")
    
    # 創建並執行 Crew
    crew = create_kano_crew_advanced()
    
    try:
        result = crew.kickoff()
        
        print("\n" + "="*60)
        print("專案完成！")
        print("="*60)
        print("\n執行結果：")
        print(result)
        
        # 保存結果到檔案
        with open("output/result.txt", "w", encoding="utf-8") as f:
            f.write(str(result))
        
        print("\n結果已保存至 output/result.txt")
        
    except Exception as e:
        error_msg = str(e)
        
        # 檢查是否為 API 過載錯誤
        overload_indicators = ["503", "429", "overloaded", "rate limit", "UNAVAILABLE", "SERVICE_UNAVAILABLE", "RESOURCE_EXHAUSTED"]
        is_overload = any(indicator in error_msg.upper() for indicator in overload_indicators)
        
        if is_overload:
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

if __name__ == "__main__":
    main()
