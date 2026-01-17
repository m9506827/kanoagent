"""
API 調用日誌記錄器
記錄每個 API 調用的詳細信息，包括 Agent、模型、時間、Token 使用等
"""
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
import json
import os

logger = logging.getLogger(__name__)

class APILogger:
    """API 調用日誌記錄器"""
    
    def __init__(self, log_file: Optional[str] = None):
        """
        初始化 API 日誌記錄器
        
        Args:
            log_file: 日誌檔案路徑（可選），如果提供則會保存到檔案
        """
        self.log_file = log_file or "output/api_calls.log"
        self.calls: List[Dict] = []
        self.stats = defaultdict(int)
        
        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(self.log_file) if os.path.dirname(self.log_file) else ".", exist_ok=True)
    
    def log_call(
        self,
        agent_name: str,
        model: str,
        llm_type: str,
        status: str = "success",
        error: Optional[str] = None,
        tokens_used: Optional[int] = None,
        duration: Optional[float] = None,
    ):
        """
        記錄 API 調用
        
        Args:
            agent_name: Agent 名稱
            model: 使用的模型
            llm_type: LLM 類型（"api" 或 "local"）
            status: 調用狀態（"success", "error", "retry"）
            error: 錯誤訊息（如果有）
            tokens_used: 使用的 Token 數量（如果有）
            duration: 調用持續時間（秒）
        """
        call_info = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "model": model,
            "llm_type": llm_type,
            "status": status,
            "error": error,
            "tokens_used": tokens_used,
            "duration": duration,
        }
        
        self.calls.append(call_info)
        self.stats[f"{agent_name}_{status}"] += 1
        self.stats[f"total_{status}"] += 1
        
        # 記錄到日誌
        if status == "success":
            logger.info(
                f"✅ API 調用成功 - Agent: {agent_name}, Model: {model}, "
                f"Type: {llm_type}, Duration: {duration:.2f}s"
                + (f", Tokens: {tokens_used}" if tokens_used else "")
            )
        elif status == "error":
            logger.error(
                f"❌ API 調用失敗 - Agent: {agent_name}, Model: {model}, "
                f"Error: {error}"
            )
        elif status == "retry":
            logger.warning(
                f"🔄 API 調用重試 - Agent: {agent_name}, Model: {model}, "
                f"Error: {error}"
            )
        
        # 保存到檔案
        self._save_to_file(call_info)
    
    def _save_to_file(self, call_info: Dict):
        """保存調用記錄到檔案"""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(call_info, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.warning(f"無法保存 API 調用日誌: {e}")
    
    def get_stats(self) -> Dict:
        """獲取統計信息"""
        stats = {
            "total_calls": len(self.calls),
            "success_calls": self.stats["total_success"],
            "error_calls": self.stats["total_error"],
            "retry_calls": self.stats["total_retry"],
            "by_agent": {},
            "by_model": defaultdict(int),
        }
        
        # 按 Agent 統計
        for call in self.calls:
            agent = call["agent"]
            if agent not in stats["by_agent"]:
                stats["by_agent"][agent] = {
                    "total": 0,
                    "success": 0,
                    "error": 0,
                    "retry": 0,
                }
            stats["by_agent"][agent]["total"] += 1
            stats["by_agent"][agent][call["status"]] += 1
            
            # 按模型統計
            stats["by_model"][call["model"]] += 1
        
        return stats
    
    def print_summary(self):
        """打印統計摘要"""
        stats = self.get_stats()
        
        print("\n" + "="*70)
        print("API 調用統計摘要")
        print("="*70)
        print(f"總調用次數: {stats['total_calls']}")
        print(f"成功: {stats['success_calls']}")
        print(f"失敗: {stats['error_calls']}")
        print(f"重試: {stats['retry_calls']}")
        
        print("\n按 Agent 統計:")
        for agent, agent_stats in stats["by_agent"].items():
            print(f"  {agent}:")
            print(f"    總計: {agent_stats['total']}")
            print(f"    成功: {agent_stats['success']}")
            print(f"    失敗: {agent_stats['error']}")
            print(f"    重試: {agent_stats['retry']}")
        
        print("\n按模型統計:")
        for model, count in stats["by_model"].items():
            print(f"  {model}: {count} 次")
        
        print(f"\n詳細日誌已保存至: {self.log_file}")
        print("="*70 + "\n")
    
    def export_to_json(self, output_file: Optional[str] = None) -> str:
        """導出所有調用記錄為 JSON"""
        output_file = output_file or "output/api_calls.json"
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "calls": self.calls,
                "stats": self.get_stats(),
            }, f, ensure_ascii=False, indent=2)
        
        return output_file

# 全局實例
_api_logger: Optional[APILogger] = None

def get_api_logger() -> APILogger:
    """獲取全局 API 日誌記錄器實例"""
    global _api_logger
    if _api_logger is None:
        _api_logger = APILogger()
    return _api_logger

def reset_api_logger():
    """重置 API 日誌記錄器（用於測試）"""
    global _api_logger
    _api_logger = None
