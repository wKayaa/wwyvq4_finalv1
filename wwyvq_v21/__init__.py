#!/usr/bin/env python3
"""
🏗️ WWYVQ Framework v2.1 - Main Package
Ultra-Organized Architecture - Root Package
"""

# Version information
__version__ = "2.1.0"
__author__ = "wKayaa"
__description__ = "Professional Red Team Automation Framework"

# Import main components for easy access
from .core.engine import WWYVQEngine
from .core.config import ConfigurationManager
from .core.session import SessionManager
from .core.target import TargetManager
from .core.logger import WWYVQLogger

__all__ = [
    'WWYVQEngine',
    'ConfigurationManager',
    'SessionManager',
    'TargetManager',
    'WWYVQLogger'
]