# GUI 使用指南

## 🎨 功能概述

KanoAgent 現在提供圖形界面（GUI），包含以下三個主要功能：

### 1. 模型配置界面
- 顯示所有 Role 的模型配置
- 可修改每個 Role 的 LLM 類型（API/Local）
- 可修改 API 模型和 Local 模型名稱
- 配置可保存到環境變數

### 2. 執行監控界面
- 實時顯示所有 Role 的執行狀態
- 顯示當前正在執行的 Agent
- 顯示任務進度
- 顯示執行日誌

### 3. 需求收集界面
- 快速勾選常見需求選項
- 支持自定義輸入
- 按類別組織問題
- 自動格式化輸出

### 4. 日誌系統
- 所有日誌（INFO 和 ERROR）寫入 `logs/KanoAgent.log`
- 支持日誌旋轉（最大 10MB，保留 5 個備份）
- 包含時間戳和日誌級別

## 🚀 啟動方式

### 方式 1: 使用快捷腳本（推薦）
```bash
python run_gui.py
```

### 方式 2: 使用命令行參數
```bash
python main.py --gui
```

### 方式 3: 直接運行主程式（命令行模式）
```bash
python main.py
```

## 📋 使用步驟

### 步驟 1: 配置模型
1. 啟動 GUI 後，點擊「模型配置」標籤頁
2. 查看或修改每個 Role 的配置：
   - **類型**：選擇 "api" 或 "local"
   - **API 模型**：輸入 API 模型名稱（如 `deepseek/deepseek-chat`）
   - **Local 模型**：輸入 Local 模型名稱（如 `ollama/gemma3:4b`）
3. 點擊「保存配置」按鈕保存設置

### 步驟 2: 收集需求（可選）
1. 在開始執行前，可以通過需求收集界面快速選擇需求
2. 點擊「需求收集」按鈕（如果可用）
3. 在各個類別中勾選符合的需求
4. 或直接輸入自定義答案
5. 點擊「確認」保存需求

### 步驟 3: 開始執行
1. 切換到「執行監控」標籤頁
2. 點擊「開始執行」按鈕
3. 監控執行進度：
   - 查看 Role 狀態（等待中/執行中/完成）
   - 查看當前 Agent
   - 查看任務進度條
   - 查看執行日誌

### 步驟 4: 查看結果
1. 執行完成後，結果會自動保存到 `output/` 目錄
2. 查看 `logs/KanoAgent.log` 了解詳細執行過程
3. 查看 `output/api_calls.json` 了解 API 調用統計

## 📁 文件結構

```
KanoAgent/
├── ui/
│   ├── __init__.py
│   ├── main_window.py      # 主視窗 GUI
│   └── requirements_ui.py  # 需求收集 UI
├── utils/
│   └── logger_config.py    # 日誌配置
├── logs/
│   └── KanoAgent.log       # 主日誌文件
├── output/
│   ├── result.txt          # 完整結果
│   ├── *.md                # 各任務輸出
│   └── api_calls.json      # API 調用統計
├── main.py                 # 主程式
└── run_gui.py              # GUI 啟動腳本
```

## 🔧 日誌系統

### 日誌位置
- 主日誌文件：`logs/KanoAgent.log`
- API 調用日誌：`output/api_calls.log`

### 日誌格式
```
2024-01-17 21:30:45 - KanoAgent - INFO - 開始執行 KanoAgent
2024-01-17 21:30:46 - crew_advanced - INFO - 創建 LLM 實例
2024-01-17 21:30:47 - KanoAgent - ERROR - 執行錯誤：...
```

### 日誌級別
- **INFO**：一般信息（執行進度、狀態更新）
- **WARNING**：警告信息（API 重試、配置問題）
- **ERROR**：錯誤信息（執行失敗、異常）

### 日誌旋轉
- 當日誌文件達到 10MB 時自動旋轉
- 保留最近 5 個備份文件
- 文件名格式：`KanoAgent.log`, `KanoAgent.log.1`, `KanoAgent.log.2`, ...

## ⚠️ 注意事項

1. **tkinter 依賴**
   - Windows/macOS：通常已包含 tkinter
   - Linux：需要安裝 `python3-tk`
     ```bash
     sudo apt-get install python3-tk
     ```

2. **執行模式**
   - GUI 模式：適合交互式使用，可實時監控
   - 命令行模式：適合自動化腳本和 CI/CD

3. **配置保存**
   - 配置保存在環境變數中，不會修改 `.env` 文件
   - 如需永久保存，請手動編輯 `.env` 文件

4. **日誌文件**
   - 日誌文件會持續增長，建議定期清理
   - 可以手動刪除舊的日誌文件

## 🐛 故障排除

### 問題：無法啟動 GUI
**解決：**
1. 檢查是否安裝 tkinter：`python -c "import tkinter"`
2. Linux 用戶：安裝 `python3-tk`
3. 檢查 Python 版本（需要 >= 3.7）

### 問題：日誌文件未生成
**解決：**
1. 檢查 `logs/` 目錄是否存在
2. 檢查文件權限
3. 查看控制台是否有錯誤信息

### 問題：配置無法保存
**解決：**
1. 檢查是否有寫入權限
2. 查看日誌文件中的錯誤信息
3. 嘗試手動設置環境變數

## 📝 更新日誌

### v1.0.0 (2024-01-17)
- ✅ 添加 GUI 主視窗
- ✅ 添加模型配置界面
- ✅ 添加執行監控界面
- ✅ 添加需求收集 UI
- ✅ 配置統一日誌系統
- ✅ 日誌寫入 `logs/KanoAgent.log`
