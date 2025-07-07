#!/usr/bin/env python3
"""
Enhanced Telegram Alerting System
Professional-grade security alerts with contextual information and severity levels
Author: wKayaa | Enhanced Version | 2025-01-28
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import hashlib
import os

from enhanced_security_monitor import DetectionResult, SeverityLevel, CredentialType

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class AlertConfig:
    """Configuration for alert system"""
    telegram_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    alert_threshold: SeverityLevel = SeverityLevel.MEDIUM
    rate_limit_seconds: int = 5  # Minimum seconds between alerts
    max_alerts_per_hour: int = 100
    include_context: bool = True
    include_suggestions: bool = True
    redact_credentials: bool = True

class ProfessionalTelegramAlerter:
    """Professional-grade Telegram alerting system"""
    
    def __init__(self, config: AlertConfig):
        self.config = config
        self.last_alert_time = 0
        self.alerts_sent_hour = 0
        self.hour_start = datetime.utcnow().hour
        self.alert_queue = []
        self.stats = {
            'total_alerts': 0,
            'alerts_sent': 0,
            'alerts_rate_limited': 0,
            'alerts_filtered': 0
        }
        
        if not self.config.telegram_token or not self.config.telegram_chat_id:
            logger.warning("Telegram credentials not configured - alerts will be logged only")
            self.telegram_enabled = False
        else:
            self.telegram_enabled = True
            logger.info("Professional Telegram alerting system initialized")
    
    async def send_detection_alert(self, detection: DetectionResult, repo_name: str = "Unknown"):
        """Send professional security alert for detected credential"""
        
        # Check if alert should be sent based on severity threshold
        if not self._should_send_alert(detection):
            self.stats['alerts_filtered'] += 1
            return False
        
        # Rate limiting check
        if not self._check_rate_limit():
            self.stats['alerts_rate_limited'] += 1
            logger.warning("Alert rate limited - queuing for later")
            self.alert_queue.append((detection, repo_name))
            return False
        
        # Generate professional alert message
        alert_message = self._generate_alert_message(detection, repo_name)
        
        # Send alert
        if self.telegram_enabled:
            success = await self._send_telegram_alert(alert_message)
            if success:
                self.stats['alerts_sent'] += 1
                self._update_rate_limit()
                logger.info(f"Alert sent for {detection.credential_type.value} in {detection.source_file}")
                return True
            else:
                logger.error("Failed to send Telegram alert")
                return False
        else:
            # Log alert instead
            logger.critical(f"SECURITY ALERT: {alert_message}")
            self.stats['alerts_sent'] += 1
            return True
    
    async def send_scan_summary(self, scan_results: Dict[str, Any], repo_name: str = "Unknown"):
        """Send scan completion summary"""
        summary_message = self._generate_summary_message(scan_results, repo_name)
        
        if self.telegram_enabled:
            await self._send_telegram_alert(summary_message)
        else:
            logger.info(f"SCAN SUMMARY: {summary_message}")
    
    async def send_system_alert(self, level: SeverityLevel, title: str, message: str):
        """Send system-level alert"""
        system_message = self._generate_system_message(level, title, message)
        
        if self.telegram_enabled:
            await self._send_telegram_alert(system_message)
        else:
            logger.log(self._severity_to_log_level(level), f"SYSTEM ALERT: {system_message}")
    
    def _should_send_alert(self, detection: DetectionResult) -> bool:
        """Determine if alert should be sent based on severity and config"""
        self.stats['total_alerts'] += 1
        
        severity_order = {
            SeverityLevel.LOW: 1,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.HIGH: 3,
            SeverityLevel.CRITICAL: 4
        }
        
        return severity_order[detection.severity] >= severity_order[self.config.alert_threshold]
    
    def _check_rate_limit(self) -> bool:
        """Check if alert can be sent based on rate limiting"""
        current_time = datetime.utcnow().timestamp()
        current_hour = datetime.utcnow().hour
        
        # Reset hourly counter if new hour
        if current_hour != self.hour_start:
            self.alerts_sent_hour = 0
            self.hour_start = current_hour
        
        # Check hourly limit
        if self.alerts_sent_hour >= self.config.max_alerts_per_hour:
            return False
        
        # Check time-based rate limit
        if current_time - self.last_alert_time < self.config.rate_limit_seconds:
            return False
        
        return True
    
    def _update_rate_limit(self):
        """Update rate limiting counters"""
        self.last_alert_time = datetime.utcnow().timestamp()
        self.alerts_sent_hour += 1
    
    def _generate_alert_message(self, detection: DetectionResult, repo_name: str) -> str:
        """Generate professional alert message"""
        
        # Severity emoji mapping
        severity_emojis = {
            SeverityLevel.LOW: "⚠️",
            SeverityLevel.MEDIUM: "🔸",
            SeverityLevel.HIGH: "🔴",
            SeverityLevel.CRITICAL: "🚨"
        }
        
        # Credential type emoji mapping
        type_emojis = {
            CredentialType.AWS_ACCESS_KEY: "☁️",
            CredentialType.AWS_SECRET_KEY: "🔐",
            CredentialType.SENDGRID_KEY: "📧",
            CredentialType.JWT_TOKEN: "🎫",
            CredentialType.BEARER_TOKEN: "🔑",
            CredentialType.API_KEY: "🗝️",
            CredentialType.PASSWORD: "🔒",
            CredentialType.SECRET: "🤐"
        }
        
        emoji = severity_emojis.get(detection.severity, "⚠️")
        type_emoji = type_emojis.get(detection.credential_type, "🔑")
        
        # Build alert message
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        message = f"""{emoji} <b>SECURITY ALERT - {detection.severity.value}</b> {emoji}

