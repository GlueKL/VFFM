"""
Logging setup for the video processing pipeline
"""
import os
import logging
import sys
from typing import Optional

def setup_logger(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up logger for the video processing pipeline.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (if None, logs are output to console only)
        
    Returns:
        Configured logger
    """
    # Get numeric logging level
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid logging level: {log_level}")
    
    # Configure base logger
    logger = logging.getLogger("video_pipeline")
    logger.setLevel(numeric_level)
    logger.handlers = []  # Clear handlers to avoid duplication
    
    # Формат для файла логов (подробный)
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Формат для консоли (компактный)
    console_formatter = logging.Formatter(
        "%(message)s"
    )
    
    # Console handler (только важные сообщения)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.WARNING)  # В консоль только WARNING и выше
    logger.addHandler(console_handler)
    
    # File handler (все сообщения)
    if log_file:
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(numeric_level)  # В файл все сообщения
        logger.addHandler(file_handler)
    
    return logger 