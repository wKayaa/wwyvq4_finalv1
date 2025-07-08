#!/usr/bin/env python3
"""
WWYVQ v2.1 Discord Notifier Module
Professional Discord notifications via webhooks

Author: wKayaa
Date: 2025-01-07
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from .base_notifier import BaseNotifierModule, NotificationMessage, NotificationResult, NotificationLevel


class DiscordNotifierModule(BaseNotifierModule):
    """
    Professional Discord notification module
    Uses webhooks for rich message formatting
    """
    
    def __init__(self):
        super().__init__(
            name="DiscordNotifier",
            description="Professional Discord notifications via webhooks"
        )
        
        # Discord configuration
        self.webhook_url = None
        self.username = "WWYVQ v2.1"
        self.avatar_url = None
        
        # Rate limiting for Discord webhooks
        self.rate_limit_delay = 1.0  # 1 second between messages
        
        # Message formatting
        self.max_message_length = 2000  # Discord limit
        self.max_embed_length = 6000   # Discord embed limit
        
        # Color scheme for different notification levels
        self.level_colors = {
            NotificationLevel.INFO: 0x3498db,       # Blue
            NotificationLevel.SUCCESS: 0x2ecc71,   # Green  
            NotificationLevel.WARNING: 0xf39c12,   # Orange
            NotificationLevel.ERROR: 0xe74c3c,     # Red
            NotificationLevel.CRITICAL: 0x9b59b6  # Purple
        }
    
    async def execute_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Discord notifications asynchronously"""
        try:
            notifications_sent = 0
            
            # Get validation results from context
            if 'results' in context and 'validation' in context['results']:
                validation_results = context['results']['validation']
                valid_credentials = validation_results.get('valid_credentials', [])
                
                # Send notifications for valid credentials
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
                    
                    for vulnerability in vulnerabilities[:3]:  # Limit to 3 vulnerabilities
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
                'discord_stats': self.get_stats()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Discord notification execution failed: {e}")
            return {'error': str(e)}
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Discord notifications synchronously"""
        return asyncio.run(self.execute_async(context))
    
    async def _send_notification_impl(self, notification: NotificationMessage) -> NotificationResult:
        """Implementation of Discord notification sending"""
        try:
            if not self.webhook_url:
                return NotificationResult(
                    success=False,
                    error_message="Discord webhook URL not configured"
                )
            
            # Create Discord webhook payload
            payload = self._create_discord_payload(notification)
            
            # Send via Discord webhook
            success = await self._send_discord_webhook(payload)
            
            if success:
                return NotificationResult(success=True)
            else:
                return NotificationResult(
                    success=False,
                    error_message="Failed to send Discord webhook"
                )
                
        except Exception as e:
            self.logger.error(f"❌ Error sending Discord notification: {e}")
            return NotificationResult(
                success=False,
                error_message=str(e)
            )
    
    async def _send_discord_webhook(self, payload: Dict[str, Any]) -> bool:
        """Send webhook to Discord"""
        try:
            import aiohttp
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.webhook_url, json=payload, headers=headers) as response:
                    if response.status in [200, 204]:
                        return True
                    else:
                        error_text = await response.text()
                        self.logger.error(f"❌ Discord webhook error {response.status}: {error_text}")
                        return False
        
        except Exception as e:
            self.logger.error(f"❌ Error calling Discord webhook: {e}")
            return False
    
    def _create_discord_payload(self, notification: NotificationMessage) -> Dict[str, Any]:
        """Create Discord webhook payload"""
        try:
            # Base payload
            payload = {
                'username': self.username,
                'embeds': []
            }
            
            if self.avatar_url:
                payload['avatar_url'] = self.avatar_url
            
            # Create embed based on notification type
            if 'credential' in notification.metadata.get('notification_type', ''):
                embed = self._create_credential_embed(notification)
            elif 'vulnerability' in notification.metadata.get('notification_type', ''):
                embed = self._create_vulnerability_embed(notification)
            elif 'cluster' in notification.metadata.get('notification_type', ''):
                embed = self._create_cluster_embed(notification)
            elif 'summary' in notification.metadata.get('notification_type', ''):
                embed = self._create_summary_embed(notification)
            else:
                embed = self._create_generic_embed(notification)
            
            payload['embeds'].append(embed)
            
            return payload
        
        except Exception as e:
            self.logger.error(f"❌ Error creating Discord payload: {e}")
            return {
                'username': self.username,
                'content': f"❌ Error creating notification: {str(e)}"
            }
    
    def _create_credential_embed(self, notification: NotificationMessage) -> Dict[str, Any]:
        """Create embed for credential notification"""
        credential = notification.data
        credential_type = credential.get('type', 'unknown')
        service = self._extract_service_from_type(credential_type)
        
        embed = {
            'title': '🎯 Valid Credential Found',
            'color': self.level_colors[NotificationLevel.SUCCESS],
            'timestamp': notification.timestamp.isoformat(),
            'fields': [
                {
                    'name': '🔑 Credential Type',
                    'value': f'`{credential_type}`',
                    'inline': True
                },
                {
                    'name': '🔗 Service',
                    'value': f'`{service.upper()}`',
                    'inline': True
                },
                {
                    'name': '📊 Confidence',
                    'value': f'`{credential.get("confidence", 0):.1f}%`',
                    'inline': True
                },
                {
                    'name': '🎯 Target',
                    'value': f'`{notification.metadata.get("target", "unknown")}`',
                    'inline': False
                }
            ],
            'footer': {
                'text': 'WWYVQ v2.1 - wKayaa'
            }
        }
        
        # Add service-specific information
        if 'service_info' in credential and credential['service_info']:
            service_info = credential['service_info']
            service_details = []
            for key, value in service_info.items():
                if key != 'service':  # Already shown
                    service_details.append(f"**{key.replace('_', ' ').title()}:** `{value}`")
            
            if service_details:
                embed['fields'].append({
                    'name': '📋 Service Details',
                    'value': '\n'.join(service_details[:5]),  # Limit to 5 details
                    'inline': False
                })
        
        return embed
    
    def _create_vulnerability_embed(self, notification: NotificationMessage) -> Dict[str, Any]:
        """Create embed for vulnerability notification"""
        vulnerability = notification.data.get('vulnerability', 'unknown')
        target = notification.metadata.get('target', 'unknown')
        
        embed = {
            'title': '⚠️ Vulnerability Detected',
            'color': self.level_colors[NotificationLevel.WARNING],
            'timestamp': notification.timestamp.isoformat(),
            'fields': [
                {
                    'name': '🔓 Vulnerability',
                    'value': f'`{vulnerability}`',
                    'inline': False
                },
                {
                    'name': '🎯 Target',
                    'value': f'`{target}`',
                    'inline': False
                }
            ],
            'footer': {
                'text': 'WWYVQ v2.1 - wKayaa'
            }
        }
        
        return embed
    
    def _create_cluster_embed(self, notification: NotificationMessage) -> Dict[str, Any]:
        """Create embed for cluster compromise notification"""
        cluster_info = notification.data
        
        embed = {
            'title': '🚨 Kubernetes Cluster Compromised',
            'color': self.level_colors[NotificationLevel.CRITICAL],
            'timestamp': notification.timestamp.isoformat(),
            'fields': [
                {
                    'name': '☸️ Cluster URL',
                    'value': f'`{cluster_info.get("url", "unknown")}`',
                    'inline': False
                },
                {
                    'name': '🔍 Services Found',
                    'value': f'`{cluster_info.get("services_found", 0)}`',
                    'inline': True
                },
                {
                    'name': '🔑 Credentials',
                    'value': f'`{len(cluster_info.get("credentials", []))}`',
                    'inline': True
                },
                {
                    'name': '🔓 Vulnerabilities',
                    'value': f'`{len(cluster_info.get("vulnerabilities", []))}`',
                    'inline': True
                }
            ],
            'footer': {
                'text': 'WWYVQ v2.1 - wKayaa'
            }
        }
        
        return embed
    
    def _create_summary_embed(self, notification: NotificationMessage) -> Dict[str, Any]:
        """Create embed for job summary notification"""
        summary = notification.data
        
        embed = {
            'title': '📊 WWYVQ Job Summary',
            'color': self.level_colors[NotificationLevel.INFO],
            'timestamp': notification.timestamp.isoformat(),
            'fields': [
                {
                    'name': '🎯 Targets Processed',
                    'value': f'`{summary.get("targets_processed", 0)}`',
                    'inline': True
                },
                {
                    'name': '☸️ Clusters Found',
                    'value': f'`{summary.get("clusters_found", 0)}`',
                    'inline': True
                },
                {
                    'name': '🔑 Credentials Found',
                    'value': f'`{summary.get("credentials_found", 0)}`',
                    'inline': True
                },
                {
                    'name': '✅ Valid Credentials',
                    'value': f'`{summary.get("valid_credentials", 0)}`',
                    'inline': True
                }
            ],
            'footer': {
                'text': 'WWYVQ v2.1 - wKayaa'
            }
        }
        
        # Add optional fields
        if 'duration' in summary:
            embed['fields'].append({
                'name': '⏱️ Duration',
                'value': f'`{summary["duration"]}`',
                'inline': True
            })
        
        if 'job_id' in summary:
            embed['fields'].append({
                'name': '🆔 Job ID',
                'value': f'`{summary["job_id"]}`',
                'inline': True
            })
        
        return embed
    
    def _create_generic_embed(self, notification: NotificationMessage) -> Dict[str, Any]:
        """Create generic embed for notification"""
        embed = {
            'title': notification.title,
            'description': notification.message,
            'color': self.level_colors.get(notification.level, self.level_colors[NotificationLevel.INFO]),
            'timestamp': notification.timestamp.isoformat(),
            'footer': {
                'text': 'WWYVQ v2.1 - wKayaa'
            }
        }
        
        return embed
    
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
        """Initialize Discord configuration"""
        self.webhook_url = config.get('discord_webhook_url', '')
        self.username = config.get('discord_username', 'WWYVQ v2.1')
        self.avatar_url = config.get('discord_avatar_url', None)
        self.rate_limit_delay = config.get('rate_limit_delay', 1.0)
        
        # Validate configuration
        if not self.webhook_url:
            raise ValueError("Discord webhook URL is required")
        
        # Test webhook
        await self._test_discord_webhook()
    
    async def _test_discord_webhook(self) -> bool:
        """Test Discord webhook connection"""
        try:
            test_payload = {
                'username': self.username,
                'embeds': [{
                    'title': '🔧 WWYVQ v2.1 Test',
                    'description': 'Discord webhook connection test',
                    'color': self.level_colors[NotificationLevel.INFO],
                    'timestamp': datetime.utcnow().isoformat(),
                    'footer': {
                        'text': 'WWYVQ v2.1 - wKayaa'
                    }
                }]
            }
            
            if self.avatar_url:
                test_payload['avatar_url'] = self.avatar_url
            
            success = await self._send_discord_webhook(test_payload)
            
            if success:
                self.logger.info("✅ Discord webhook test successful")
                return True
            else:
                self.logger.error("❌ Discord webhook test failed")
                return False
        
        except Exception as e:
            self.logger.error(f"❌ Discord webhook test failed: {e}")
            return False
    
    def supports_level(self, level: NotificationLevel) -> bool:
        """Check if module supports this notification level"""
        return True  # Discord supports all notification levels
    
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