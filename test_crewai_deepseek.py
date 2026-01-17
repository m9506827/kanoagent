"""
測試 CrewAI OpenAICompletion 實際發送的請求
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
from dotenv import load_dotenv

load_dotenv()

print("="*70)
print("測試 CrewAI OpenAICompletion 實際請求")
print("="*70)

deepseek_key = os.getenv("DEEPSEEK_API_KEY")
if not deepseek_key:
    print("❌ 未設定 DEEPSEEK_API_KEY")
    exit(1)

print(f"\nAPI Key: {deepseek_key[:20]}...")

# 創建 OpenAICompletion 實例
from crewai.llms.providers.openai.completion import OpenAICompletion

completion = OpenAICompletion(
    model="deepseek-chat",
    api_key=deepseek_key,
    base_url="https://api.deepseek.com/v1",
    temperature=0.7,
)

print(f"\n實例配置：")
params = completion._get_client_params()
print(f"  Client params: {params}")
print(f"  Model 屬性: {getattr(completion, 'model', 'N/A')}")

# 檢查 client
if hasattr(completion, 'client'):
    client = completion.client
    print(f"  Client base_url: {getattr(client, 'base_url', 'N/A')}")

# 嘗試調用（這會實際發送請求）
print(f"\n嘗試調用 API...")
try:
    # 使用 call 方法（這是 CrewAI 實際使用的方法）
    # 檢查 call 方法的簽名
    import inspect
    sig = inspect.signature(completion.call)
    print(f"  call 方法參數: {list(sig.parameters.keys())}")
    
    # 嘗試調用
    response = completion.call(
        messages=[{"role": "user", "content": "Say hi"}]
    )
    print(f"✅ 成功！")
    print(f"  回應: {str(response)[:100] if response else 'None'}...")
except Exception as e:
    print(f"❌ 錯誤: {e}")
    error_str = str(e)
    if "402" in error_str or "Insufficient" in error_str:
        print(f"\n⚠️  402 錯誤 - 可能的原因：")
        print(f"  1. 帳戶餘額不足")
        print(f"  2. 模型名稱不正確（實際發送的模型名稱可能不是 'deepseek-chat'）")
        print(f"  3. API key 對應的帳戶沒有權限使用該模型")
    
    # 檢查實際發送的請求
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
