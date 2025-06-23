#!/usr/bin/env python3
"""
Production Configuration for K8s Credential Harvester
"""

import os
from typing import List, Optional

class ProductionConfig:
    """Production configuration settings"""
    
    # Target Configuration
    DEFAULT_TARGET_RANGES = [
        "10.0.0.0/16",      # Private networks
        "172.16.0.0/12",
        "192.168.0.0/16",
        "127.0.0.1"         # Localhost
    ]
    
    # Kubernetes Ports
    K8S_PORTS = [6443, 8443, 8080, 10250, 10255]
    
    # Timing Configuration
    SCAN_TIMEOUT = 5
    API_TIMEOUT = 10
    VERIFICATION_TIMEOUT = 15
    
    # Concurrency Limits
    MAX_CONCURRENT_SCANS = 50
    MAX_CONCURRENT_VERIFICATIONS = 10
    
    # Security Settings
    REQUIRE_EXPLICIT_TARGETS = True
    BLOCK_PRODUCTION_DOMAINS = [
        "amazonaws.com", "azure.com", "googleapis.com",
        "digitalocean.com", "linode.com"
    ]
    
    # Output Settings
    SAVE_RAW_CREDENTIALS = False  # Don't save raw creds for security
    ENCRYPT_OUTPUT = True
    COMPRESS_RESULTS = True
    
    @classmethod
    def get_webhook_url(cls) -> Optional[str]:
        """Get webhook URL from environment"""
        return os.getenv('K8S_HARVEST_WEBHOOK_URL')
    
    @classmethod
    def get_target_ranges(cls) -> List[str]:
        """Get target ranges from environment or use defaults"""
        env_targets = os.getenv('K8S_TARGET_RANGES')
        if env_targets:
            return env_targets.split(',')
        return cls.DEFAULT_TARGET_RANGES
    
    @classmethod
    def is_production_safe(cls, target: str) -> bool:
        """Check if target is safe for production scanning"""
        for blocked_domain in cls.BLOCK_PRODUCTION_DOMAINS:
            if blocked_domain in target.lower():
                return False
        return True

# Usage example
if __name__ == "__main__":
    config = ProductionConfig()
    print("Production K8s Harvester Configuration:")
    print(f"Target Ranges: {config.get_target_ranges()}")
    print(f"Webhook URL: {'Set' if config.get_webhook_url() else 'Not set'}")