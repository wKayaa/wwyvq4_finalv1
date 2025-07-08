#!/usr/bin/env python3
"""
WWYVQ v2.1 - Ultra-Organized Architecture
Main Entry Point

Author: wKayaa
Date: 2025-01-07

Ultra-organized Kubernetes exploitation framework with:
- Core Engine for module coordination
- Specialized modules (exploit/, validator/, notifier/, exporter/)
- Multiple interfaces (CLI, Web, API)
- Centralized configuration management
- Real-time validation and professional notifications
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from interfaces.cli.main_cli import WWYVQCLIInterface


def main():
    """Main entry point for WWYVQ v2.1"""
    try:
        # Run CLI interface
        cli = WWYVQCLIInterface()
        exit_code = asyncio.run(cli.run())
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()