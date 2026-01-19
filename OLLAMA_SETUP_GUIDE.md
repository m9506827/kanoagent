# Ollama 設置指南

## 🔍 Ollama 不可用的情況

根據代碼檢查邏輯，Ollama 會在以下兩種情況下被判定為「不可用」：

### 1. Python 模組不可導入

**檢查代碼：**
```python
try:
    from langchain_community.llms import Ollama
except ImportError:
    return False  # Ollama 不可用
```

**可能原因：**
- ❌ 未安裝 `langchain-community` 套件
- ❌ Python 環境中缺少依賴
- ❌ 套件版本不兼容

**解決方案：**
```bash
# 安裝 langchain-community
pip install langchain-community>=0.3.0

# 或重新安裝所有依賴
pip install -r requirements.txt
```

### 2. Ollama 服務未運行

**檢查代碼：**
```python
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=2)
    return response.status_code == 200
except:
    return False  # Ollama 服務不可用
```

**可能原因：**

#### 2.1 Ollama 未安裝
- ❌ 系統中沒有安裝 Ollama
- ❌ Ollama 安裝不完整

**解決方案：**
1. **下載並安裝 Ollama**
   - Windows: https://ollama.ai/download/windows
   - macOS: https://ollama.ai/download/mac
   - Linux: https://ollama.ai/download/linux

2. **驗證安裝**
   ```bash
   ollama --version
   ```

#### 2.2 Ollama 服務未啟動
- ❌ Ollama 已安裝但未啟動
- ❌ Ollama 服務已停止

**解決方案：**
1. **啟動 Ollama**
   - Windows: 通常會自動啟動，或從開始菜單啟動
   - macOS/Linux: 運行 `ollama serve` 或確保服務正在運行

2. **檢查服務狀態**
   ```bash
   # 檢查 Ollama 是否運行
   curl http://localhost:11434/api/tags
   
   # 或使用瀏覽器訪問
   # http://localhost:11434/api/tags
   ```

#### 2.3 端口被占用
- ❌ 端口 11434 被其他程序占用
- ❌ 防火牆阻止連接

**解決方案：**
1. **檢查端口占用**
   ```bash
   # Windows
   netstat -ano | findstr :11434
   
   # macOS/Linux
   lsof -i :11434
   ```

2. **修改 Ollama 端口（如果需要）**
   ```bash
   # 設置環境變數
   export OLLAMA_HOST=localhost:11435
   ```

#### 2.4 網路連接問題
- ❌ 無法連接到 localhost
- ❌ 代理設置問題

**解決方案：**
1. **檢查本地連接**
   ```bash
   ping localhost
   ```

2. **檢查代理設置**
   - 確保沒有代理阻止 localhost 連接

#### 2.5 模型未下載
- ❌ 配置的模型不存在
- ❌ 模型下載不完整

**解決方案：**
1. **下載所需模型**
   ```bash
   # 下載 gemma3:4b（quality 和 technical 使用）
   ollama pull gemma3:4b
   
   # 下載其他常用模型
   ollama pull deepseek-coder:33b
   ollama pull llama3.2:3b
   ```

2. **檢查已下載的模型**
   ```bash
   ollama list
   ```

3. **驗證模型可用性**
   ```bash
   ollama run gemma3:4b "Hello"
   ```

## 🔧 完整設置步驟

### Windows

1. **安裝 Ollama**
   - 下載：https://ollama.ai/download/windows
   - 運行安裝程序
   - 安裝完成後，Ollama 通常會自動啟動

2. **驗證安裝**
   ```powershell
   ollama --version
   ```

3. **下載模型**
   ```powershell
   ollama pull gemma3:4b
   ```

4. **測試連接**
   ```powershell
   curl http://localhost:11434/api/tags
   ```

5. **安裝 Python 依賴**
   ```powershell
   pip install langchain-community>=0.3.0
   ```

### macOS

1. **安裝 Ollama**
   ```bash
   # 使用 Homebrew
   brew install ollama
   
   # 或下載安裝包
   # https://ollama.ai/download/mac
   ```

2. **啟動服務**
   ```bash
   ollama serve
   ```

3. **下載模型**
   ```bash
   ollama pull gemma3:4b
   ```

4. **安裝 Python 依賴**
   ```bash
   pip install langchain-community>=0.3.0
   ```

### Linux

1. **安裝 Ollama**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **啟動服務**
   ```bash
   systemctl start ollama
   # 或
   ollama serve
   ```

3. **下載模型**
   ```bash
   ollama pull gemma3:4b
   ```

4. **安裝 Python 依賴**
   ```bash
   pip install langchain-community>=0.3.0
   ```

## ✅ 驗證 Ollama 可用性

運行以下 Python 代碼來驗證：

```python
import requests

def check_ollama():
    # 檢查模組
    try:
        from langchain_community.llms import Ollama
        print("✓ langchain_community 模組可用")
    except ImportError:
        print("✗ langchain_community 模組不可用")
        return False
    
    # 檢查服務
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("✓ Ollama 服務正在運行")
            models = response.json().get('models', [])
            print(f"  已下載的模型: {[m.get('name') for m in models]}")
            return True
        else:
            print(f"✗ Ollama 服務返回錯誤: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Ollama 服務不可用: {e}")
        return False

if __name__ == "__main__":
    check_ollama()
```

## 🚨 常見錯誤與解決

### 錯誤：`Connection refused`
**原因：** Ollama 服務未啟動
**解決：** 啟動 Ollama 服務

### 錯誤：`ModuleNotFoundError: No module named 'langchain_community'`
**原因：** 未安裝 langchain-community
**解決：** `pip install langchain-community>=0.3.0`

### 錯誤：`Model not found`
**原因：** 配置的模型未下載
**解決：** 使用 `ollama pull <model_name>` 下載模型

### 錯誤：`Timeout`
**原因：** 網路連接問題或服務響應慢
**解決：** 檢查網路連接，增加 timeout 時間

## 📝 在 KanoAgent 中的配置

當 Ollama 不可用時，系統會：

1. **自動檢測**：在啟動時檢查 Ollama 可用性
2. **顯示警告**：在配置表中標示「⚠️ 降級」
3. **自動降級**：將 local model 配置自動切換為 API model
4. **提供提示**：顯示解決方案和設置步驟

## 🔗 相關資源

- Ollama 官方網站：https://ollama.ai/
- Ollama 模型庫：https://ollama.ai/library
- LangChain Community 文檔：https://python.langchain.com/docs/integrations/llms/ollama
