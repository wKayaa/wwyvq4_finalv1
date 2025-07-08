#!/usr/bin/env python3
"""
WWYVQ v2.1 Base Notifier Module
Base class for all notification modules

Author: wKayaa
Date: 2025-01-07
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class NotificationLevel(Enum):
    """Notification levels"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class NotificationMessage:
    """Notification message structure"""
    title: str
    message: str
    level: NotificationLevel = NotificationLevel.INFO
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationResult:
    """Result of notification sending"""
    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


class BaseNotifierModule(ABC):
    """
    Base class for all notification modules
    Provides common functionality and interface
    """
    
    def __init__(self, name: str, description: str = ""):
        """Initialize base notifier module"""
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"NotifierModule.{name}")
        self.stats = {
            'notifications_sent': 0,
            'notifications_failed': 0,
            'notifications_queued': 0,
            'rate_limit_hits': 0
        }
        
        # Rate limiting
        self.rate_limit_delay = 1.0  # Default 1 second between messages
        self.last_notification_time = None
        
        # Message queue for batching
        self.message_queue = asyncio.Queue()
        self.batch_size = 1  # Default no batching
        self.batch_timeout = 10  # Seconds to wait for batch to fill
    
    @abstractmethod
    async def execute_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the module asynchronously"""
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the module synchronously"""
        pass
    
    async def send_notification(self, notification: NotificationMessage) -> NotificationResult:
        """Send a single notification"""
        try:
            # Apply rate limiting
            await self._apply_rate_limiting()
            
            # Send the notification
            result = await self._send_notification_impl(notification)
            
            # Update statistics
            if result.success:
                self.stats['notifications_sent'] += 1
            else:
                self.stats['notifications_failed'] += 1
            
            self.last_notification_time = datetime.utcnow()
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error sending notification: {e}")
            self.stats['notifications_failed'] += 1
            return NotificationResult(
                success=False,
                error_message=str(e)
            )
    
    @abstractmethod
    async def _send_notification_impl(self, notification: NotificationMessage) -> NotificationResult:
        """Implementation of notification sending"""
        pass
    
    async def send_batch(self, notifications: List[NotificationMessage]) -> List[NotificationResult]:
        """Send a batch of notifications"""
        try:
            self.logger.info(f"📢 Sending batch of {len(notifications)} notifications")
            
            results = []
            for notification in notifications:
                result = await self.send_notification(notification)
                results.append(result)
                
                # Small delay between notifications in batch
                if len(notifications) > 1:
                    await asyncio.sleep(0.1)
            
            self.logger.info(f"✅ Batch sending complete: {sum(1 for r in results if r.success)} successful")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Batch sending failed: {e}")
            return []
    
    async def _apply_rate_limiting(self):
        """Apply rate limiting between notifications"""
        if self.last_notification_time is not None:
            time_since_last = (datetime.utcnow() - self.last_notification_time).total_seconds()
            if time_since_last < self.rate_limit_delay:
                wait_time = self.rate_limit_delay - time_since_last
                self.logger.debug(f"⏳ Rate limiting: waiting {wait_time:.2f}s")
                self.stats['rate_limit_hits'] += 1
                await asyncio.sleep(wait_time)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get module statistics"""
        return {
            'name': self.name,
            'description': self.description,
            'stats': self.stats.copy()
        }
    
    def reset_stats(self):
        """Reset module statistics"""
        self.stats = {
            'notifications_sent': 0,
            'notifications_failed': 0,
            'notifications_queued': 0,
            'rate_limit_hits': 0
        }
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the module with configuration"""
        try:
            self.logger.info(f"🔧 Initializing {self.name} module")
            
            # Update rate limiting settings
            self.rate_limit_delay = config.get('rate_limit_delay', 1.0)
            self.batch_size = config.get('batch_size', 1)
            self.batch_timeout = config.get('batch_timeout', 10)
            
            await self._initialize_impl(config)
            self.logger.info(f"✅ {self.name} module initialized")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {self.name} module: {e}")
            return False
    
    async def _initialize_impl(self, config: Dict[str, Any]) -> None:
        """Implementation of module initialization"""
        pass
    
    async def shutdown(self) -> None:
        """Shutdown the module"""
        try:
            self.logger.info(f"🛑 Shutting down {self.name} module")
            await self._shutdown_impl()
            self.logger.info(f"✅ {self.name} module shutdown complete")
        except Exception as e:
            self.logger.error(f"❌ Error shutting down {self.name} module: {e}")
    
    async def _shutdown_impl(self) -> None:
        """Implementation of module shutdown"""
        pass
    
    def format_message(self, notification: NotificationMessage) -> str:
        """Format notification message for display"""
        # Default implementation - can be overridden by subclasses
        level_emoji = {
            NotificationLevel.INFO: "ℹ️",
            NotificationLevel.SUCCESS: "✅",
            NotificationLevel.WARNING: "⚠️",
            NotificationLevel.ERROR: "❌",
            NotificationLevel.CRITICAL: "🚨"
        }
        
        emoji = level_emoji.get(notification.level, "📢")
        timestamp = notification.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
        
        formatted = f"{emoji} **{notification.title}**\n"
        formatted += f"🕐 {timestamp}\n\n"
        formatted += f"{notification.message}"
        
        return formatted
    
    def supports_level(self, level: NotificationLevel) -> bool:
        """Check if module supports this notification level"""
        return True  # Default implementation supports all levels
    
    def get_supported_levels(self) -> List[NotificationLevel]:
        """Get list of supported notification levels"""
        return list(NotificationLevel)  # Default implementation
    
    async def queue_notification(self, notification: NotificationMessage) -> None:
        """Queue notification for batch processing"""
        await self.message_queue.put(notification)
        self.stats['notifications_queued'] += 1
    
    async def process_queue(self) -> None:
        """Process queued notifications"""
        try:
            while True:
                # Collect messages for batch
                messages = []
                deadline = asyncio.get_event_loop().time() + self.batch_timeout
                
                # Collect up to batch_size messages or until timeout
                while len(messages) < self.batch_size and asyncio.get_event_loop().time() < deadline:
                    try:
                        # Calculate remaining timeout
                        remaining_timeout = deadline - asyncio.get_event_loop().time()
                        if remaining_timeout <= 0:
                            break
                        
                        message = await asyncio.wait_for(
                            self.message_queue.get(),
                            timeout=remaining_timeout
                        )
                        messages.append(message)
                        
                    except asyncio.TimeoutError:
                        break
                
                # Send batch if we have messages
                if messages:
                    await self.send_batch(messages)
                    
                    # Mark messages as done
                    for _ in messages:
                        self.message_queue.task_done()
                
                # Small delay before next batch
                await asyncio.sleep(0.1)
                
        except asyncio.CancelledError:
            self.logger.info("Queue processing cancelled")
        except Exception as e:
            self.logger.error(f"❌ Queue processing error: {e}")
    
    def create_credential_notification(self, credential: Dict[str, Any], target: str) -> NotificationMessage:
        """Create notification for found credential"""
        return NotificationMessage(
            title="🎯 Valid Credential Found",
            message=f"**Type:** {credential.get('type', 'unknown')}\n"
                   f"**Service:** {credential.get('service', 'unknown')}\n"
                   f"**Target:** {target}\n"
                   f"**Confidence:** {credential.get('confidence', 0):.1f}%",
            level=NotificationLevel.SUCCESS,
            data=credential,
            metadata={'target': target, 'credential_type': credential.get('type')}
        )
    
    def create_vulnerability_notification(self, vulnerability: str, target: str) -> NotificationMessage:
        """Create notification for found vulnerability"""
        return NotificationMessage(
            title="🔓 Vulnerability Detected",
            message=f"**Vulnerability:** {vulnerability}\n"
                   f"**Target:** {target}",
            level=NotificationLevel.WARNING,
            data={'vulnerability': vulnerability},
            metadata={'target': target, 'vulnerability_type': vulnerability}
        )
    
    def create_cluster_notification(self, cluster_info: Dict[str, Any]) -> NotificationMessage:
        """Create notification for compromised cluster"""
        return NotificationMessage(
            title="🚨 Kubernetes Cluster Compromised",
            message=f"**Cluster:** {cluster_info.get('url', 'unknown')}\n"
                   f"**Services:** {cluster_info.get('services_found', 0)}\n"
                   f"**Credentials:** {len(cluster_info.get('credentials', []))}\n"
                   f"**Vulnerabilities:** {len(cluster_info.get('vulnerabilities', []))}",
            level=NotificationLevel.CRITICAL,
            data=cluster_info,
            metadata={'target': cluster_info.get('url'), 'cluster_type': 'kubernetes'}
        )
    
    def create_summary_notification(self, summary: Dict[str, Any]) -> NotificationMessage:
        """Create notification for job summary"""
        return NotificationMessage(
            title="📊 WWYVQ Job Summary",
            message=f"**Targets Processed:** {summary.get('targets_processed', 0)}\n"
                   f"**Clusters Found:** {summary.get('clusters_found', 0)}\n"
                   f"**Credentials Found:** {summary.get('credentials_found', 0)}\n"
                   f"**Valid Credentials:** {summary.get('valid_credentials', 0)}\n"
                   f"**Duration:** {summary.get('duration', 'unknown')}",
            level=NotificationLevel.INFO,
            data=summary,
            metadata={'notification_type': 'summary'}
        )