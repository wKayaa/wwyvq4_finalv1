#!/usr/bin/env python3
"""
Enhanced Monitoring Dashboard and Configuration Management
Real-time monitoring, searchable logs, and comprehensive configuration
Author: wKayaa | Enhanced Version | 2025-01-28
"""

import asyncio
import json
import logging
import os
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
import threading
import time
from collections import defaultdict, deque

from enhanced_security_monitor import FilterConfig, SeverityLevel, CredentialType
from enhanced_telegram_alerts import AlertConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MonitoringConfig:
    """Configuration for monitoring and dashboard"""
    log_retention_days: int = 30
    max_log_entries: int = 10000
    update_interval_seconds: int = 5
    enable_real_time_updates: bool = True
    export_logs_format: str = "json"  # json, csv, yaml
    dashboard_port: int = 8080
    enable_web_dashboard: bool = True
    enable_api_endpoints: bool = True

@dataclass
class SystemConfig:
    """Master configuration combining all subsystems"""
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    filtering: FilterConfig = field(default_factory=FilterConfig)
    alerting: AlertConfig = field(default_factory=AlertConfig)
    
    # Global settings
    scan_name: str = field(default_factory=lambda: f"scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
    operator_name: str = "wKayaa"
    enable_detailed_logging: bool = True
    output_directory: str = "./security_scan_results"
    config_file_path: str = "./security_monitor_config.yaml"

class SearchableLogManager:
    """Advanced log management with search capabilities"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.logs = deque(maxlen=config.max_log_entries)
        self.log_index = defaultdict(list)  # For fast searching
        self.stats = {
            'total_entries': 0,
            'entries_by_level': defaultdict(int),
            'entries_by_hour': defaultdict(int),
            'start_time': datetime.utcnow()
        }
        self._lock = threading.Lock()
    
    def add_log_entry(self, level: str, message: str, category: str = "general", 
                     metadata: Optional[Dict[str, Any]] = None):
        """Add searchable log entry"""
        with self._lock:
            timestamp = datetime.utcnow()
            
            entry = {
                'timestamp': timestamp.isoformat(),
                'level': level.upper(),
                'message': message,
                'category': category,
                'metadata': metadata or {},
                'id': self.stats['total_entries']
            }
            
            self.logs.append(entry)
            
            # Update search index
            words = message.lower().split()
            for word in words:
                if len(word) > 2:  # Skip very short words
                    self.log_index[word].append(entry['id'])
            
            # Update statistics
            self.stats['total_entries'] += 1
            self.stats['entries_by_level'][level.upper()] += 1
            self.stats['entries_by_hour'][timestamp.strftime('%Y-%m-%d %H')] += 1
    
    def search_logs(self, query: str, limit: int = 100, level_filter: Optional[str] = None,
                   category_filter: Optional[str] = None, time_range_hours: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search logs with various filters"""
        with self._lock:
            results = []
            query_lower = query.lower()
            
            # Time range filter
            time_cutoff = None
            if time_range_hours:
                time_cutoff = datetime.utcnow() - timedelta(hours=time_range_hours)
            
            for entry in reversed(self.logs):  # Most recent first
                # Time range check
                if time_cutoff:
                    entry_time = datetime.fromisoformat(entry['timestamp'])
                    if entry_time < time_cutoff:
                        continue
                
                # Level filter
                if level_filter and entry['level'] != level_filter.upper():
                    continue
                
                # Category filter
                if category_filter and entry['category'] != category_filter:
                    continue
                
                # Text search
                if (query_lower in entry['message'].lower() or
                    query_lower in entry['category'].lower() or
                    any(query_lower in str(v).lower() for v in entry['metadata'].values())):
                    
                    results.append(entry)
                    
                    if len(results) >= limit:
                        break
            
            return results
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get comprehensive log statistics"""
        with self._lock:
            uptime = datetime.utcnow() - self.stats['start_time']
            
            # Recent activity (last hour)
            current_hour = datetime.utcnow().strftime('%Y-%m-%d %H')
            recent_activity = self.stats['entries_by_hour'].get(current_hour, 0)
            
            return {
                'total_entries': self.stats['total_entries'],
                'current_buffer_size': len(self.logs),
                'max_buffer_size': self.config.max_log_entries,
                'uptime': str(uptime),
                'entries_by_level': dict(self.stats['entries_by_level']),
                'recent_activity_count': recent_activity,
                'indexed_words': len(self.log_index),
                'retention_hours': self.config.log_retention_days * 24
            }
    
    def export_logs(self, format_type: str = "json", filter_options: Optional[Dict] = None) -> str:
        """Export logs in specified format"""
        with self._lock:
            # Apply filters if specified
            logs_to_export = list(self.logs)
            
            if filter_options:
                if filter_options.get('level'):
                    logs_to_export = [log for log in logs_to_export 
                                    if log['level'] == filter_options['level'].upper()]
                
                if filter_options.get('category'):
                    logs_to_export = [log for log in logs_to_export 
                                    if log['category'] == filter_options['category']]
                
                if filter_options.get('hours'):
                    cutoff = datetime.utcnow() - timedelta(hours=filter_options['hours'])
                    logs_to_export = [log for log in logs_to_export 
                                    if datetime.fromisoformat(log['timestamp']) >= cutoff]
            
            # Export in specified format
            if format_type.lower() == "json":
                return json.dumps(logs_to_export, indent=2)
            elif format_type.lower() == "yaml":
                return yaml.dump(logs_to_export, default_flow_style=False)
            elif format_type.lower() == "csv":
                # Simple CSV export
                if not logs_to_export:
                    return "timestamp,level,category,message\n"
                
                csv_lines = ["timestamp,level,category,message"]
                for log in logs_to_export:
                    # Escape commas and quotes in message
                    message = log['message'].replace('"', '""')
                    if ',' in message:
                        message = f'"{message}"'
                    
                    csv_lines.append(f"{log['timestamp']},{log['level']},{log['category']},{message}")
                
                return "\n".join(csv_lines)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")

class RealTimeMonitor:
    """Real-time monitoring system with live updates"""
    
    def __init__(self, config: MonitoringConfig, log_manager: SearchableLogManager):
        self.config = config
        self.log_manager = log_manager
        self.active_scans = {}
        self.system_metrics = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'active_connections': 0,
            'scan_queue_size': 0
        }
        self.alert_metrics = {
            'alerts_per_minute': 0,
            'last_alert_time': None,
            'total_alerts_today': 0
        }
        self.running = False
        self._monitor_task = None
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        if self.running:
            return
        
        self.running = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        self.log_manager.add_log_entry("INFO", "Real-time monitoring started", "monitor")
        logger.info("Real-time monitoring started")
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        if not self.running:
            return
        
        self.running = False
        if self._monitor_task:
            self._monitor_task.cancel()
        
        self.log_manager.add_log_entry("INFO", "Real-time monitoring stopped", "monitor")
        logger.info("Real-time monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Update system metrics
                await self._update_system_metrics()
                
                # Update alert metrics
                self._update_alert_metrics()
                
                # Log periodic status
                if datetime.utcnow().minute % 5 == 0:  # Every 5 minutes
                    self._log_status_update()
                
                await asyncio.sleep(self.config.update_interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.log_manager.add_log_entry("ERROR", f"Monitoring loop error: {e}", "monitor")
                await asyncio.sleep(self.config.update_interval_seconds)
    
    async def _update_system_metrics(self):
        """Update system performance metrics"""
        try:
            # Try to get system metrics if psutil is available
            try:
                import psutil
                self.system_metrics['cpu_usage'] = psutil.cpu_percent()
                self.system_metrics['memory_usage'] = psutil.virtual_memory().percent
            except ImportError:
                # Fallback to basic metrics
                pass
            
            # Update scan-related metrics
            self.system_metrics['active_scans'] = len(self.active_scans)
            
        except Exception as e:
            logger.warning(f"Failed to update system metrics: {e}")
    
    def _update_alert_metrics(self):
        """Update alerting metrics"""
        # This would be called by the alerting system
        # For now, just maintain the structure
        pass
    
    def _log_status_update(self):
        """Log periodic status update"""
        status = {
            'active_scans': len(self.active_scans),
            'system_metrics': self.system_metrics,
            'alert_metrics': self.alert_metrics,
            'log_stats': self.log_manager.get_log_statistics()
        }
        
        self.log_manager.add_log_entry(
            "INFO", 
            "Periodic status update", 
            "monitor", 
            status
        )
    
    def register_scan(self, scan_id: str, scan_info: Dict[str, Any]):
        """Register a new scan for monitoring"""
        self.active_scans[scan_id] = {
            'start_time': datetime.utcnow(),
            'info': scan_info,
            'last_update': datetime.utcnow()
        }
        
        self.log_manager.add_log_entry(
            "INFO", 
            f"Scan registered: {scan_id}", 
            "scan", 
            scan_info
        )
    
    def update_scan_progress(self, scan_id: str, progress_info: Dict[str, Any]):
        """Update scan progress"""
        if scan_id in self.active_scans:
            self.active_scans[scan_id]['last_update'] = datetime.utcnow()
            self.active_scans[scan_id]['progress'] = progress_info
            
            self.log_manager.add_log_entry(
                "DEBUG", 
                f"Scan progress update: {scan_id}", 
                "scan", 
                progress_info
            )
    
    def complete_scan(self, scan_id: str, results: Dict[str, Any]):
        """Mark scan as completed"""
        if scan_id in self.active_scans:
            scan_duration = datetime.utcnow() - self.active_scans[scan_id]['start_time']
            
            completion_info = {
                'scan_id': scan_id,
                'duration': str(scan_duration),
                'results': results
            }
            
            self.log_manager.add_log_entry(
                "INFO", 
                f"Scan completed: {scan_id}", 
                "scan", 
                completion_info
            )
            
            del self.active_scans[scan_id]
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get real-time dashboard data"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'system_status': {
                'monitoring_active': self.running,
                'uptime': str(datetime.utcnow() - self.log_manager.stats['start_time']),
                'metrics': self.system_metrics
            },
            'active_scans': {
                scan_id: {
                    'duration': str(datetime.utcnow() - scan_data['start_time']),
                    'last_update': scan_data['last_update'].isoformat(),
                    'info': scan_data['info'],
                    'progress': scan_data.get('progress', {})
                }
                for scan_id, scan_data in self.active_scans.items()
            },
            'alert_metrics': self.alert_metrics,
            'log_summary': self.log_manager.get_log_statistics()
        }

class ConfigurationManager:
    """Comprehensive configuration management"""
    
    def __init__(self, config_path: str = "./security_monitor_config.yaml"):
        self.config_path = Path(config_path)
        self.config = SystemConfig()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                # Update configuration with loaded data
                if config_data:
                    self._update_config_from_dict(config_data)
                
                logger.info(f"Configuration loaded from {self.config_path}")
                
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
                logger.info("Using default configuration")
        else:
            logger.info("No configuration file found, using defaults")
            self.save_config()  # Create default config file
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]):
        """Update configuration from dictionary"""
        
        # Update monitoring config
        if 'monitoring' in config_data:
            monitoring_data = config_data['monitoring']
            for key, value in monitoring_data.items():
                if hasattr(self.config.monitoring, key):
                    setattr(self.config.monitoring, key, value)
        
        # Update filtering config
        if 'filtering' in config_data:
            filtering_data = config_data['filtering']
            for key, value in filtering_data.items():
                if hasattr(self.config.filtering, key):
                    if key in ['excluded_extensions', 'excluded_paths', 'test_keywords']:
                        setattr(self.config.filtering, key, set(value))
                    else:
                        setattr(self.config.filtering, key, value)
        
        # Update alerting config
        if 'alerting' in config_data:
            alerting_data = config_data['alerting']
            for key, value in alerting_data.items():
                if hasattr(self.config.alerting, key):
                    if key == 'alert_threshold':
                        setattr(self.config.alerting, key, SeverityLevel(value))
                    else:
                        setattr(self.config.alerting, key, value)
        
        # Update global settings
        for key, value in config_data.items():
            if key not in ['monitoring', 'filtering', 'alerting'] and hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            config_dict = self._config_to_dict()
            
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def _config_to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization"""
        config_dict = {
            'monitoring': asdict(self.config.monitoring),
            'filtering': asdict(self.config.filtering),
            'alerting': asdict(self.config.alerting),
            'scan_name': self.config.scan_name,
            'operator_name': self.config.operator_name,
            'enable_detailed_logging': self.config.enable_detailed_logging,
            'output_directory': self.config.output_directory,
            'config_file_path': self.config.config_file_path
        }
        
        # Convert sets to lists for YAML serialization
        config_dict['filtering']['excluded_extensions'] = list(self.config.filtering.excluded_extensions)
        config_dict['filtering']['excluded_paths'] = list(self.config.filtering.excluded_paths)
        config_dict['filtering']['test_keywords'] = list(self.config.filtering.test_keywords)
        
        # Convert enum to string
        config_dict['alerting']['alert_threshold'] = self.config.alerting.alert_threshold.value
        
        return config_dict
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration with new values"""
        self._update_config_from_dict(updates)
        self.save_config()
    
    def get_config(self) -> SystemConfig:
        """Get current configuration"""
        return self.config
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = SystemConfig()
        self.save_config()
        logger.info("Configuration reset to defaults")

# Export classes for use in other modules
__all__ = [
    'SearchableLogManager', 'RealTimeMonitor', 'ConfigurationManager',
    'MonitoringConfig', 'SystemConfig'
]

if __name__ == "__main__":
    print("🚀 Enhanced Monitoring Dashboard - wKayaa Production")