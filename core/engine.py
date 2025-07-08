#!/usr/bin/env python3
"""
WWYVQ v2.1 Core Engine
Ultra-Organized Architecture - Central Coordination Engine

Author: wKayaa
Date: 2025-01-07
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml
from pathlib import Path

from .config import ConfigurationManager
from .job_manager import JobManager  
from .logger import SystemLogger


class ExecutionMode(Enum):
    """Execution modes for the framework"""
    PASSIVE = "passive"
    ACTIVE = "active"
    AGGRESSIVE = "aggressive"
    STEALTH = "stealth"


class ModuleType(Enum):
    """Available module types"""
    EXPLOIT = "exploit"
    VALIDATOR = "validator"
    NOTIFIER = "notifier"
    EXPORTER = "exporter"


@dataclass
class JobConfiguration:
    """Configuration for a WWYVQ job"""
    job_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = "WWYVQ Job"
    mode: ExecutionMode = ExecutionMode.ACTIVE
    targets: List[str] = field(default_factory=list)
    max_concurrent: int = 50
    timeout: int = 30
    kubernetes_focus: bool = True
    validation_enabled: bool = True
    notifications_enabled: bool = True
    export_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SystemStats:
    """System-wide statistics"""
    jobs_executed: int = 0
    targets_processed: int = 0
    clusters_found: int = 0
    clusters_exploited: int = 0
    credentials_found: int = 0
    credentials_validated: int = 0
    notifications_sent: int = 0
    exports_generated: int = 0
    start_time: datetime = field(default_factory=datetime.utcnow)


class WWYVQCoreEngine:
    """
    WWYVQ v2.1 Core Engine
    Central coordination system for all modules
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the core engine"""
        self.engine_id = str(uuid.uuid4())[:8]
        self.start_time = datetime.utcnow()
        
        # Initialize core components
        self.config_manager = ConfigurationManager(config_path)
        self.job_manager = JobManager()
        self.logger = SystemLogger("WWYVQCoreEngine")
        
        # Module registries
        self.modules: Dict[ModuleType, Dict[str, Any]] = {
            ModuleType.EXPLOIT: {},
            ModuleType.VALIDATOR: {},
            ModuleType.NOTIFIER: {},
            ModuleType.EXPORTER: {}
        }
        
        # System statistics
        self.stats = SystemStats()
        
        # Active jobs
        self.active_jobs: Dict[str, JobConfiguration] = {}
        
        self.logger.info(f"🚀 WWYVQ v2.1 Core Engine initialized - ID: {self.engine_id}")
    
    async def initialize(self) -> bool:
        """Initialize all system components"""
        try:
            self.logger.info("🔧 Initializing WWYVQ Core Engine...")
            
            # Load configuration
            await self.config_manager.load_config()
            
            # Initialize job manager
            await self.job_manager.initialize()
            
            # Register default modules
            await self._register_default_modules()
            
            # Validate system readiness
            if await self._validate_system_readiness():
                self.logger.info("✅ WWYVQ Core Engine initialization complete")
                return True
            else:
                self.logger.error("❌ System validation failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize core engine: {e}")
            return False
    
    async def register_module(self, module_type: ModuleType, name: str, module_instance: Any) -> bool:
        """Register a module with the core engine"""
        try:
            self.modules[module_type][name] = module_instance
            self.logger.info(f"✅ Registered {module_type.value} module: {name}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to register module {name}: {e}")
            return False
    
    async def create_job(self, job_config: JobConfiguration) -> str:
        """Create a new job"""
        try:
            # Validate job configuration
            if not job_config.targets:
                raise ValueError("Job must have at least one target")
            
            # Generate unique job ID if not provided
            if not job_config.job_id:
                job_config.job_id = str(uuid.uuid4())[:8]
            
            # Store job configuration
            self.active_jobs[job_config.job_id] = job_config
            
            # Register with job manager
            await self.job_manager.create_job(job_config)
            
            self.logger.info(f"📋 Created job: {job_config.job_id} - {job_config.name}")
            return job_config.job_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create job: {e}")
            raise
    
    async def execute_job(self, job_id: str) -> Dict[str, Any]:
        """Execute a job using all registered modules"""
        try:
            if job_id not in self.active_jobs:
                raise ValueError(f"Job {job_id} not found")
            
            job_config = self.active_jobs[job_id]
            self.logger.info(f"🚀 Executing job: {job_id} - {job_config.name}")
            
            # Create execution context
            context = {
                'job_id': job_id,
                'config': job_config,
                'start_time': datetime.utcnow(),
                'results': {},
                'errors': []
            }
            
            # Execute phases in order
            if job_config.kubernetes_focus:
                # Phase 1: Kubernetes Exploitation
                context['results']['exploitation'] = await self._execute_exploitation_phase(context)
            
            if job_config.validation_enabled:
                # Phase 2: Credential Validation
                context['results']['validation'] = await self._execute_validation_phase(context)
            
            if job_config.notifications_enabled:
                # Phase 3: Notifications
                context['results']['notifications'] = await self._execute_notification_phase(context)
            
            if job_config.export_enabled:
                # Phase 4: Export Results
                context['results']['exports'] = await self._execute_export_phase(context)
            
            # Update statistics
            self.stats.jobs_executed += 1
            
            self.logger.info(f"✅ Job {job_id} completed successfully")
            return context['results']
            
        except Exception as e:
            self.logger.error(f"❌ Job {job_id} execution failed: {e}")
            raise
    
    async def _execute_exploitation_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute exploitation modules"""
        results = {'clusters_found': 0, 'clusters_exploited': 0, 'credentials_found': 0}
        
        if ModuleType.EXPLOIT not in self.modules or not self.modules[ModuleType.EXPLOIT]:
            self.logger.warning("⚠️ No exploitation modules registered")
            return results
        
        try:
            for module_name, module in self.modules[ModuleType.EXPLOIT].items():
                self.logger.info(f"🎯 Executing exploitation module: {module_name}")
                
                # Execute module with job context
                if hasattr(module, 'execute_async'):
                    module_results = await module.execute_async(context)
                else:
                    module_results = await asyncio.to_thread(module.execute, context)
                
                # Aggregate results
                for key, value in module_results.items():
                    if key in results and isinstance(value, int):
                        results[key] += value
                    else:
                        results[key] = value
                        
        except Exception as e:
            self.logger.error(f"❌ Exploitation phase failed: {e}")
            context['errors'].append(f"Exploitation: {e}")
        
        return results
    
    async def _execute_validation_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validation modules"""
        results = {'credentials_validated': 0, 'validation_errors': 0}
        
        if ModuleType.VALIDATOR not in self.modules or not self.modules[ModuleType.VALIDATOR]:
            self.logger.warning("⚠️ No validation modules registered")
            return results
        
        try:
            for module_name, module in self.modules[ModuleType.VALIDATOR].items():
                self.logger.info(f"🔍 Executing validation module: {module_name}")
                
                # Execute module with job context
                if hasattr(module, 'execute_async'):
                    module_results = await module.execute_async(context)
                else:
                    module_results = await asyncio.to_thread(module.execute, context)
                
                # Aggregate results
                for key, value in module_results.items():
                    if key in results and isinstance(value, int):
                        results[key] += value
                    else:
                        results[key] = value
                        
        except Exception as e:
            self.logger.error(f"❌ Validation phase failed: {e}")
            context['errors'].append(f"Validation: {e}")
        
        return results
    
    async def _execute_notification_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute notification modules"""
        results = {'notifications_sent': 0, 'notification_errors': 0}
        
        if ModuleType.NOTIFIER not in self.modules or not self.modules[ModuleType.NOTIFIER]:
            self.logger.warning("⚠️ No notification modules registered")
            return results
        
        try:
            for module_name, module in self.modules[ModuleType.NOTIFIER].items():
                self.logger.info(f"📢 Executing notification module: {module_name}")
                
                # Execute module with job context
                if hasattr(module, 'execute_async'):
                    module_results = await module.execute_async(context)
                else:
                    module_results = await asyncio.to_thread(module.execute, context)
                
                # Aggregate results
                for key, value in module_results.items():
                    if key in results and isinstance(value, int):
                        results[key] += value
                    else:
                        results[key] = value
                        
        except Exception as e:
            self.logger.error(f"❌ Notification phase failed: {e}")
            context['errors'].append(f"Notification: {e}")
        
        return results
    
    async def _execute_export_phase(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute export modules"""
        results = {'exports_generated': 0, 'export_errors': 0}
        
        if ModuleType.EXPORTER not in self.modules or not self.modules[ModuleType.EXPORTER]:
            self.logger.warning("⚠️ No export modules registered")
            return results
        
        try:
            for module_name, module in self.modules[ModuleType.EXPORTER].items():
                self.logger.info(f"📊 Executing export module: {module_name}")
                
                # Execute module with job context
                if hasattr(module, 'execute_async'):
                    module_results = await module.execute_async(context)
                else:
                    module_results = await asyncio.to_thread(module.execute, context)
                
                # Aggregate results
                for key, value in module_results.items():
                    if key in results and isinstance(value, int):
                        results[key] += value
                    else:
                        results[key] = value
                        
        except Exception as e:
            self.logger.error(f"❌ Export phase failed: {e}")
            context['errors'].append(f"Export: {e}")
        
        return results
    
    async def _register_default_modules(self) -> None:
        """Register default modules if available"""
        try:
            # Try to import and register existing modules with absolute imports
            import sys
            from pathlib import Path
            
            # Add the base directory to path for imports
            base_dir = Path(__file__).parent.parent
            if str(base_dir) not in sys.path:
                sys.path.insert(0, str(base_dir))
            
            from exploit.kubernetes_exploit import KubernetesExploitModule
            await self.register_module(ModuleType.EXPLOIT, "kubernetes", KubernetesExploitModule())
        except ImportError as e:
            self.logger.warning(f"⚠️ Kubernetes exploit module not available: {e}")
        
        try:
            from exploit.scraper import IntelligentScraper
            await self.register_module(ModuleType.EXPLOIT, "scraper", IntelligentScraper())
        except ImportError as e:
            self.logger.warning(f"⚠️ Intelligent scraper module not available: {e}")
        
        try:
            from validator.credential_validator import CredentialValidatorModule
            await self.register_module(ModuleType.VALIDATOR, "credentials", CredentialValidatorModule())
        except ImportError as e:
            self.logger.warning(f"⚠️ Credential validator module not available: {e}")
        
        try:
            from notifier.telegram_notifier import TelegramNotifierModule
            await self.register_module(ModuleType.NOTIFIER, "telegram", TelegramNotifierModule())
        except ImportError as e:
            self.logger.warning(f"⚠️ Telegram notifier module not available: {e}")
        
        try:
            from notifier.discord_notifier import DiscordNotifierModule
            await self.register_module(ModuleType.NOTIFIER, "discord", DiscordNotifierModule())
        except ImportError as e:
            self.logger.warning(f"⚠️ Discord notifier module not available: {e}")
        
        try:
            from exporter.json_exporter import JsonExporterModule
            await self.register_module(ModuleType.EXPORTER, "json", JsonExporterModule())
        except ImportError as e:
            self.logger.warning(f"⚠️ JSON exporter module not available: {e}")
    
    async def _validate_system_readiness(self) -> bool:
        """Validate system is ready for operation"""
        try:
            # Check if at least one exploitation module is registered
            if not self.modules[ModuleType.EXPLOIT]:
                self.logger.error("❌ No exploit modules registered")
                return False
            
            # Check configuration
            if not self.config_manager.is_valid():
                self.logger.error("❌ Invalid configuration")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ System validation failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        return {
            'engine_id': self.engine_id,
            'start_time': self.start_time.isoformat(),
            'uptime_seconds': (datetime.utcnow() - self.start_time).total_seconds(),
            'stats': self.stats.__dict__,
            'active_jobs': len(self.active_jobs),
            'registered_modules': {
                module_type.value: len(modules) 
                for module_type, modules in self.modules.items()
            }
        }
    
    async def shutdown(self) -> None:
        """Graceful shutdown of the core engine"""
        try:
            self.logger.info("🛑 Shutting down WWYVQ Core Engine...")
            
            # Stop all active jobs
            for job_id in list(self.active_jobs.keys()):
                await self.job_manager.stop_job(job_id)
            
            # Clean up modules
            for module_type in self.modules:
                for module_name, module in self.modules[module_type].items():
                    if hasattr(module, 'shutdown'):
                        await module.shutdown()
            
            self.logger.info("✅ WWYVQ Core Engine shutdown complete")
            
        except Exception as e:
            self.logger.error(f"❌ Error during shutdown: {e}")