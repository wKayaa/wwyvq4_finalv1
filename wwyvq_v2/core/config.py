#!/usr/bin/env python3
"""
WWYVQ Framework v2 - Configuration Manager
Author: wKayaa
Date: 2025-01-15

Gestionnaire de configuration centralisé avec support YAML/JSON.
"""

import json
import yaml
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime


@dataclass
class CoreConfig:
    """Configuration du moteur principal"""
    session_id: str = "auto"
    max_concurrent: int = 100
    timeout: int = 30
    retry_attempts: int = 3
    safe_mode: bool = True
    debug_mode: bool = False


@dataclass
class ModuleConfig:
    """Configuration des modules"""
    exploit: Dict[str, Any] = field(default_factory=lambda: {
        'enabled': True,
        'stealth_mode': False,
        'max_pods': 10
    })
    scanner: Dict[str, Any] = field(default_factory=lambda: {
        'enabled': True,
        'port_range': [80, 443, 6443, 8080, 8443],
        'timeout': 10
    })
    validator: Dict[str, Any] = field(default_factory=lambda: {
        'enabled': True,
        'api_timeout': 10,
        'max_retries': 3
    })
    notifier: Dict[str, Any] = field(default_factory=lambda: {
        'telegram': {
            'enabled': False,
            'token': '',
            'chat_id': ''
        },
        'discord': {
            'enabled': False,
            'webhook_url': ''
        }
    })


@dataclass
class TargetConfig:
    """Configuration des cibles"""
    cidr_expansion: bool = True
    max_ips_per_cidr: int = 1000
    default_ports: List[int] = field(default_factory=lambda: [6443, 8443, 8080])
    timeout_per_target: int = 10


@dataclass
class LoggingConfig:
    """Configuration du logging"""
    level: str = "INFO"
    file_enabled: bool = True
    file_path: str = "logs/wwyvq.log"
    max_file_size: int = 10_000_000  # 10MB
    backup_count: int = 5
    console_enabled: bool = True


@dataclass
class SecurityConfig:
    """Configuration de sécurité"""
    encryption_enabled: bool = True
    audit_logging: bool = True
    session_timeout: int = 3600
    safe_mode_restrictions: List[str] = field(default_factory=lambda: [
        'no_pod_deployment',
        'no_privilege_escalation',
        'readonly_operations'
    ])


