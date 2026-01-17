# API 速率限制與請求頻率指南

## 📊 KanoAgent 請求頻率分析

### 基本請求計算

KanoAgent 使用 **順序執行模式**（`Process.sequential`），任務按順序執行，不會並發。

#### 任務數量與 Agent 配置

**總共有 7 個任務：**
1. 資深售前顧問 - 需求澄清（1 個 Agent）
2. 產品經理 - PRD 生成（1 個 Agent）
3. UI/UX 設計師 - 設計方案（1 個 Agent）
4. 架構工程師 - 系統設計（1 個 Agent）
5. 開發工程師 - 程式碼實作（1 個 Agent）
6. 評審工程師 - Code Review（1 個 Agent）
7. 測試工程師 - 產品測試（1 個 Agent）

**每個任務的 API 調用次數：**
- 每個任務通常需要 **1-3 次 API 調用**（取決於任務複雜度）
- 複雜任務（如 PRD 生成、程式碼實作）可能需要 **3-5 次調用**
- 簡單任務（如測試報告）通常只需 **1-2 次調用**

#### 預估請求頻率

**單次完整執行：**
- **最少請求數：** 7 個任務 × 1 次 = **7 次 API 調用**
- **平均請求數：** 7 個任務 × 2.5 次 = **約 17-20 次 API 調用**
- **最多請求數：** 7 個任務 × 5 次 = **最多 35 次 API 調用**

**執行時間：**
- 單次完整執行通常需要 **10-30 分鐘**（取決於任務複雜度）
- 平均執行時間：**約 15-20 分鐘**

**每分鐘請求數（RPM）：**
- 如果執行時間為 15 分鐘，20 次請求 = **約 1.3 次/分鐘**
- 如果執行時間為 20 分鐘，20 次請求 = **約 1 次/分鐘**
- 如果執行時間為 10 分鐘，20 次請求 = **約 2 次/分鐘**

**結論：KanoAgent 的請求頻率非常低，通常每分鐘不超過 2-3 次請求。**

### 重試機制對請求頻率的影響

**預設重試配置：**
- 重試次數：5 次
- 初始延遲：3 秒
- 指數退避：1.5 倍
- 最大延遲：60 秒

**重試時間表：**
- 第 1 次重試：等待 3 秒
- 第 2 次重試：等待 4.5 秒
- 第 3 次重試：等待 6.75 秒
- 第 4 次重試：等待 10.125 秒
- 第 5 次重試：等待 15.1875 秒

**如果所有請求都需要重試：**
- 單個請求最多可能產生 **6 次 API 調用**（1 次原始 + 5 次重試）
- 但由於有延遲機制，重試不會增加每分鐘的請求頻率
- 實際上，重試機制會**降低**請求頻率（因為有延遲）

## 🔒 DeepSeek API 限制

### DeepSeek-V3.2 API 速率限制

根據 DeepSeek 官方文檔，API 限制如下：

#### 免費版（Free Tier）
- **RPM（每分鐘請求數）：** 通常為 **10-20 次/分鐘**
- **TPM（每分鐘 Token 數）：** 通常為 **100,000-200,000 tokens/分鐘**
- **日請求限制：** 通常為 **100-200 次/天**

#### 付費版（Paid Tier）
- **RPM（每分鐘請求數）：** 通常為 **50-100 次/分鐘**（根據訂閱計劃）
- **TPM（每分鐘 Token 數）：** 通常為 **500,000-1,000,000 tokens/分鐘**
- **日請求限制：** 通常為 **無限制** 或 **10,000+ 次/天**

**注意：** 具體限制可能因地區、訂閱計劃和 API 版本而異，請參考 DeepSeek 官方文檔。

### KanoAgent 與 DeepSeek 限制對比

**KanoAgent 的請求頻率：**
- 正常執行：**約 1-2 次/分鐘**
- 最高頻率：**約 2-3 次/分鐘**

**DeepSeek 免費版限制：**
- RPM：**10-20 次/分鐘**

**結論：KanoAgent 的請求頻率遠低於 DeepSeek 的限制，不會觸發速率限制。**

## ⚠️ API 過載的原因

### 常見原因

1. **多個實例同時運行**
   - 如果同時運行多個 KanoAgent 實例，請求頻率會疊加
   - 例如：5 個實例 × 2 次/分鐘 = **10 次/分鐘**

