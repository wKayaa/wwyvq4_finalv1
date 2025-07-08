#!/usr/bin/env python3
"""
WWYVQ Framework v2 - Core Engine
Author: wKayaa
Date: 2025-01-15

Moteur principal unifié gérant toutes les opérations du framework.
"""

import asyncio
import uuid
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

from .config import ConfigurationManager
from .session import SessionManager
from .target import TargetManager
from .logger import WWYVQLogger


class ExecutionMode(Enum):
    """Modes d'exécution disponibles"""
    PASSIVE = "passive"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"
    STEALTH = "stealth"


class OperationStatus(Enum):
    """Status des opérations"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class OperationResult:
    """Résultat d'une opération"""
    operation_id: str
    operation_type: str
    status: OperationStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WWYVQEngine:
    """
    Moteur principal du framework WWYVQ v2
    
    Responsabilités:
    - Orchestration de toutes les opérations
    - Gestion des sessions et configurations
    - Coordination des modules spécialisés
    - Monitoring et logging centralisé
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le moteur principal
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.engine_id = str(uuid.uuid4())[:8]
        self.start_time = datetime.utcnow()
        self.status = OperationStatus.PENDING
        
        # Composants core
        self.config_manager = ConfigurationManager(config_path)
        self.session_manager = SessionManager(self.config_manager)
        self.target_manager = TargetManager(self.config_manager)
        self.logger = WWYVQLogger(self.config_manager)
        
        # Modules spécialisés (seront chargés dynamiquement)
        self.modules = {}
        self.active_operations = {}
        
        # Statistiques globales
        self.stats = {
            'engine_id': self.engine_id,
            'start_time': self.start_time.isoformat(),
            'operations_total': 0,
            'operations_completed': 0,
            'operations_failed': 0,
            'targets_processed': 0,
            'results_collected': 0
        }
        
        self.logger.info(f"🚀 WWYVQ Engine v2 initialized - ID: {self.engine_id}")
    
    async def initialize(self) -> bool:
        """
        Initialise tous les composants du moteur
        
        Returns:
            bool: True si l'initialisation réussit
        """
        try:
            self.logger.info("🔧 Initializing WWYVQ Engine components...")
            
            # Initialisation des managers
            await self.session_manager.initialize()
            await self.target_manager.initialize()
            
            # Chargement des modules
            await self._load_modules()
            
            # Validation de la configuration
            if not await self._validate_configuration():
                return False
            
            self.status = OperationStatus.RUNNING
            self.logger.info("✅ WWYVQ Engine initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Engine initialization failed: {e}")
            self.status = OperationStatus.FAILED
            return False
    
    async def _load_modules(self):
        """Charge les modules spécialisés"""
        modules_to_load = [
            'exploit',
            'scanner', 
            'validator',
            'notifier',
            'exporter',
            'utils'
        ]
        
        for module_name in modules_to_load:
            try:
                # Import dynamique des modules
                module_path = f"wwyvq_v2.modules.{module_name}"
                module = __import__(module_path, fromlist=[module_name])
                self.modules[module_name] = module
                self.logger.info(f"✅ Module '{module_name}' loaded")
            except ImportError as e:
                self.logger.warning(f"⚠️ Module '{module_name}' not available: {e}")
    
    async def _validate_configuration(self) -> bool:
        """Valide la configuration du système"""
        try:
            config = self.config_manager.get_config()
            
            # Validation des paramètres critiques
            if not config.core.max_concurrent or config.core.max_concurrent <= 0:
                self.logger.error("❌ Invalid max_concurrent configuration")
                return False
            
            if not config.core.timeout or config.core.timeout <= 0:
                self.logger.error("❌ Invalid timeout configuration")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Configuration validation failed: {e}")
            return False
    
    async def execute_operation(self, operation_type: str, 
                              targets: List[str], 
                              mode: ExecutionMode = ExecutionMode.STANDARD,
                              **kwargs) -> OperationResult:
        """
        Exécute une opération spécifique
        
        Args:
            operation_type: Type d'opération (scan, exploit, validate, etc.)
            targets: Liste des cibles
            mode: Mode d'exécution
            **kwargs: Paramètres additionnels
            
        Returns:
            OperationResult: Résultat de l'opération
        """
        operation_id = str(uuid.uuid4())[:8]
        operation = OperationResult(
            operation_id=operation_id,
            operation_type=operation_type,
            status=OperationStatus.PENDING,
            start_time=datetime.utcnow()
        )
        
        self.active_operations[operation_id] = operation
        self.stats['operations_total'] += 1
        
        try:
            self.logger.info(f"🚀 Starting operation '{operation_type}' - ID: {operation_id}")
            
            # Préparation des cibles
            processed_targets = await self.target_manager.process_targets(targets)
            operation.metadata['targets_count'] = len(processed_targets)
            
            # Démarrage de l'opération
            operation.status = OperationStatus.RUNNING
            
            # Exécution selon le type d'opération
            if operation_type == 'scan':
                results = await self._execute_scan(processed_targets, mode, **kwargs)
            elif operation_type == 'exploit':
                results = await self._execute_exploit(processed_targets, mode, **kwargs)
            elif operation_type == 'validate':
                results = await self._execute_validate(processed_targets, mode, **kwargs)
            else:
                raise ValueError(f"Unknown operation type: {operation_type}")
            
            # Finalisation
            operation.results = results
            operation.status = OperationStatus.COMPLETED
            operation.end_time = datetime.utcnow()
            
            self.stats['operations_completed'] += 1
            self.stats['targets_processed'] += len(processed_targets)
            
            self.logger.info(f"✅ Operation '{operation_type}' completed - ID: {operation_id}")
            
        except Exception as e:
            operation.status = OperationStatus.FAILED
            operation.end_time = datetime.utcnow()
            operation.errors.append(str(e))
            
            self.stats['operations_failed'] += 1
            self.logger.error(f"❌ Operation '{operation_type}' failed - ID: {operation_id}: {e}")
        
        return operation
    
    async def _execute_scan(self, targets: List[str], mode: ExecutionMode, **kwargs) -> Dict[str, Any]:
        """Exécute une opération de scan"""
        # Placeholder pour l'implémentation du scan
        # Sera connecté aux modules de scan
        return {
            'operation': 'scan',
            'targets_scanned': len(targets),
            'results': []
        }
    
    async def _execute_exploit(self, targets: List[str], mode: ExecutionMode, **kwargs) -> Dict[str, Any]:
        """Exécute une opération d'exploitation"""
        # Placeholder pour l'implémentation d'exploitation
        # Sera connecté aux modules d'exploitation
        return {
            'operation': 'exploit',
            'targets_exploited': len(targets),
            'results': []
        }
    
    async def _execute_validate(self, targets: List[str], mode: ExecutionMode, **kwargs) -> Dict[str, Any]:
        """Exécute une opération de validation"""
        # Placeholder pour l'implémentation de validation
        # Sera connecté aux modules de validation
        return {
            'operation': 'validate',
            'targets_validated': len(targets),
            'results': []
        }
    
    async def get_operation_status(self, operation_id: str) -> Optional[OperationResult]:
        """
        Récupère le statut d'une opération
        
        Args:
            operation_id: ID de l'opération
            
        Returns:
            OperationResult ou None si non trouvée
        """
        return self.active_operations.get(operation_id)
    
    async def cancel_operation(self, operation_id: str) -> bool:
        """
        Annule une opération en cours
        
        Args:
            operation_id: ID de l'opération
            
        Returns:
            bool: True si l'annulation réussit
        """
        if operation_id in self.active_operations:
            operation = self.active_operations[operation_id]
            if operation.status == OperationStatus.RUNNING:
                operation.status = OperationStatus.CANCELLED
                operation.end_time = datetime.utcnow()
                self.logger.info(f"⏹️ Operation cancelled - ID: {operation_id}")
                return True
        return False
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques du moteur
        
        Returns:
            Dict contenant les statistiques
        """
        current_time = datetime.utcnow()
        uptime = current_time - self.start_time
        
        stats = self.stats.copy()
        stats.update({
            'current_time': current_time.isoformat(),
            'uptime_seconds': uptime.total_seconds(),
            'status': self.status.value,
            'active_operations': len(self.active_operations),
            'modules_loaded': len(self.modules)
        })
        
        return stats
    
    async def shutdown(self):
        """Arrêt propre du moteur"""
        self.logger.info("🛑 Shutting down WWYVQ Engine...")
        
        # Annulation des opérations en cours
        for operation_id in list(self.active_operations.keys()):
            await self.cancel_operation(operation_id)
        
        # Nettoyage des sessions
        await self.session_manager.cleanup()
        
        self.status = OperationStatus.CANCELLED
        self.logger.info("✅ WWYVQ Engine shutdown completed")