@dataclass
class WWYVQConfig:
    """Configuration principale du framework"""
    core: CoreConfig = field(default_factory=CoreConfig)
    modules: ModuleConfig = field(default_factory=ModuleConfig)
    targets: TargetConfig = field(default_factory=TargetConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    version: str = "2.0.0"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class ConfigurationManager:
    """
    Gestionnaire de configuration centralisé
    
    Responsabilités:
    - Chargement/sauvegarde des configurations
    - Validation des paramètres
    - Gestion des profils (dev, prod, test)
    - Hot reload des configurations
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le gestionnaire de configuration
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config_path = Path(config_path) if config_path else Path("configs/default.yaml")
        self.config = WWYVQConfig()
        self.watchers = []  # Pour le hot reload
        
        # Création du répertoire de configuration si nécessaire
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Chargement de la configuration
        self._load_config()
    
    def _load_config(self):
        """Charge la configuration depuis le fichier"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    if self.config_path.suffix.lower() == '.yaml':
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                
                if config_data:
                    self._update_config_from_dict(config_data)
                
                print(f"✅ Configuration loaded from {self.config_path}")
                
            except Exception as e:
                print(f"❌ Failed to load configuration: {e}")
                print("⚠️ Using default configuration")
                self._save_default_config()
        else:
            print(f"⚠️ No configuration file found at {self.config_path}")
            print("📝 Creating default configuration...")
            self._save_default_config()
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]):
        """Met à jour la configuration à partir d'un dictionnaire"""
        # Mise à jour du core
        if 'core' in config_data:
            core_data = config_data['core']
            for key, value in core_data.items():
                if hasattr(self.config.core, key):
                    setattr(self.config.core, key, value)
        
        # Mise à jour des modules
        if 'modules' in config_data:
            modules_data = config_data['modules']
            for module_name, module_config in modules_data.items():
                if hasattr(self.config.modules, module_name):
                    setattr(self.config.modules, module_name, module_config)
        
        # Mise à jour des targets
        if 'targets' in config_data:
            targets_data = config_data['targets']
            for key, value in targets_data.items():
                if hasattr(self.config.targets, key):
                    setattr(self.config.targets, key, value)
        
        # Mise à jour du logging
        if 'logging' in config_data:
            logging_data = config_data['logging']
            for key, value in logging_data.items():
                if hasattr(self.config.logging, key):
                    setattr(self.config.logging, key, value)
        
        # Mise à jour de la sécurité
        if 'security' in config_data:
            security_data = config_data['security']
            for key, value in security_data.items():
                if hasattr(self.config.security, key):
                    setattr(self.config.security, key, value)
    
    def _save_default_config(self):
        """Sauvegarde la configuration par défaut"""
        try:
            config_dict = self._config_to_dict()
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                if self.config_path.suffix.lower() == '.yaml':
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Default configuration saved to {self.config_path}")
            
        except Exception as e:
            print(f"❌ Failed to save default configuration: {e}")
    
    def _config_to_dict(self) -> Dict[str, Any]:
        """Convertit la configuration en dictionnaire"""
        return {
            'version': self.config.version,
            'created_at': self.config.created_at,
            'core': {
                'session_id': self.config.core.session_id,
                'max_concurrent': self.config.core.max_concurrent,
                'timeout': self.config.core.timeout,
                'retry_attempts': self.config.core.retry_attempts,
                'safe_mode': self.config.core.safe_mode,
                'debug_mode': self.config.core.debug_mode
            },
            'modules': {
                'exploit': self.config.modules.exploit,
                'scanner': self.config.modules.scanner,
                'validator': self.config.modules.validator,
                'notifier': self.config.modules.notifier
            },
            'targets': {
                'cidr_expansion': self.config.targets.cidr_expansion,
                'max_ips_per_cidr': self.config.targets.max_ips_per_cidr,
                'default_ports': self.config.targets.default_ports,
                'timeout_per_target': self.config.targets.timeout_per_target
            },
            'logging': {
                'level': self.config.logging.level,
                'file_enabled': self.config.logging.file_enabled,
                'file_path': self.config.logging.file_path,
                'max_file_size': self.config.logging.max_file_size,
                'backup_count': self.config.logging.backup_count,
                'console_enabled': self.config.logging.console_enabled
            },
            'security': {
                'encryption_enabled': self.config.security.encryption_enabled,
                'audit_logging': self.config.security.audit_logging,
                'session_timeout': self.config.security.session_timeout,
                'safe_mode_restrictions': self.config.security.safe_mode_restrictions
            }
        }
    
    def get_config(self) -> WWYVQConfig:
        """
        Récupère la configuration actuelle
        
        Returns:
            WWYVQConfig: Configuration actuelle
        """
        return self.config
    
    def update_config(self, updates: Dict[str, Any]):
        """
        Met à jour la configuration avec de nouvelles valeurs
        
        Args:
            updates: Dictionnaire des mises à jour
        """
        self._update_config_from_dict(updates)
        self.save_config()
    
    def save_config(self):
        """Sauvegarde la configuration actuelle"""
        try:
            config_dict = self._config_to_dict()
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                if self.config_path.suffix.lower() == '.yaml':
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Configuration saved to {self.config_path}")
            
        except Exception as e:
            print(f"❌ Failed to save configuration: {e}")
    
    def load_profile(self, profile_name: str):
        """
        Charge un profil de configuration spécifique
        
        Args:
            profile_name: Nom du profil (dev, prod, test, etc.)
        """
        profile_path = self.config_path.parent / f"{profile_name}.yaml"
        
        if profile_path.exists():
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                
                if config_data:
                    self._update_config_from_dict(config_data)
                
                print(f"✅ Profile '{profile_name}' loaded")
                
            except Exception as e:
                print(f"❌ Failed to load profile '{profile_name}': {e}")
        else:
            print(f"⚠️ Profile '{profile_name}' not found at {profile_path}")
    
    def create_profile(self, profile_name: str, config_overrides: Dict[str, Any]):
        """
        Crée un nouveau profil de configuration
        
        Args:
            profile_name: Nom du profil
            config_overrides: Surcharges de configuration
        """
        profile_path = self.config_path.parent / f"{profile_name}.yaml"
        
        try:
            # Partir de la configuration par défaut
            base_config = self._config_to_dict()
            
            # Appliquer les surcharges
            def deep_update(base_dict, update_dict):
                for key, value in update_dict.items():
                    if isinstance(value, dict) and key in base_dict:
                        deep_update(base_dict[key], value)
                    else:
                        base_dict[key] = value
            
            deep_update(base_config, config_overrides)
            
            # Sauvegarder le profil
            with open(profile_path, 'w', encoding='utf-8') as f:
                yaml.dump(base_config, f, default_flow_style=False, indent=2)
            
            print(f"✅ Profile '{profile_name}' created at {profile_path}")
            
        except Exception as e:
            print(f"❌ Failed to create profile '{profile_name}': {e}")
    
    def validate_config(self) -> bool:
        """
        Valide la configuration actuelle
        
        Returns:
            bool: True si la configuration est valide
        """
        try:
            # Validation des paramètres critiques
            if self.config.core.max_concurrent <= 0:
                print("❌ Invalid max_concurrent: must be > 0")
                return False
            
            if self.config.core.timeout <= 0:
                print("❌ Invalid timeout: must be > 0")
                return False
            
            if self.config.core.retry_attempts < 0:
                print("❌ Invalid retry_attempts: must be >= 0")
                return False
            
            # Validation des ports
            if not self.config.targets.default_ports:
                print("❌ No default ports configured")
                return False
            
            # Validation du logging
            if self.config.logging.level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
                print(f"❌ Invalid logging level: {self.config.logging.level}")
                return False
            
            print("✅ Configuration validation passed")
            return True
            
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            return False
    
    def reset_to_defaults(self):
        """Remet la configuration aux valeurs par défaut"""
        self.config = WWYVQConfig()
        self.save_config()
        print("🔄 Configuration reset to defaults")
    
    def get_module_config(self, module_name: str) -> Optional[Dict[str, Any]]:
        """
        Récupère la configuration d'un module spécifique
        
        Args:
            module_name: Nom du module
            
        Returns:
            Dict ou None si le module n'existe pas
        """
        return getattr(self.config.modules, module_name, None)
    
    def is_safe_mode(self) -> bool:
        """
        Vérifie si le mode sécurisé est activé
        
        Returns:
            bool: True si le mode sécurisé est activé
        """
        return self.config.core.safe_mode
    
    def get_restrictions(self) -> List[str]:
        """
        Récupère les restrictions du mode sécurisé
        
        Returns:
            List des restrictions actives
        """
        return self.config.security.safe_mode_restrictions if self.is_safe_mode() else []