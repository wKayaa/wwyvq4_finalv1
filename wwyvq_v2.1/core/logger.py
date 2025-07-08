#!/usr/bin/env python3
"""
📝 WWYVQ Framework v2.1 - Professional Logger
Ultra-Organized Architecture - Advanced Logging System

Features:
- Multi-level logging with rotation
- Structured logging with metadata
- Real-time log streaming
- Performance metrics
- Module-specific logging
- Session-based log tracking
"""

import logging
import logging.handlers
import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import queue
import threading


class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: datetime
    level: LogLevel
    message: str
    module: str
    session_id: Optional[str] = None
    operation_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.value,
            'message': self.message,
            'module': self.module,
            'session_id': self.session_id,
            'operation_id': self.operation_id,
            'metadata': self.metadata or {}
        }


class LogFormatter(logging.Formatter):
    """Custom log formatter with colors"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        """Format log record with colors"""
        # Get color for level
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Format message
        formatted = f"{timestamp} | {color}{record.levelname:8s}{reset} | {record.name} | {record.getMessage()}"
        
        # Add metadata if present
        if hasattr(record, 'metadata') and record.metadata:
            metadata_str = json.dumps(record.metadata, separators=(',', ':'))
            formatted += f" | {metadata_str}"
        
        return formatted


class WWYVQLogger:
    """
    Professional logging system for WWYVQ v2.1
    
    Features:
    - Multi-level logging with rotation
    - Structured logging with metadata
    - Real-time log streaming
    - Performance metrics
    - Module-specific logging
    - Session-based tracking
    """
    
    def __init__(self, config_manager):
        """
        Initialize logger
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.config = config_manager.get_config().logging
        
        # Initialize components
        self.log_entries: List[LogEntry] = []
        self.log_queue = queue.Queue()
        self.log_listeners: List[callable] = []
        
        # Setup logging
        self._setup_logging()
        
        # Start background log processing
        self._start_log_processor()
        
        # Create module-specific loggers
        self.module_loggers = {}
        
        print("✅ WWYVQ Logger v2.1 initialized")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory
        log_path = Path(self.config.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        self.root_logger = logging.getLogger('wwyvq_v2.1')
        self.root_logger.setLevel(getattr(logging, self.config.level))
        
        # Remove existing handlers
        self.root_logger.handlers.clear()
        
        # Console handler
        if self.config.console_logging:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(LogFormatter())
            self.root_logger.addHandler(console_handler)
        
        # File handler with rotation
        if self.config.file_logging:
            file_handler = logging.handlers.RotatingFileHandler(
                self.config.log_file,
                maxBytes=self.config.max_log_size,
                backupCount=self.config.backup_count
            )
            
            # File formatter (no colors)
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)8s | %(name)s | %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.root_logger.addHandler(file_handler)
        
        # Prevent propagation to root logger
        self.root_logger.propagate = False
    
    def _start_log_processor(self):
        """Start background log processor"""
        def process_logs():
            while True:
                try:
                    entry = self.log_queue.get(timeout=1)
                    if entry is None:  # Shutdown signal
                        break
                    
                    # Store entry
                    self.log_entries.append(entry)
                    
                    # Limit stored entries
                    if len(self.log_entries) > 10000:
                        self.log_entries = self.log_entries[-5000:]
                    
                    # Notify listeners
                    for listener in self.log_listeners:
                        try:
                            listener(entry)
                        except Exception as e:
                            print(f"Log listener error: {e}")
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Log processor error: {e}")
        
        self.log_thread = threading.Thread(target=process_logs, daemon=True)
        self.log_thread.start()
    
    def get_module_logger(self, module_name: str) -> logging.Logger:
        """Get module-specific logger"""
        if module_name not in self.module_loggers:
            logger = logging.getLogger(f'wwyvq_v2.1.{module_name}')
            logger.setLevel(getattr(logging, self.config.level))
            self.module_loggers[module_name] = logger
        
        return self.module_loggers[module_name]
    
    def debug(self, message: str, module: str = "core", session_id: Optional[str] = None, 
              operation_id: Optional[str] = None, **kwargs):
        """Log debug message"""
        self._log(LogLevel.DEBUG, message, module, session_id, operation_id, kwargs)
    
    def info(self, message: str, module: str = "core", session_id: Optional[str] = None,
             operation_id: Optional[str] = None, **kwargs):
        """Log info message"""
        self._log(LogLevel.INFO, message, module, session_id, operation_id, kwargs)
    
    def warning(self, message: str, module: str = "core", session_id: Optional[str] = None,
                operation_id: Optional[str] = None, **kwargs):
        """Log warning message"""
        self._log(LogLevel.WARNING, message, module, session_id, operation_id, kwargs)
    
    def error(self, message: str, module: str = "core", session_id: Optional[str] = None,
              operation_id: Optional[str] = None, **kwargs):
        """Log error message"""
        self._log(LogLevel.ERROR, message, module, session_id, operation_id, kwargs)
    
    def critical(self, message: str, module: str = "core", session_id: Optional[str] = None,
                 operation_id: Optional[str] = None, **kwargs):
        """Log critical message"""
        self._log(LogLevel.CRITICAL, message, module, session_id, operation_id, kwargs)
    
    def _log(self, level: LogLevel, message: str, module: str, session_id: Optional[str],
             operation_id: Optional[str], metadata: Dict[str, Any]):
        """Internal logging method"""
        # Create log entry
        entry = LogEntry(
            timestamp=datetime.utcnow(),
            level=level,
            message=message,
            module=module,
            session_id=session_id,
            operation_id=operation_id,
            metadata=metadata
        )
        
        # Queue for processing
        self.log_queue.put(entry)
        
        # Log to Python logger
        logger = self.get_module_logger(module)
        log_level = getattr(logging, level.value)
        
        # Format message with context
        formatted_message = self._format_log_message(message, session_id, operation_id, metadata)
        
        # Log with metadata as extra
        logger.log(log_level, formatted_message, extra={'metadata': metadata})
    
    def _format_log_message(self, message: str, session_id: Optional[str], 
                           operation_id: Optional[str], metadata: Dict[str, Any]) -> str:
        """Format log message with context"""
        formatted = message
        
        # Add session context
        if session_id:
            formatted += f" [Session: {session_id}]"
        
        # Add operation context
        if operation_id:
            formatted += f" [Op: {operation_id}]"
        
        return formatted
    
    def add_log_listener(self, listener: callable):
        """Add real-time log listener"""
        self.log_listeners.append(listener)
    
    def remove_log_listener(self, listener: callable):
        """Remove log listener"""
        if listener in self.log_listeners:
            self.log_listeners.remove(listener)
    
    def search_logs(self, query: str = None, level: Optional[LogLevel] = None,
                   module: Optional[str] = None, session_id: Optional[str] = None,
                   operation_id: Optional[str] = None, limit: int = 100) -> List[LogEntry]:
        """Search log entries"""
        results = []
        
        for entry in reversed(self.log_entries):
            # Apply filters
            if level and entry.level != level:
                continue
            
            if module and entry.module != module:
                continue
            
            if session_id and entry.session_id != session_id:
                continue
            
            if operation_id and entry.operation_id != operation_id:
                continue
            
            # Search in message
            if query:
                query_lower = query.lower()
                if query_lower not in entry.message.lower():
                    continue
            
            results.append(entry)
            
            # Limit results
            if len(results) >= limit:
                break
        
        return results
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get logging statistics"""
        stats = {
            'total_entries': len(self.log_entries),
            'by_level': {},
            'by_module': {},
            'by_session': {},
            'recent_activity': 0
        }
        
        # Calculate statistics
        one_hour_ago = datetime.utcnow().timestamp() - 3600
        
        for entry in self.log_entries:
            # By level
            level_name = entry.level.value
            stats['by_level'][level_name] = stats['by_level'].get(level_name, 0) + 1
            
            # By module
            stats['by_module'][entry.module] = stats['by_module'].get(entry.module, 0) + 1
            
            # By session
            if entry.session_id:
                stats['by_session'][entry.session_id] = stats['by_session'].get(entry.session_id, 0) + 1
            
            # Recent activity
            if entry.timestamp.timestamp() > one_hour_ago:
                stats['recent_activity'] += 1
        
        return stats
    
    def export_logs(self, format: str = 'json', output_path: Optional[str] = None) -> str:
        """Export logs to file"""
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f'logs_export_{timestamp}.{format}'
        
        try:
            if format.lower() == 'json':
                with open(output_path, 'w') as f:
                    json.dump([entry.to_dict() for entry in self.log_entries], f, indent=2)
            
            elif format.lower() == 'csv':
                import csv
                with open(output_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['timestamp', 'level', 'module', 'session_id', 'operation_id', 'message'])
                    for entry in self.log_entries:
                        writer.writerow([
                            entry.timestamp.isoformat(),
                            entry.level.value,
                            entry.module,
                            entry.session_id,
                            entry.operation_id,
                            entry.message
                        ])
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            return output_path
            
        except Exception as e:
            self.error(f"Failed to export logs: {e}")
            raise
    
    def get_recent_logs(self, limit: int = 50) -> List[LogEntry]:
        """Get recent log entries"""
        return list(reversed(self.log_entries[-limit:]))
    
    def clear_logs(self):
        """Clear all log entries"""
        self.log_entries.clear()
        self.info("Log entries cleared")
    
    def get_log_stream(self) -> asyncio.Queue:
        """Get async log stream"""
        log_stream = asyncio.Queue()
        
        def stream_listener(entry):
            try:
                asyncio.create_task(log_stream.put(entry))
            except:
                pass
        
        self.add_log_listener(stream_listener)
        return log_stream
    
    def shutdown(self):
        """Shutdown logger"""
        self.info("Shutting down logger...")
        
        # Stop log processor
        self.log_queue.put(None)
        
        # Wait for thread
        if hasattr(self, 'log_thread') and self.log_thread.is_alive():
            self.log_thread.join(timeout=1)
        
        # Close handlers
        for handler in self.root_logger.handlers:
            handler.close()
            
        print("✅ Logger shutdown completed")