"""Common utilities for the security AI platform."""

import logging
import json
from typing import Any, Dict
from datetime import datetime
from pathlib import Path


def setup_logging(level: str = "INFO", log_file: str = None) -> logging.Logger:
    """
    Setup standardized logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for logs
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # JSON formatter for structured logging
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
        '"logger": "%(name)s", "message": "%(message)s"}'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division fails
        
    Returns:
        Result of division or default
    """
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ZeroDivisionError):
        return default


def load_json_config(config_path: Path) -> Dict[str, Any]:
    """
    Load JSON configuration file.
    
    Args:
        config_path: Path to JSON config file
        
    Returns:
        Configuration dictionary
    """
    with open(config_path, 'r') as f:
        return json.load(f)


def timestamp_to_iso(ts: datetime) -> str:
    """Convert datetime to ISO format string."""
    return ts.isoformat() + 'Z' if ts.tzinfo is None else ts.isoformat()


class Timer:
    """Context manager for timing code blocks."""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.start_time = None
        self.elapsed = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, *args):
        self.elapsed = (datetime.now() - self.start_time).total_seconds()
        logging.info(f"{self.name} took {self.elapsed:.4f} seconds")
