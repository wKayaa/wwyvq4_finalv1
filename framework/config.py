#!/usr/bin/env python3
"""
Configuration Management Module
Author: wKayaa
Date: 2025-06-24 17:02:05 UTC
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Configuration management for the framework"""
    
    def __init__(self, config_path: str = "framework_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_default_config()
        self.load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            "performance": {
                "max_threads": 500,
                "timeout_per_operation": 10,
                "max_concurrent_clusters": 100
            },
            "integrations": {
                "telegram_enabled": False,
                "telegram_token": "",
                "telegram_chat_id": "",
                "web_interface_enabled": False,
                "api_server_enabled": False
            },
            "network": {
                "web_interface_port": 5000,
                "api_server_port": 8080,
                "bind_address": "0.0.0.0"
            },
            "logging": {
                "level": "INFO",
                "file": "framework.log",
                "console": True
            },
            "exploitation": {
                "mode": "aggressive",
                "scan_only": False,
                "mail_focus": False
            }
        }
    
    def load_config(self) -> bool:
        """Load configuration from file"""
        if not self.config_path.exists():
            self.save_config()
            return True
            
        try:
            with open(self.config_path, 'r') as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    self._merge_config(file_config)
            return True
        except Exception as e:
            print(f"⚠️ Failed to load config from {self.config_path}: {e}")
            return False
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            return True
        except Exception as e:
            print(f"⚠️ Failed to save config to {self.config_path}: {e}")
            return False
    
    def _merge_config(self, new_config: Dict[str, Any]):
        """Merge new configuration with existing"""
        def merge_dict(base: Dict, update: Dict):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
        
        merge_dict(self.config, new_config)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'performance.max_threads')"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> bool:
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        return self.save_config()
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """Update configuration with new values"""
        self._merge_config(updates)
        return self.save_config()