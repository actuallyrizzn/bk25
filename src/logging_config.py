"""
BK25 Logging Configuration

Centralized logging setup for the BK25 system.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from .config import config

def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Set up logging configuration for BK25
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    
    # Get log level from config or parameter
    if log_level is None:
        log_level = "DEBUG" if config.debug else "INFO"
    
    # Create logger
    logger = logging.getLogger("bk25")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log file specified)
    if log_file is None:
        log_file = config.data_path / "logs" / "bk25.log"
    
    # Ensure log directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Set propagation to False to avoid duplicate logs
    logger.propagate = False
    
    return logger

def get_logger(name: str = "bk25") -> logging.Logger:
    """
    Get a logger instance for a specific component
    
    Args:
        name: Logger name (usually module name)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"bk25.{name}")

# Create default logger
default_logger = setup_logging()