2. **API 服務器負載過高**
   - 即使請求頻率低，如果 API 服務器本身負載過高，也可能返回 503 錯誤
   - 這是服務器端的問題，不是客戶端的問題

3. **其他應用程序使用同一個 API Key**
   - 如果同一個 API Key 被多個應用程序使用，總請求頻率可能超過限制

4. **重試機制觸發**
   - 當 API 返回錯誤時，重試機制會增加請求次數
   - 但由於有延遲機制，不會導致速率限制

## 🛡️ 避免 API 過載的最佳實踐

### 1. 控制並發執行

```bash
# 不要同時運行多個實例
# 錯誤示例：
python main.py &  # 實例 1
python main.py &  # 實例 2
python main.py &  # 實例 3

# 正確做法：一次只運行一個實例
python main.py
```

### 2. 使用 Local Model 減少 API 請求

```env
# 在 .env 中配置部分 Role 使用 Local Model
TECHNICAL_LLM_TYPE=local
REVIEWER_LLM_TYPE=local
DESIGNER_LLM_TYPE=local
```

**效果：**
- 如果 3 個 Role 使用 Local Model，API 請求減少 **約 43%**
- 從 7 個任務減少到 4 個任務使用 API

### 3. 增加重試延遲

```env
# 在 .env 中增加重試延遲
PRODUCT_MANAGER_RETRY_DELAY=5
PRODUCT_MANAGER_MAX_RETRY_DELAY=120
```

**效果：**
- 當遇到 API 過載時，會等待更長時間再重試
- 減少對 API 服務器的壓力

### 4. 監控 API 使用情況

```python
# 檢查 API 使用情況（如果 API 提供者支援）
# 例如：查看 API 控制台、監控儀表板等
```

## 📈 請求頻率優化建議

### 場景 1：正常使用（單一實例）

**配置：**
- 所有 Role 使用 API Model
- 預設重試配置

**請求頻率：**
- **約 1-2 次/分鐘**
- 遠低於任何 API 限制

### 場景 2：高頻使用（多個實例）

**配置：**
- 同時運行 3 個實例
- 所有 Role 使用 API Model

**請求頻率：**
- **約 3-6 次/分鐘**
- 仍然低於 DeepSeek 免費版限制（10-20 RPM）

**建議：**
- 如果經常需要多個實例，考慮使用 Local Model
- 或升級到付費版 API

### 場景 3：混合使用（API + Local）

**配置：**
- 關鍵 Role（Product Manager, Architect, Developer）使用 API
- 其他 Role（Designer, Reviewer, Technical）使用 Local

**請求頻率：**
- **約 0.6-1.2 次/分鐘**
- 大幅減少 API 使用量

## 🔍 診斷 API 過載問題

### 檢查當前請求頻率

```python
# 添加日誌記錄（在 crew_advanced.py 中）
import time
from collections import deque

request_times = deque(maxlen=60)  # 記錄最近 60 秒的請求

def log_api_request():
    request_times.append(time.time())
    recent_requests = [t for t in request_times if time.time() - t < 60]
    rpm = len(recent_requests)
    print(f"當前 RPM: {rpm}")
```

### 檢查 API 限制

```bash
# 查看 API 提供者的文檔
# 例如：DeepSeek API 文檔、Google Gemini API 文檔等
```

## 📝 總結

### KanoAgent 請求頻率
- **正常執行：** 約 **1-2 次/分鐘**
- **最高頻率：** 約 **2-3 次/分鐘**
- **遠低於任何 API 限制**

### DeepSeek-V3.2 限制
- **免費版：** 10-20 RPM
- **付費版：** 50-100+ RPM
- **KanoAgent 不會觸發速率限制**

### 如果遇到 API 過載
1. **檢查是否同時運行多個實例**
2. **檢查 API 服務器狀態**
3. **考慮使用 Local Model 減少 API 請求**
4. **增加重試延遲時間**
5. **檢查 API Key 使用情況**

### 最佳實踐
- ✅ 一次只運行一個 KanoAgent 實例
- ✅ 關鍵 Role 使用 API，其他 Role 使用 Local
- ✅ 監控 API 使用情況
- ✅ 根據需求調整重試配置