{type_emoji} <b>Credential Detected:</b> {detection.credential_type.value.replace('_', ' ').title()}
📊 <b>Confidence:</b> {detection.confidence_score:.1f}%
🎯 <b>Repository:</b> {repo_name}
📁 <b>File:</b> <code>{detection.source_file}</code>
📍 <b>Line:</b> {detection.line_number}

🔍 <b>Redacted Value:</b> <code>{detection.redacted_value if self.config.redact_credentials else detection.value}</code>"""
        
        # Add context if enabled
        if self.config.include_context and detection.context:
            context_preview = detection.context[:200] + "..." if len(detection.context) > 200 else detection.context
            message += f"\n\n📄 <b>Context:</b>\n<code>{context_preview}</code>"
        
        # Add proximity matches if available
        if detection.proximity_matches:
            matches_str = ", ".join(detection.proximity_matches[:3])
            message += f"\n\n🔗 <b>Related Patterns:</b> {matches_str}"
        
        # Add suggestions if enabled
        if self.config.include_suggestions and detection.suggestions:
            message += "\n\n🛠️ <b>Remediation Steps:</b>"
            for i, suggestion in enumerate(detection.suggestions[:3], 1):
                message += f"\n{i}. {suggestion}"
        
        # Add timestamp and operator info
        message += f"""

⏰ <b>Detected:</b> {timestamp}
👤 <b>Scanner:</b> wKayaa Enhanced Security Monitor
🔖 <b>Alert ID:</b> {self._generate_alert_id(detection)}"""
        
        return message
    
    def _generate_summary_message(self, scan_results: Dict[str, Any], repo_name: str) -> str:
        """Generate scan completion summary message"""
        
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        message = f"""✅ <b>SECURITY SCAN COMPLETED</b> ✅

🎯 <b>Repository:</b> {repo_name}
📊 <b>Scan Results:</b>

📁 Files Scanned: {scan_results.get('files_scanned', 0):,}
🔍 Credentials Found: {scan_results.get('credentials_detected', 0)}
🚫 False Positives Filtered: {scan_results.get('false_positives_filtered', 0)}
✅ Confirmed Threats: {scan_results.get('confirmed_credentials', 0)}

⏱️ <b>Scan Duration:</b> {scan_results.get('elapsed_time', 'Unknown')}
⏰ <b>Completed:</b> {timestamp}

📈 <b>Alert Statistics:</b>
• Alerts Generated: {self.stats['total_alerts']}
• Alerts Sent: {self.stats['alerts_sent']}
• Rate Limited: {self.stats['alerts_rate_limited']}
• Filtered: {self.stats['alerts_filtered']}

🚀 <b>Scanner:</b> wKayaa Enhanced Security Monitor v2.0"""
        
        return message
    
    def _generate_system_message(self, level: SeverityLevel, title: str, message: str) -> str:
        """Generate system alert message"""
        
        severity_emojis = {
            SeverityLevel.LOW: "ℹ️",
            SeverityLevel.MEDIUM: "⚠️",
            SeverityLevel.HIGH: "🔴",
            SeverityLevel.CRITICAL: "🚨"
        }
        
        emoji = severity_emojis.get(level, "ℹ️")
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        return f"""{emoji} <b>SYSTEM {level.value}</b> {emoji}

📢 <b>{title}</b>

{message}

