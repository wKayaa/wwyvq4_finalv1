#!/usr/bin/env python3
"""
WWYVQ v2.1 System Logger
Centralized logging system for all modules

Author: wKayaa
Date: 2025-01-07
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class LogLevel(Enum):
    """Logging levels"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class SystemLogger:
    """
    WWYVQ v2.1 System Logger
    Provides centralized logging for all modules
    """
    
    def __init__(self, name: str, log_level: LogLevel = LogLevel.INFO, 
                 log_dir: Optional[str] = None, enable_console: bool = True):
        """Initialize system logger"""
        self.name = name
        self.log_level = log_level
        self.log_dir = Path(log_dir) if log_dir else Path("./logs")
        self.enable_console = enable_console
        
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level.value)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Setup handlers
        self._setup_file_handler()
        if enable_console:
            self._setup_console_handler()
        
        # Setup formatter
        self._setup_formatter()
    
    def _setup_file_handler(self):
        """Setup file handler for logging"""
        log_file = self.log_dir / f"{self.name.lower()}_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Use rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        
        file_handler.setLevel(self.log_level.value)
        self.logger.addHandler(file_handler)
        self.file_handler = file_handler
    
    def _setup_console_handler(self):
        """Setup console handler for logging"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level.value)
        self.logger.addHandler(console_handler)
        self.console_handler = console_handler
    
    def _setup_formatter(self):
        """Setup log formatter"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Apply formatter to all handlers
        for handler in self.logger.handlers:
            handler.setFormatter(formatter)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        self.logger.debug(message, extra=extra)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message"""
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log error message"""
        self.logger.error(message, extra=extra)
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log critical message"""
        self.logger.critical(message, extra=extra)
    
    def set_level(self, level: LogLevel):
        """Set logging level"""
        self.log_level = level
        self.logger.setLevel(level.value)
        
        # Update handler levels
        for handler in self.logger.handlers:
            handler.setLevel(level.value)
    
    def get_logger(self) -> logging.Logger:
        """Get the underlying logger"""
        return self.logger


# Global logger instance
_global_logger = None


def get_logger(name: str = "WWYVQ") -> SystemLogger:
    """Get or create global logger instance"""
    global _global_logger
    
    if _global_logger is None:
        _global_logger = SystemLogger(name)
    
    return _global_logger


def setup_global_logging(log_level: LogLevel = LogLevel.INFO, 
                        log_dir: Optional[str] = None,
                        enable_console: bool = True):
    """Setup global logging configuration"""
    global _global_logger
    
    _global_logger = SystemLogger(
        "WWYVQ",
        log_level=log_level,
        log_dir=log_dir,
        enable_console=enable_console
    )
    
    return _global_logger