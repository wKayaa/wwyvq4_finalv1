#!/usr/bin/env python3
"""
🧠 WWYVQ Framework v2.1 - Core Engine
Ultra-Organized Architecture - Main Orchestration Engine

Responsibilities:
- Orchestration of all operations
- Module coordination and loading
- Session and configuration management
- Monitoring and logging centralization
- Performance optimization
"""

import asyncio
import uuid
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import logging

# Import core components
from .config import ConfigurationManager
from .session import SessionManager
from .target import TargetManager
from .logger import WWYVQLogger


class OperationStatus(Enum):
    """Status of operations"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionMode(Enum):
    """Execution modes"""
    STANDARD = "standard"
    STEALTH = "stealth"
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"


@dataclass
class OperationResult:
    """Result of an operation"""
    operation_id: str
    operation_type: str
    status: OperationStatus
    targets_processed: int
    results_found: int
    execution_time: float
    metadata: Dict[str, Any]
    errors: List[str]


class WWYVQEngine:
    """
    Main orchestration engine for WWYVQ v2.1
    
    Features:
    - Ultra-organized modular architecture
    - Async/await native implementation
    - Advanced session management
    - Professional logging system
    - Real-time monitoring
    - Connection pooling
    - Rate limiting
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the WWYVQ v2.1 engine
        
        Args:
            config_path: Path to configuration file
        """
        self.engine_id = str(uuid.uuid4())[:8]
        self.start_time = datetime.utcnow()
        self.status = OperationStatus.PENDING
        
        # Core components
        self.config_manager = ConfigurationManager(config_path)
        self.session_manager = SessionManager(self.config_manager)
        self.target_manager = TargetManager(self.config_manager)
        self.logger = WWYVQLogger(self.config_manager)
        
        # Module registry
        self.modules = {}
        self.active_operations = {}
        
        # Performance metrics
        self.stats = {
            'engine_id': self.engine_id,
            'start_time': self.start_time.isoformat(),
            'operations_total': 0,
            'operations_completed': 0,
            'operations_failed': 0,
            'targets_processed': 0,
            'credentials_found': 0,
            'valid_credentials': 0,
            'k8s_clusters_found': 0,
            'uptime_seconds': 0
        }
        
        # Connection pool for HTTP requests
        self.http_session = None
        self.semaphore = None
        
        self.logger.info(f"🚀 WWYVQ Engine v2.1 initialized - ID: {self.engine_id}")
    
    async def initialize(self) -> bool:
        """
        Initialize all engine components
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("🔧 Initializing WWYVQ Engine v2.1 components...")
            
            # Initialize managers
            await self.session_manager.initialize()
            await self.target_manager.initialize()
            
            # Load specialized modules
            await self._load_modules()
            
            # Initialize connection pool
            await self._initialize_connection_pool()
            
            # Validate configuration
            if not await self._validate_configuration():
                return False
            
            self.status = OperationStatus.RUNNING
            self.logger.info("✅ WWYVQ Engine v2.1 initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Engine initialization failed: {e}")
            self.status = OperationStatus.FAILED
            return False
    
    async def _load_modules(self):
        """Load specialized modules"""
        modules_to_load = [
            'exploit',
            'scrape',
            'validator',
            'notifier',
            'exporter',
            'utils'
        ]
        
        for module_name in modules_to_load:
            try:
                # Dynamic import with v2.1 path
                module_path = f"wwyvq_v2.1.{module_name}"
                module = __import__(module_path, fromlist=[module_name])
                
                # Get main class from module
                main_class_name = f"{module_name.title()}Module"
                if hasattr(module, main_class_name):
                    module_class = getattr(module, main_class_name)
                    self.modules[module_name] = module_class(
                        self.config_manager,
                        self.logger,
                        self
                    )
                    self.logger.info(f"✅ Module '{module_name}' loaded and initialized")
                else:
                    self.logger.warning(f"⚠️ Module '{module_name}' main class not found")
                    
            except ImportError as e:
                self.logger.warning(f"⚠️ Module '{module_name}' not available: {e}")
            except Exception as e:
                self.logger.error(f"❌ Failed to load module '{module_name}': {e}")
    
    async def _initialize_connection_pool(self):
        """Initialize HTTP connection pool"""
        try:
            import aiohttp
            
            # Create session with connection pool
            connector = aiohttp.TCPConnector(
                limit=self.config_manager.get_config().core.max_concurrent,
                limit_per_host=20,
                ttl_dns_cache=300,
                use_dns_cache=True
            )
            
            timeout = aiohttp.ClientTimeout(
                total=self.config_manager.get_config().core.timeout
            )
            
            self.http_session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            # Create semaphore for rate limiting
            self.semaphore = asyncio.Semaphore(
                self.config_manager.get_config().core.max_concurrent
            )
            
            self.logger.info("✅ Connection pool initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize connection pool: {e}")
            raise
    
    async def _validate_configuration(self) -> bool:
        """Validate engine configuration"""
        return self.config_manager.validate_config()
    
    async def execute_operation(self, 
                               operation_type: str,
                               targets: List[str],
                               mode: ExecutionMode = ExecutionMode.STANDARD,
                               **kwargs) -> OperationResult:
        """
        Execute an operation
        
        Args:
            operation_type: Type of operation (scan, exploit, scrape, validate)
            targets: List of targets
            mode: Execution mode
            **kwargs: Additional parameters
            
        Returns:
            OperationResult: Result of the operation
        """
        operation_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        self.logger.info(f"🎯 Starting operation: {operation_type} - ID: {operation_id}")
        
        try:
            # Create operation context
            operation_context = {
                'operation_id': operation_id,
                'operation_type': operation_type,
                'targets': targets,
                'mode': mode,
                'start_time': start_time,
                'kwargs': kwargs
            }
            
            self.active_operations[operation_id] = operation_context
            
            # Execute based on operation type
            if operation_type == 'scan':
                results = await self._execute_scan(targets, mode, **kwargs)
            elif operation_type == 'exploit':
                results = await self._execute_exploit(targets, mode, **kwargs)
            elif operation_type == 'scrape':
                results = await self._execute_scrape(targets, mode, **kwargs)
            elif operation_type == 'validate':
                results = await self._execute_validate(targets, mode, **kwargs)
            else:
                raise ValueError(f"Unknown operation type: {operation_type}")
            
            # Update statistics
            execution_time = time.time() - start_time
            self.stats['operations_total'] += 1
            self.stats['operations_completed'] += 1
            self.stats['targets_processed'] += len(targets)
            self.stats['uptime_seconds'] = int(time.time() - self.start_time.timestamp())
            
            # Create result
            result = OperationResult(
                operation_id=operation_id,
                operation_type=operation_type,
                status=OperationStatus.COMPLETED,
                targets_processed=len(targets),
                results_found=len(results.get('results', [])),
                execution_time=execution_time,
                metadata=results,
                errors=results.get('errors', [])
            )
            
            self.logger.info(f"✅ Operation completed: {operation_id} in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            self.stats['operations_failed'] += 1
            self.logger.error(f"❌ Operation failed: {operation_id} - {e}")
            
            return OperationResult(
                operation_id=operation_id,
                operation_type=operation_type,
                status=OperationStatus.FAILED,
                targets_processed=0,
                results_found=0,
                execution_time=time.time() - start_time,
                metadata={},
                errors=[str(e)]
            )
        
        finally:
            # Clean up operation context
            self.active_operations.pop(operation_id, None)
    
    async def _execute_scan(self, targets: List[str], mode: ExecutionMode, **kwargs) -> Dict[str, Any]:
        """Execute scan operation"""
        results = {'results': [], 'errors': []}
        
        if 'exploit' in self.modules:
            exploit_results = await self.modules['exploit'].scan_targets(targets, mode, **kwargs)
            results['results'].extend(exploit_results.get('results', []))
            results['errors'].extend(exploit_results.get('errors', []))
        
        return results
    
    async def _execute_exploit(self, targets: List[str], mode: ExecutionMode, **kwargs) -> Dict[str, Any]:
        """Execute exploitation operation"""
        results = {'results': [], 'errors': []}
        
        if 'exploit' in self.modules:
            exploit_results = await self.modules['exploit'].exploit_targets(targets, mode, **kwargs)
            results['results'].extend(exploit_results.get('results', []))
            results['errors'].extend(exploit_results.get('errors', []))
        
        return results
    
    async def _execute_scrape(self, targets: List[str], mode: ExecutionMode, **kwargs) -> Dict[str, Any]:
        """Execute scraping operation"""
        results = {'results': [], 'errors': []}
        
        if 'scrape' in self.modules:
            scrape_results = await self.modules['scrape'].scrape_targets(targets, mode, **kwargs)
            results['results'].extend(scrape_results.get('results', []))
            results['errors'].extend(scrape_results.get('errors', []))
        
        return results
    
    async def _execute_validate(self, targets: List[str], mode: ExecutionMode, **kwargs) -> Dict[str, Any]:
        """Execute validation operation"""
        results = {'results': [], 'errors': []}
        
        if 'validator' in self.modules:
            validation_results = await self.modules['validator'].validate_targets(targets, mode, **kwargs)
            results['results'].extend(validation_results.get('results', []))
            results['errors'].extend(validation_results.get('errors', []))
        
        return results
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        current_time = time.time()
        self.stats['uptime_seconds'] = int(current_time - self.start_time.timestamp())
        return self.stats.copy()
    
    def get_active_operations(self) -> Dict[str, Any]:
        """Get active operations"""
        return self.active_operations.copy()
    
    async def shutdown(self):
        """Gracefully shutdown the engine"""
        self.logger.info("🛑 Shutting down WWYVQ Engine v2.1...")
        
        # Close HTTP session
        if self.http_session:
            await self.http_session.close()
        
        # Shutdown modules
        for module_name, module in self.modules.items():
            if hasattr(module, 'shutdown'):
                await module.shutdown()
        
        self.status = OperationStatus.CANCELLED
        self.logger.info("✅ Engine shutdown completed")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.shutdown()