"""
啟動 GUI 模式的快捷腳本
默認啟動 GUI，顯示模型配置界面，確認後再執行
"""
import sys
import os

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main_gui

if __name__ == "__main__":
    print("="*70)
    print("KanoAgent GUI 模式")
    print("="*70)
    print("提示：")
    print("  1. 啟動後會先顯示模型配置界面")
    print("  2. 請確認或修改 LLM 模型配置")
    print("  3. 點擊「確認配置並開始執行」按鈕開始執行")
    print("="*70 + "\n")
    main_gui()
