#!/usr/bin/env python3
"""
WWYVQ v2.1 Configuration Manager
Centralized configuration management for all modules

Author: wKayaa
Date: 2025-01-07
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum


class ConfigFormat(Enum):
    """Supported configuration formats"""
    JSON = "json"
    YAML = "yaml"


@dataclass
class ExploitConfig:
    """Exploitation module configuration"""
    enabled: bool = True
    kubernetes_focus: bool = True
    max_concurrent_clusters: int = 50
    timeout_per_operation: int = 30
    stealth_mode: bool = False
    rate_limit_delay: float = 0.1
    cidr_expansion: bool = True
    paths_to_scan: int = 2500


@dataclass
class ValidatorConfig:
    """Validator module configuration"""
    enabled: bool = True
    real_time_validation: bool = True
    confidence_threshold: float = 75.0
    validate_aws: bool = True
    validate_smtp: bool = True
    validate_sendgrid: bool = True
    validate_mailgun: bool = True
    validate_twilio: bool = True
    batch_size: int = 10


@dataclass
class NotifierConfig:
    """Notifier module configuration"""
    enabled: bool = True
    telegram_enabled: bool = False
    discord_enabled: bool = False
    telegram_token: str = ""
    telegram_chat_id: str = ""
    discord_webhook_url: str = ""
    rate_limit_delay: float = 1.0
    professional_format: bool = True
    valid_credentials_only: bool = True


@dataclass
class ExporterConfig:
    """Exporter module configuration"""
    enabled: bool = True
    json_export: bool = True
    csv_export: bool = True
    yaml_export: bool = False
    output_directory: str = "./results"
    create_host_file: bool = True
    compression: bool = False
    encryption: bool = False


@dataclass
class SystemConfig:
    """System-wide configuration"""
    scan_name: str = "WWYVQ_Scan"
    operator_name: str = "wKayaa"
    job_timeout: int = 3600
    max_concurrent_jobs: int = 5
    log_level: str = "INFO"
    debug_mode: bool = False
    memory_limit_mb: int = 2048
    temp_directory: str = "/tmp/wwyvq"


@dataclass
class WWYVQConfig:
    """Complete WWYVQ configuration"""
    version: str = "2.1"
    exploit: ExploitConfig = field(default_factory=ExploitConfig)
    validator: ValidatorConfig = field(default_factory=ValidatorConfig)
    notifier: NotifierConfig = field(default_factory=NotifierConfig)
    exporter: ExporterConfig = field(default_factory=ExporterConfig)
    system: SystemConfig = field(default_factory=SystemConfig)


class ConfigurationManager:
    """
    Centralized configuration management for WWYVQ v2.1
    Supports JSON and YAML configuration files
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager"""
        self.config_path = Path(config_path) if config_path else Path("./config/wwyvq.yaml")
        self.config = WWYVQConfig()
        self.logger = logging.getLogger("ConfigManager")
        
        # Create config directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def load_config(self) -> bool:
        """Load configuration from file"""
        try:
            if not self.config_path.exists():
                self.logger.info(f"Configuration file not found at {self.config_path}")
                self.logger.info("Creating default configuration...")
                await self.save_config()
                return True
            
            # Determine format from file extension
            if self.config_path.suffix.lower() == '.json':
                format_type = ConfigFormat.JSON
            elif self.config_path.suffix.lower() in ['.yaml', '.yml']:
                format_type = ConfigFormat.YAML
            else:
                self.logger.error(f"Unsupported configuration format: {self.config_path.suffix}")
                return False
            
            # Load configuration
            with open(self.config_path, 'r') as f:
                if format_type == ConfigFormat.JSON:
                    config_data = json.load(f)
                else:
                    config_data = yaml.safe_load(f)
            
            # Update configuration
            self._update_from_dict(config_data)
            
            self.logger.info(f"✅ Configuration loaded from {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load configuration: {e}")
            return False
    
    async def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            # Convert to dictionary
            config_dict = self._to_dict()
            
            # Determine format from file extension
            if self.config_path.suffix.lower() == '.json':
                format_type = ConfigFormat.JSON
            elif self.config_path.suffix.lower() in ['.yaml', '.yml']:
                format_type = ConfigFormat.YAML
            else:
                # Default to YAML
                format_type = ConfigFormat.YAML
                self.config_path = self.config_path.with_suffix('.yaml')
            
            # Save configuration
            with open(self.config_path, 'w') as f:
                if format_type == ConfigFormat.JSON:
                    json.dump(config_dict, f, indent=2)
                else:
                    yaml.safe_dump(config_dict, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"✅ Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save configuration: {e}")
            return False
    
    def _update_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Update configuration from dictionary"""
        try:
            # Update exploit configuration
            if 'exploit' in config_data:
                for key, value in config_data['exploit'].items():
                    if hasattr(self.config.exploit, key):
                        setattr(self.config.exploit, key, value)
            
            # Update validator configuration
            if 'validator' in config_data:
                for key, value in config_data['validator'].items():
                    if hasattr(self.config.validator, key):
                        setattr(self.config.validator, key, value)
            
            # Update notifier configuration
            if 'notifier' in config_data:
                for key, value in config_data['notifier'].items():
                    if hasattr(self.config.notifier, key):
                        setattr(self.config.notifier, key, value)
            
            # Update exporter configuration
            if 'exporter' in config_data:
                for key, value in config_data['exporter'].items():
                    if hasattr(self.config.exporter, key):
                        setattr(self.config.exporter, key, value)
            
            # Update system configuration
            if 'system' in config_data:
                for key, value in config_data['system'].items():
                    if hasattr(self.config.system, key):
                        setattr(self.config.system, key, value)
            
            # Update version
            if 'version' in config_data:
                self.config.version = config_data['version']
                
        except Exception as e:
            self.logger.error(f"❌ Failed to update configuration: {e}")
    
    def _to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'version': self.config.version,
            'exploit': asdict(self.config.exploit),
            'validator': asdict(self.config.validator),
            'notifier': asdict(self.config.notifier),
            'exporter': asdict(self.config.exporter),
            'system': asdict(self.config.system)
        }
    
    def get_config(self) -> WWYVQConfig:
        """Get current configuration"""
        return self.config
    
    def update_config(self, section: str, key: str, value: Any) -> bool:
        """Update specific configuration value"""
        try:
            section_obj = getattr(self.config, section)
            if hasattr(section_obj, key):
                setattr(section_obj, key, value)
                self.logger.info(f"✅ Updated {section}.{key} = {value}")
                return True
            else:
                self.logger.error(f"❌ Unknown configuration key: {section}.{key}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to update configuration: {e}")
            return False
    
    def is_valid(self) -> bool:
        """Validate configuration"""
        try:
            # Check critical configurations
            if self.config.exploit.max_concurrent_clusters <= 0:
                self.logger.error("❌ Invalid exploit.max_concurrent_clusters")
                return False
            
            if self.config.validator.confidence_threshold < 0 or self.config.validator.confidence_threshold > 100:
                self.logger.error("❌ Invalid validator.confidence_threshold")
                return False
            
            if self.config.notifier.rate_limit_delay < 0:
                self.logger.error("❌ Invalid notifier.rate_limit_delay")
                return False
            
            if self.config.system.job_timeout <= 0:
                self.logger.error("❌ Invalid system.job_timeout")
                return False
            
            # Check notification settings if enabled
            if self.config.notifier.telegram_enabled:
                if not self.config.notifier.telegram_token:
                    self.logger.error("❌ Telegram enabled but no token provided")
                    return False
                if not self.config.notifier.telegram_chat_id:
                    self.logger.error("❌ Telegram enabled but no chat_id provided")
                    return False
            
            if self.config.notifier.discord_enabled:
                if not self.config.notifier.discord_webhook_url:
                    self.logger.error("❌ Discord enabled but no webhook URL provided")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Configuration validation failed: {e}")
            return False
    
    def create_sample_config(self, output_path: Optional[str] = None) -> bool:
        """Create a sample configuration file"""
        try:
            if output_path:
                original_path = self.config_path
                self.config_path = Path(output_path)
            
            # Create sample configuration with comments
            sample_config = {
                'version': '2.1',
                'exploit': {
                    'enabled': True,
                    'kubernetes_focus': True,
                    'max_concurrent_clusters': 50,
                    'timeout_per_operation': 30,
                    'stealth_mode': False,
                    'rate_limit_delay': 0.1,
                    'cidr_expansion': True,
                    'paths_to_scan': 2500
                },
                'validator': {
                    'enabled': True,
                    'real_time_validation': True,
                    'confidence_threshold': 75.0,
                    'validate_aws': True,
                    'validate_smtp': True,
                    'validate_sendgrid': True,
                    'validate_mailgun': True,
                    'validate_twilio': True,
                    'batch_size': 10
                },
                'notifier': {
                    'enabled': True,
                    'telegram_enabled': False,
                    'discord_enabled': False,
                    'telegram_token': 'YOUR_TELEGRAM_BOT_TOKEN',
                    'telegram_chat_id': 'YOUR_TELEGRAM_CHAT_ID',
                    'discord_webhook_url': 'YOUR_DISCORD_WEBHOOK_URL',
                    'rate_limit_delay': 1.0,
                    'professional_format': True,
                    'valid_credentials_only': True
                },
                'exporter': {
                    'enabled': True,
                    'json_export': True,
                    'csv_export': True,
                    'yaml_export': False,
                    'output_directory': './results',
                    'create_host_file': True,
                    'compression': False,
                    'encryption': False
                },
                'system': {
                    'scan_name': 'WWYVQ_Scan',
                    'operator_name': 'wKayaa',
                    'job_timeout': 3600,
                    'max_concurrent_jobs': 5,
                    'log_level': 'INFO',
                    'debug_mode': False,
                    'memory_limit_mb': 2048,
                    'temp_directory': '/tmp/wwyvq'
                }
            }
            
            # Save sample configuration
            with open(self.config_path, 'w') as f:
                yaml.safe_dump(sample_config, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"✅ Sample configuration created at {self.config_path}")
            
            if output_path:
                self.config_path = original_path
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create sample configuration: {e}")
            return False
    
    def get_module_config(self, module_type: str) -> Optional[Any]:
        """Get configuration for a specific module"""
        try:
            return getattr(self.config, module_type)
        except AttributeError:
            self.logger.error(f"❌ Unknown module type: {module_type}")
            return None