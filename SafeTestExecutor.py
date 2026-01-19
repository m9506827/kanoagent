import subprocess
import shlex
import logging
from typing import Dict, Union, List

# 設定 Log 格式，方便追蹤 Agent 行為
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SafeTestExecutor:
    """
    提供給 Agent 使用的安全測試執行工具。
    包含指令白名單檢查與執行時間限制。
    """
    
    def __init__(self, timeout_seconds: int = 30):
        self.timeout = timeout_seconds
        # 🛡️ 安全機制 1: 白名單 (Whitelist)
        # 只允許 Agent 執行特定的測試指令，防止惡意操作 (如 rm, wget, curl)
        self.allowed_commands = {
            "pytest": "執行 Python 單元測試",
            "npm test": "執行 Node.js 測試",
            "python -m unittest": "執行標準庫測試",
            "flake8": "程式碼風格檢查",
            "pylint": "程式碼品質分析"
        }

    def validate_command(self, command_str: str) -> bool:
        """檢查指令是否在白名單內"""
        # 使用 shlex.split 正確解析指令字串，避免 shell injection 風險
        try:
            parts = shlex.split(command_str)
            if not parts:
                return False
            
            # 檢查指令開頭是否為允許的工具
            # 例如: "pytest tests/test_login.py" -> 開頭是 "pytest" -> 通過
            base_cmd = parts[0]
            
            # 針對複合指令的簡單處理 (如 npm test)
            if base_cmd == "npm" and len(parts) > 1 and parts[1] == "test":
                return True
            if base_cmd == "python" and len(parts) > 2 and parts[1] == "-m" and parts[2] == "unittest":
                return True
                
            return base_cmd in self.allowed_commands
            
        except Exception as e:
            logging.error(f"指令解析失敗: {e}")
            return False

    def run_test(self, command_str: str) -> Dict[str, Union[bool, str, int]]:
        """
        執行測試指令並捕捉輸出。
        
        Returns:
            Dict: 包含執行結果、標準輸出(stdout)、錯誤輸出(stderr)的結構化資料
        """
        logging.info(f"Agent 嘗試執行: {command_str}")

        # 1. 安全檢查
        if not self.validate_command(command_str):
            msg = f"⛔ 安全阻擋: 指令 '{command_str}' 不在允許清單中。"
            logging.warning(msg)
            return {
                "success": False,
                "output": "",
                "error": msg,
                "exit_code": -1
            }

        # 2. 執行指令
        try:
            # 🛡️ 安全機制 2: 不使用 shell=True (除非必要)，減少注入風險
            # 🛡️ 安全機制 3: 設定 timeout，防止無限迴圈 (Deadlock)
            result = subprocess.run(
                shlex.split(command_str),
                capture_output=True, # 捕捉輸出給 Agent 閱讀
                text=True,           # 自動解碼為字串
                timeout=self.timeout,
                check=False          # 測試失敗不拋出 Exception，而是回傳 exit_code
            )

            is_success = (result.returncode == 0)
            
            # 回傳結構化資訊給 Quality Agent
            return {
                "success": is_success,
                "output": result.stdout,
                "error": result.stderr if result.stderr else ("測試失敗" if not is_success else ""),
                "exit_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            msg = f"⏳ 執行超時: 指令執行超過 {self.timeout} 秒，已強制終止。"
            logging.error(msg)
            return {
                "success": False,
                "output": "",
                "error": msg,
                "exit_code": 124 # 常見的 Timeout exit code
            }
        except Exception as e:
            msg = f"💥 系統錯誤: {str(e)}"
            logging.error(msg)
            return {
                "success": False,
                "output": "",
                "error": msg,
                "exit_code": -1
            }

# --- 模擬 Agent 調用情境 ---
if __name__ == "__main__":
    tool = SafeTestExecutor(timeout_seconds=5)

    # 情境 A: Agent 嘗試執行合法的測試
    print("--- Test A: Valid Command ---")
    # 假設目錄下沒有測試檔，這裡僅示範邏輯
    response_a = tool.run_test("pytest tests/") 
    print(f"Agent 收到: {response_a}\n")

    # 情境 B: Agent 嘗試執行危險指令
    print("--- Test B: Malicious Command ---")
    response_b = tool.run_test("rm -rf /")
    print(f"Agent 收到: {response_b}\n")
    
    # 情境 C: Agent 寫的 Code 造成無限迴圈
    print("--- Test C: Infinite Loop Protection ---")
    # 模擬一個睡 10 秒的指令，但我們 timeout 設為 5 秒
    response_c = tool.run_test("python -c 'import time; time.sleep(10)'") 
    print(f"Agent 收到: {response_c}")