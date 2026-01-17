"""
API 重試與延遲處理機制
支援指數退避、自動降級、智能重試
"""
import time
import logging
from typing import Callable, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)

# API 過載相關錯誤碼（可重試）
OVERLOAD_ERRORS = ["503", "overloaded", "rate limit", "UNAVAILABLE", "SERVICE_UNAVAILABLE"]

# 配額用盡相關錯誤碼（不可重試，需要切換方案）
QUOTA_EXHAUSTED_INDICATORS = ["quota exceeded", "exceeded your current quota", "limit: 0"]

def is_overload_error(error_msg: str) -> bool:
    """
    檢查是否為 API 過載錯誤（可重試）
    
    注意：429 錯誤需要區分：
    - Rate Limit（請求過於頻繁）- 可重試
    - Quota Exceeded（配額用盡）- 不可重試
    """
    error_msg_lower = error_msg.lower()
    
    # 先檢查是否為配額用盡（不可重試）
    if "429" in error_msg and any(indicator in error_msg_lower for indicator in QUOTA_EXHAUSTED_INDICATORS):
        return False
    
    # 檢查是否為其他過載錯誤（可重試）
    if any(code.lower() in error_msg_lower for code in OVERLOAD_ERRORS):
        return True
    
    # 429 但沒有配額用盡指標，視為 rate limit（可重試）
    if "429" in error_msg:
        return True
    
    return False

def is_quota_exceeded_error(error_msg: str) -> bool:
    """檢查是否為配額用盡錯誤（不可重試）"""
    error_msg_lower = error_msg.lower()
    return "429" in error_msg and any(indicator in error_msg_lower for indicator in QUOTA_EXHAUSTED_INDICATORS)

def calculate_retry_delay(attempt: int, base_delay: float, backoff: float, max_delay: float = 60.0) -> float:
    """
    計算重試延遲時間（指數退避）
    
    Args:
        attempt: 當前嘗試次數（從 0 開始）
        base_delay: 基礎延遲時間（秒）
        backoff: 退避倍數
        max_delay: 最大延遲時間（秒）
    
    Returns:
        計算後的延遲時間
    """
    delay = base_delay * (backoff ** attempt)
    return min(delay, max_delay)

def retry_with_delay(
    max_retries: int = 3,
    delay: float = 2.0,
    backoff: float = 1.5,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,),
    jitter: bool = True,
):
    """
    重試裝飾器，支援延遲和指數退避
    
    Args:
        max_retries: 最大重試次數
        delay: 初始延遲時間（秒）
        backoff: 退避倍數（每次重試延遲時間會乘以這個值）
        max_delay: 最大延遲時間（秒），防止延遲過長
        exceptions: 要捕獲的異常類型
        jitter: 是否添加隨機抖動（避免雷群效應）
    """
    import random
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    error_msg = str(e)
                    
                    # 檢查是否為可重試的錯誤
                    if attempt < max_retries:
                        if is_overload_error(error_msg):
                            # 計算延遲時間
                            calculated_delay = calculate_retry_delay(attempt, delay, backoff, max_delay)
                            
                            # 添加隨機抖動（±20%）
                            if jitter:
                                jitter_amount = calculated_delay * 0.2 * (random.random() * 2 - 1)
                                actual_delay = max(0.1, calculated_delay + jitter_amount)
                            else:
                                actual_delay = calculated_delay
                            
                            logger.warning(
                                f"⚠️  API 過載錯誤（嘗試 {attempt + 1}/{max_retries + 1}）\n"
                                f"   錯誤: {error_msg[:100]}...\n"
                                f"   等待 {actual_delay:.1f} 秒後重試..."
                            )
                            time.sleep(actual_delay)
                        else:
                            # 其他錯誤（如 404）不重試
                            logger.error(f"❌ 不可重試的錯誤: {error_msg[:200]}")
                            raise
                    else:
                        # 達到最大重試次數
                        logger.error(
                            f"❌ 達到最大重試次數 ({max_retries + 1})\n"
                            f"   最後錯誤: {str(last_exception)[:200]}"
                        )
                        raise last_exception
            
            return None
        return wrapper
    return decorator

class RetryHandler:
    """重試處理器類 - 支援智能重試和自動降級"""
    
    def __init__(
        self,
        max_retries: int = 3,
        delay: float = 2.0,
        backoff: float = 1.5,
        max_delay: float = 60.0,
        jitter: bool = True,
    ):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff
        self.max_delay = max_delay
        self.jitter = jitter
    
    def execute(
        self,
        func: Callable,
        *args,
        exceptions: tuple = (Exception,),
        **kwargs
    ) -> Any:
        """執行函數並處理重試"""
        import random
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                error_msg = str(e)
                
                if attempt < self.max_retries:
                    if is_overload_error(error_msg):
                        # 計算延遲時間（指數退避）
                        calculated_delay = calculate_retry_delay(
                            attempt, self.delay, self.backoff, self.max_delay
                        )
                        
                        # 添加隨機抖動
                        if self.jitter:
                            jitter_amount = calculated_delay * 0.2 * (random.random() * 2 - 1)
                            actual_delay = max(0.1, calculated_delay + jitter_amount)
                        else:
                            actual_delay = calculated_delay
                        
                        logger.warning(
                            f"⚠️  API 過載錯誤（嘗試 {attempt + 1}/{self.max_retries + 1}）\n"
                            f"   錯誤: {error_msg[:100]}...\n"
                            f"   等待 {actual_delay:.1f} 秒後重試..."
                        )
                        time.sleep(actual_delay)
                    else:
                        logger.error(f"❌ 不可重試的錯誤: {error_msg[:200]}")
                        raise
                else:
                    logger.error(
                        f"❌ 達到最大重試次數 ({self.max_retries + 1})\n"
                        f"   最後錯誤: {str(last_exception)[:200]}"
                    )
                    raise last_exception
        
        return None
