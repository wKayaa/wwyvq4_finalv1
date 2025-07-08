#!/usr/bin/env python3
"""
🚀 WWYVQ Framework v2.1 - Main Runner Script
Ultra-Organized Architecture for Red Team Automation

Author: wKayaa
Version: 2.1
"""

import asyncio
import sys
import argparse
from pathlib import Path
from typing import Optional, List

# Add wwyvq_v21 to path
sys.path.insert(0, str(Path(__file__).parent))

from wwyvq_v21.core.engine import WWYVQEngine
from wwyvq_v21.interface.cli import WWYVQCLIInterface
from wwyvq_v21.interface.web import WWYVQWebDashboard
from wwyvq_v21.interface.api import WWYVQRestAPI


class WWYVQRunner:
    """
    Main runner class for WWYVQ Framework v2.1
    
    Orchestrates all interfaces and provides unified entry point
    """
    
    def __init__(self):
        self.engine = None
        self.cli_interface = None
        self.web_dashboard = None
        self.rest_api = None
    
    async def initialize(self, config_path: Optional[str] = None):
        """Initialize the WWYVQ framework"""
        try:
            # Initialize core engine
            self.engine = WWYVQEngine(config_path)
            await self.engine.initialize()
            
            # Initialize interfaces
            self.cli_interface = WWYVQCLIInterface(self.engine)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize WWYVQ Framework: {e}")
            return False
    
    async def run_cli(self, **kwargs):
        """Run CLI interface"""
        if not self.cli_interface:
            print("❌ CLI interface not initialized")
            return False
        
        await self.cli_interface.run_interactive(**kwargs)
        return True
    
    async def run_scan(self, targets: List[str], **kwargs):
        """Run direct scan operation"""
        if not self.engine:
            print("❌ Engine not initialized")
            return False
        
        result = await self.engine.execute_operation(
            operation_type='scan',
            targets=targets,
            **kwargs
        )
        
        return result
    
    async def run_exploit(self, targets: List[str], **kwargs):
        """Run exploitation operation"""
        if not self.engine:
            print("❌ Engine not initialized")
            return False
        
        result = await self.engine.execute_operation(
            operation_type='exploit',
            targets=targets,
            **kwargs
        )
        
        return result
    
    async def run_web_dashboard(self, host: str = "0.0.0.0", port: int = 8080):
        """Run web dashboard"""
        self.web_dashboard = WWYVQWebDashboard(self.engine)
        await self.web_dashboard.run(host, port)
    
    async def run_rest_api(self, host: str = "0.0.0.0", port: int = 8081):
        """Run REST API server"""
        self.rest_api = WWYVQRestAPI(self.engine)
        await self.rest_api.run(host, port)
    
    def print_banner(self):
        """Print WWYVQ v2.1 banner"""
        banner = """
╭─────────────────────────────────────────────────────────────────────────────╮
│                                                                             │
│  ██╗    ██╗██╗    ██╗██╗   ██╗██╗   ██╗ ██████╗     ██╗   ██╗██████╗ ██╗   │
│  ██║    ██║██║    ██║╚██╗ ██╔╝██║   ██║██╔═══██╗    ██║   ██║╚════██╗███║   │
│  ██║ █╗ ██║██║ █╗ ██║ ╚████╔╝ ██║   ██║██║   ██║    ██║   ██║ █████╔╝╚██║   │
│  ██║███╗██║██║███╗██║  ╚██╔╝  ╚██╗ ██╔╝██║▄▄ ██║    ╚██╗ ██╔╝██╔═══╝  ██║   │
│  ╚███╔███╔╝╚███╔███╔╝   ██║    ╚████╔╝ ╚██████╔╝     ╚████╔╝ ███████╗ ██║   │
│   ╚══╝╚══╝  ╚══╝╚══╝    ╚═╝     ╚═══╝   ╚══▀▀═╝       ╚═══╝  ╚══════╝ ╚═╝   │
│                                                                             │
│                🚀 Red Team Automation Framework v2.1 🚀                    │
│                     Ultra-Organized Architecture                           │
│                                                                             │
╰─────────────────────────────────────────────────────────────────────────────╯

🎯 Focus: Kubernetes Exploitation & Credential Harvesting
🔧 Author: wKayaa
📅 Version: 2.1 - Professional Edition
"""
        print(banner)


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="WWYVQ Framework v2.1 - Red Team Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--config", "-c",
        help="Configuration file path",
        default=None
    )
    
    parser.add_argument(
        "--targets", "-t",
        help="Target file or single target",
        default=None
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["cli", "scan", "exploit", "web", "api"],
        default="cli",
        help="Operation mode"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for web/api mode"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for web/api mode"
    )
    
    parser.add_argument(
        "--threads",
        type=int,
        default=100,
        help="Number of concurrent threads"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = WWYVQRunner()
    runner.print_banner()
    
    # Initialize framework
    if not await runner.initialize(args.config):
        return 1
    
    # Parse targets if provided
    targets = []
    if args.targets:
        if Path(args.targets).exists():
            with open(args.targets, 'r') as f:
                targets = [line.strip() for line in f if line.strip()]
        else:
            targets = [args.targets]
    
    # Run based on mode
    try:
        if args.mode == "cli":
            await runner.run_cli(
                verbose=args.verbose,
                threads=args.threads,
                timeout=args.timeout
            )
        
        elif args.mode == "scan":
            if not targets:
                print("❌ No targets provided for scan mode")
                return 1
            
            result = await runner.run_scan(
                targets=targets,
                threads=args.threads,
                timeout=args.timeout
            )
            print(f"✅ Scan completed: {result}")
        
        elif args.mode == "exploit":
            if not targets:
                print("❌ No targets provided for exploit mode")
                return 1
            
            result = await runner.run_exploit(
                targets=targets,
                threads=args.threads,
                timeout=args.timeout
            )
            print(f"✅ Exploitation completed: {result}")
        
        elif args.mode == "web":
            print(f"🌐 Starting web dashboard on {args.host}:{args.port}")
            await runner.run_web_dashboard(args.host, args.port)
        
        elif args.mode == "api":
            print(f"🔌 Starting REST API on {args.host}:{args.port}")
            await runner.run_rest_api(args.host, args.port)
        
        return 0
    
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        return 0
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))