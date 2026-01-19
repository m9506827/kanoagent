"""
日誌配置模組
配置統一的日誌系統，將所有日誌寫入 KanoAgent.log
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# 日誌文件路徑
LOG_FILE = "KanoAgent.log"
LOG_DIR = "logs"

def setup_logger(name: str = "KanoAgent", log_level: int = logging.INFO) -> logging.Logger:
    """
    設置統一的日誌記錄器
    
    Args:
        name: Logger 名稱
        log_level: 日誌級別（默認 INFO）
    
    Returns:
        配置好的 Logger 實例
    """
    # 確保日誌目錄存在
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # 創建 logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # 避免重複添加 handler
    if logger.handlers:
        return logger
    
    # 創建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件 handler（旋轉日誌，最大10MB，保留5個備份）
    log_file_path = os.path.join(LOG_DIR, LOG_FILE)
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # 控制台 handler（只顯示 INFO 及以上級別）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # 添加 handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str = "KanoAgent") -> logging.Logger:
    """獲取配置好的 logger"""
    return logging.getLogger(name)
