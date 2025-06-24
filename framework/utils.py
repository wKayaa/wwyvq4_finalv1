#!/usr/bin/env python3
"""
Framework Utilities Module
Author: wKayaa
Date: 2025-06-24 17:02:05 UTC
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Union
from ipaddress import IPv4Network, IPv4Address


class FrameworkUtils:
    """Utility functions for the framework"""
    
    @staticmethod
    def setup_logging(config: dict) -> logging.Logger:
        """Setup logging configuration"""
        log_level = getattr(logging, config.get('level', 'INFO').upper())
        logger = logging.getLogger('framework')
        logger.setLevel(log_level)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Console handler
        if config.get('console', True):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # File handler
        if 'file' in config:
            try:
                file_handler = logging.FileHandler(config['file'])
                file_handler.setLevel(log_level)
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                print(f"⚠️ Failed to setup file logging: {e}")
        
        return logger
    
    @staticmethod
    def load_targets(file_path: str) -> List[str]:
        """Load targets from file"""
        targets = []
        
        if not file_path:
            return targets
            
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        targets.append(line)
        except FileNotFoundError:
            print(f"❌ Target file not found: {file_path}")
        except Exception as e:
            print(f"❌ Error loading targets: {e}")
        
        return targets
    
    @staticmethod
    def expand_cidr_targets(targets: List[str]) -> List[str]:
        """Expand CIDR notation to individual IPs"""
        expanded = []
        
        for target in targets:
            target = target.strip()
            if not target:
                continue
                
            try:
                # Check if it's a CIDR
                if '/' in target:
                    network = IPv4Network(target, strict=False)
                    # Limit expansion to reasonable size
                    if network.num_addresses <= 65536:  # /16 or smaller
                        expanded.extend([str(ip) for ip in network.hosts()])
                    else:
                        print(f"⚠️ CIDR too large, skipping: {target}")
                else:
                    # Single IP or hostname
                    expanded.append(target)
            except Exception:
                # If it's not a valid IP/CIDR, treat as hostname
                expanded.append(target)
        
        return expanded
    
    @staticmethod
    def validate_file_exists(file_path: str) -> bool:
        """Check if file exists"""
        return Path(file_path).exists()
    
    @staticmethod
    def ensure_directory(dir_path: str) -> bool:
        """Ensure directory exists"""
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"❌ Failed to create directory {dir_path}: {e}")
            return False
    
    @staticmethod
    def safe_import(module_name: str, class_name: str = None):
        """Safely import a module or class"""
        try:
            module = __import__(module_name, fromlist=[class_name] if class_name else [])
            if class_name:
                return getattr(module, class_name)
            return module
        except ImportError as e:
            print(f"⚠️ Failed to import {module_name}.{class_name or ''}: {e}")
            return None
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    @staticmethod
    def format_number(num: int) -> str:
        """Format number with thousand separators"""
        return f"{num:,}"