⏰ <b>Time:</b> {timestamp}
🤖 <b>System:</b> wKayaa Enhanced Security Monitor"""
    
    def _generate_alert_id(self, detection: DetectionResult) -> str:
        """Generate unique alert ID"""
        content = f"{detection.source_file}{detection.line_number}{detection.value}{detection.timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:8].upper()
    
    def _severity_to_log_level(self, severity: SeverityLevel) -> int:
        """Convert severity to logging level"""
        mapping = {
            SeverityLevel.LOW: logging.INFO,
            SeverityLevel.MEDIUM: logging.WARNING,
            SeverityLevel.HIGH: logging.ERROR,
            SeverityLevel.CRITICAL: logging.CRITICAL
        }
        return mapping.get(severity, logging.INFO)
    
    async def _send_telegram_alert(self, message: str) -> bool:
        """Send message to Telegram with error handling"""
        try:
            url = f"https://api.telegram.org/bot{self.config.telegram_token}/sendMessage"
            data = {
                "chat_id": self.config.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }
            
            connector = aiohttp.TCPConnector(
                ssl=False,
                keepalive_timeout=30,
                limit=10
            )
            
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(url, json=data, timeout=15) as response:
                    if response.status == 200:
                        logger.debug("Telegram alert sent successfully")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Telegram API error {response.status}: {error_text}")
                        return False
                        
        except asyncio.TimeoutError:
            logger.error("Telegram alert timed out")
            return False
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False
    
    async def process_queued_alerts(self):
        """Process any queued alerts that were rate limited"""
        while self.alert_queue:
            if not self._check_rate_limit():
                break
                
            detection, repo_name = self.alert_queue.pop(0)
            await self.send_detection_alert(detection, repo_name)
            
            # Small delay between processing queued alerts
            await asyncio.sleep(1)
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alerting system statistics"""
        return {
            'total_alerts_processed': self.stats['total_alerts'],
            'alerts_sent_successfully': self.stats['alerts_sent'],
            'alerts_rate_limited': self.stats['alerts_rate_limited'],
            'alerts_filtered_by_severity': self.stats['alerts_filtered'],
            'alerts_queued': len(self.alert_queue),
            'telegram_enabled': self.telegram_enabled,
            'current_hour_count': self.alerts_sent_hour,
            'hourly_limit': self.config.max_alerts_per_hour
        }

class AlertingDashboard:
    """Real-time alerting dashboard for monitoring"""
    
    def __init__(self, alerter: ProfessionalTelegramAlerter):
        self.alerter = alerter
        self.alert_history = []
        self.max_history = 1000
    
    def record_alert(self, detection: DetectionResult, sent: bool):
        """Record alert in history"""
        alert_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'credential_type': detection.credential_type.value,
            'severity': detection.severity.value,
            'confidence': detection.confidence_score,
            'file': detection.source_file,
            'sent': sent,
            'alert_id': self.alerter._generate_alert_id(detection)
        }
        
        self.alert_history.append(alert_record)
        
        # Maintain history size limit
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data for monitoring"""
        recent_alerts = self.alert_history[-50:]  # Last 50 alerts
        
        # Calculate statistics
        total_alerts = len(self.alert_history)
        sent_alerts = sum(1 for alert in self.alert_history if alert['sent'])
        
        severity_counts = {}
        type_counts = {}
        
        for alert in recent_alerts:
            severity = alert['severity']
            cred_type = alert['credential_type']
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            type_counts[cred_type] = type_counts.get(cred_type, 0) + 1
        
        return {
            'summary': {
                'total_alerts': total_alerts,
                'alerts_sent': sent_alerts,
                'success_rate': (sent_alerts / total_alerts * 100) if total_alerts > 0 else 0
            },
            'recent_alerts': recent_alerts,
            'statistics': {
                'severity_distribution': severity_counts,
                'credential_type_distribution': type_counts
            },
            'system_stats': self.alerter.get_alert_stats(),
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def search_alerts(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Search alert history"""
        query_lower = query.lower()
        
        matching_alerts = []
        for alert in reversed(self.alert_history):  # Most recent first
            if (query_lower in alert['file'].lower() or 
                query_lower in alert['credential_type'].lower() or
                query_lower in alert['severity'].lower() or
                query_lower in alert['alert_id'].lower()):
                
                matching_alerts.append(alert)
                
                if len(matching_alerts) >= limit:
                    break
        
        return matching_alerts

# Export classes for use in other modules
__all__ = [
    'ProfessionalTelegramAlerter', 'AlertingDashboard', 'AlertConfig'
]

if __name__ == "__main__":
    print("🚀 Enhanced Telegram Alerting System - wKayaa Production")