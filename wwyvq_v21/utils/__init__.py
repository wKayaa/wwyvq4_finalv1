#!/usr/bin/env python3
"""
🛠️ WWYVQ Framework v2.1 - Utilities Module
Ultra-Organized Architecture - Utility Functions and Helpers

Common utilities used across the framework.
"""

import hashlib
import time
import re
from typing import Any, Dict, List, Optional
from datetime import datetime


class UtilsModule:
    """
    Utility functions for WWYVQ v2.1
    """
    
    def __init__(self, config_manager, logger, engine):
        """Initialize utils module"""
        self.config_manager = config_manager
        self.logger = logger
        self.engine = engine
        
        self.logger.info("🛠️ Utilities Module initialized")
    
    @staticmethod
    def generate_id(prefix: str = "", length: int = 8) -> str:
        """Generate unique ID"""
        timestamp = str(time.time())
        hash_obj = hashlib.md5(timestamp.encode())
        unique_id = hash_obj.hexdigest()[:length]
        return f"{prefix}{unique_id}" if prefix else unique_id
    
    @staticmethod
    def validate_ip(ip: str) -> bool:
        """Validate IP address"""
        import ipaddress
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_cidr(cidr: str) -> bool:
        """Validate CIDR notation"""
        import ipaddress
        try:
            ipaddress.ip_network(cidr, strict=False)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    @staticmethod
    def format_bytes(bytes_count: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f} PB"
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format duration in seconds to human readable format"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe filesystem usage"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        # Limit length
        if len(filename) > 255:
            filename = filename[:255]
        
        return filename
    
    @staticmethod
    def extract_domain(url: str) -> Optional[str]:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return None
    
    @staticmethod
    def is_private_ip(ip: str) -> bool:
        """Check if IP is private"""
        import ipaddress
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except ValueError:
            return False
    
    @staticmethod
    def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
        """Mask sensitive data for logging"""
        if len(data) <= visible_chars * 2:
            return mask_char * len(data)
        
        start_visible = data[:visible_chars]
        end_visible = data[-visible_chars:]
        masked_middle = mask_char * (len(data) - visible_chars * 2)
        
        return f"{start_visible}{masked_middle}{end_visible}"
    
    async def shutdown(self):
        """Shutdown utils module"""
        self.logger.info("🛑 Utilities Module shutdown completed")


# Global utility functions
def get_timestamp() -> str:
    """Get current timestamp"""
    return datetime.utcnow().isoformat()


def safe_get(dictionary: Dict, key: str, default: Any = None) -> Any:
    """Safely get value from dictionary"""
    return dictionary.get(key, default)


def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Merge two dictionaries"""
    result = dict1.copy()
    result.update(dict2)
    return result


def flatten_list(nested_list: List[Any]) -> List[Any]:
    """Flatten nested list"""
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result