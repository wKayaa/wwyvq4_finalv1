#!/usr/bin/env python3
"""
🖥️ WWYVQ Framework v2.1 - Interface Module
Ultra-Organized Architecture - Multiple User Interfaces

This module provides multiple interfaces for the WWYVQ framework:
- CLI: Interactive command-line interface
- Web: Real-time web dashboard
- API: Professional REST API
"""

from .cli import WWYVQCLIInterface, CLIModule
from .web import WWYVQWebDashboard, WebModule
from .api import WWYVQRestAPI, APIModule

__all__ = [
    # CLI Interface
    'WWYVQCLIInterface',
    'CLIModule',
    
    # Web Dashboard
    'WWYVQWebDashboard',
    'WebModule',
    
    # REST API
    'WWYVQRestAPI',
    'APIModule'
]