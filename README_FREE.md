# 免費 LLM 使用指南

## 🆓 免費選項

### 1. Ollama (推薦 - 完全免費，本地運行)

**優點：**
- ✅ 完全免費
- ✅ 離線運行，保護隱私
- ✅ 無使用限制

**安裝步驟：**

1. 下載並安裝 Ollama：
   - Windows: https://ollama.ai/download
   - 或使用命令：`winget install Ollama.Ollama`

2. 下載模型：
   ```bash
   ollama pull llama3.2
   # 或其他模型：mistral, qwen2.5, gemma2
   ```

3. 安裝 Python 套件：
   ```bash
   pip install langchain-community
   ```

4. 在 `.env` 中不需要設定任何 API Key（Ollama 是本地運行）

5. 執行：
   ```bash
   python crew_free.py
   ```

### 2. Hugging Face (免費額度)

**優點：**
- ✅ 有免費額度
- ✅ 多種模型可選

**申請步驟：**

1. 註冊帳號：https://huggingface.co
2. 申請 API Token：https://huggingface.co/settings/tokens
3. 在 `.env` 中設定：
   ```
   HUGGINGFACE_API_KEY=your_hf_token_here
   ```
4. 安裝套件：
   ```bash
   pip install langchain-huggingface
   ```

### 3. Google Gemini (免費 tier)

**優點：**
- ✅ 有免費額度
- ✅ 效能不錯

**申請步驟：**

1. 申請 API Key：https://makersuite.google.com/app/apikey
2. 在 `.env` 中設定：
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```
3. 安裝套件：
   ```bash
   pip install langchain-google-genai
   ```

## 📝 使用方式

### 使用免費版本：
```bash
python crew_free.py
```

### 使用付費 OpenAI 版本：
```bash
python main.py
```

## 💡 建議

- **開發/測試**：使用 Ollama（完全免費，本地運行）
- **生產環境**：根據需求選擇付費服務或免費額度方案
