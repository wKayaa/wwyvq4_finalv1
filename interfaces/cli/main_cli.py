#!/usr/bin/env python3
"""
WWYVQ v2.1 CLI Interface
Advanced command-line interface with interactive features

Author: wKayaa
Date: 2025-01-07
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.engine import WWYVQCoreEngine, JobConfiguration, ExecutionMode
from core.config import ConfigurationManager
from core.logger import setup_global_logging, LogLevel


class WWYVQCLIInterface:
    """
    WWYVQ v2.1 Advanced CLI Interface
    Interactive command-line interface with real-time feedback
    """
    
    def __init__(self):
        """Initialize CLI interface"""
        self.engine = None
        self.config_manager = None
        self.version = "2.1"
        
        # CLI styling
        self.colors = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m'
        }
    
    def print_banner(self):
        """Print WWYVQ banner"""
        banner = f"""
{self.colors['cyan']}{self.colors['bold']}
╔══════════════════════════════════════════════════════════════╗
║                    WWYVQ v{self.version} Ultra-Organized                     ║
║              Kubernetes Exploitation Framework              ║
║                        by wKayaa                            ║
╚══════════════════════════════════════════════════════════════╝
{self.colors['reset']}
{self.colors['yellow']}🎯 Focus: Kubernetes Cluster Exploitation{self.colors['reset']}
{self.colors['green']}🔍 Features: Real-time validation, 2500+ paths, Professional notifications{self.colors['reset']}
{self.colors['blue']}⚡ Architecture: Ultra-organized modular design{self.colors['reset']}
"""
        print(banner)
    
    def print_colored(self, text: str, color: str = 'white', bold: bool = False):
        """Print colored text"""
        style = self.colors.get(color, self.colors['white'])
        if bold:
            style += self.colors['bold']
        print(f"{style}{text}{self.colors['reset']}")
    
    def create_argument_parser(self) -> argparse.ArgumentParser:
        """Create argument parser for CLI"""
        parser = argparse.ArgumentParser(
            description="WWYVQ v2.1 - Ultra-Organized Kubernetes Exploitation Framework",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s -t 192.168.1.0/24 -m aggressive --k8s-focus
  %(prog)s -f targets.txt -m stealth --validate --notify
  %(prog)s --config custom_config.yaml -t 10.0.0.1-10.0.0.100
  %(prog)s --interactive
  %(prog)s --generate-config
  %(prog)s --web-dashboard
            """
        )
        
        # Target specification
        target_group = parser.add_argument_group('Target Specification')
        target_group.add_argument(
            '-t', '--targets',
            nargs='+',
            help='Target hosts, IPs, or CIDR ranges'
        )
        target_group.add_argument(
            '-f', '--file',
            help='File containing targets (one per line)'
        )
        target_group.add_argument(
            '--cidr',
            help='CIDR range to scan (e.g., 192.168.1.0/24)'
        )
        
        # Execution modes
        mode_group = parser.add_argument_group('Execution Modes')
        mode_group.add_argument(
            '-m', '--mode',
            choices=['passive', 'active', 'aggressive', 'stealth'],
            default='active',
            help='Execution mode (default: active)'
        )
        mode_group.add_argument(
            '--k8s-focus',
            action='store_true',
            help='Focus on Kubernetes exploitation'
        )
        mode_group.add_argument(
            '--scrape-only',
            action='store_true',
            help='Only perform intelligent scraping'
        )
        
        # Performance options
        perf_group = parser.add_argument_group('Performance Options')
        perf_group.add_argument(
            '--threads',
            type=int,
            default=50,
            help='Maximum concurrent threads (default: 50)'
        )
        perf_group.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='Timeout per operation in seconds (default: 30)'
        )
        perf_group.add_argument(
            '--rate-limit',
            type=float,
            default=0.1,
            help='Rate limiting delay in seconds (default: 0.1)'
        )
        
        # Feature toggles
        feature_group = parser.add_argument_group('Feature Options')
        feature_group.add_argument(
            '--validate',
            action='store_true',
            help='Enable real-time credential validation'
        )
        feature_group.add_argument(
            '--notify',
            action='store_true',
            help='Enable notifications (Telegram/Discord)'
        )
        feature_group.add_argument(
            '--export',
            action='store_true',
            help='Enable data export (JSON/CSV)'
        )
        feature_group.add_argument(
            '--no-validation',
            action='store_true',
            help='Disable credential validation'
        )
        feature_group.add_argument(
            '--valid-only',
            action='store_true',
            help='Only notify for valid credentials'
        )
        
        # Configuration
        config_group = parser.add_argument_group('Configuration')
        config_group.add_argument(
            '--config',
            help='Configuration file path (YAML/JSON)'
        )
        config_group.add_argument(
            '--generate-config',
            action='store_true',
            help='Generate sample configuration file'
        )
        config_group.add_argument(
            '--telegram-token',
            help='Telegram bot token'
        )
        config_group.add_argument(
            '--telegram-chat',
            help='Telegram chat ID'
        )
        config_group.add_argument(
            '--discord-webhook',
            help='Discord webhook URL'
        )
        
        # Output options
        output_group = parser.add_argument_group('Output Options')
        output_group.add_argument(
            '-o', '--output',
            help='Output directory (default: ./results)'
        )
        output_group.add_argument(
            '--json',
            action='store_true',
            help='Export results in JSON format'
        )
        output_group.add_argument(
            '--csv',
            action='store_true',
            help='Export results in CSV format'
        )
        output_group.add_argument(
            '--hosts-file',
            action='store_true',
            help='Generate hosts file from targets'
        )
        
        # Interface options
        interface_group = parser.add_argument_group('Interface Options')
        interface_group.add_argument(
            '--interactive',
            action='store_true',
            help='Launch interactive mode'
        )
        interface_group.add_argument(
            '--web-dashboard',
            action='store_true',
            help='Launch web dashboard'
        )
        interface_group.add_argument(
            '--api-server',
            action='store_true',
            help='Start REST API server'
        )
        interface_group.add_argument(
            '--port',
            type=int,
            default=8080,
            help='Port for web/API interface (default: 8080)'
        )
        
        # Logging and debugging
        debug_group = parser.add_argument_group('Logging & Debug')
        debug_group.add_argument(
            '--verbose', '-v',
            action='count',
            default=0,
            help='Increase verbosity (use -vv for debug)'
        )
        debug_group.add_argument(
            '--quiet', '-q',
            action='store_true',
            help='Quiet mode (minimal output)'
        )
        debug_group.add_argument(
            '--log-file',
            help='Log file path'
        )
        debug_group.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug mode'
        )
        
        # Job management
        job_group = parser.add_argument_group('Job Management')
        job_group.add_argument(
            '--job-name',
            help='Custom job name'
        )
        job_group.add_argument(
            '--job-id',
            help='Custom job ID'
        )
        job_group.add_argument(
            '--resume',
            help='Resume job from ID'
        )
        
        # Utility commands
        parser.add_argument(
            '--version',
            action='version',
            version=f'WWYVQ v{self.version}'
        )
        
        return parser
    
    async def run(self, args: List[str] = None) -> int:
        """Run the CLI interface"""
        try:
            # Parse arguments
            parser = self.create_argument_parser()
            parsed_args = parser.parse_args(args)
            
            # Print banner
            if not parsed_args.quiet:
                self.print_banner()
            
            # Setup logging
            log_level = LogLevel.INFO
            if parsed_args.verbose >= 2 or parsed_args.debug:
                log_level = LogLevel.DEBUG
            elif parsed_args.verbose == 1:
                log_level = LogLevel.INFO
            elif parsed_args.quiet:
                log_level = LogLevel.WARNING
            
            setup_global_logging(
                log_level=log_level,
                log_dir=Path(parsed_args.log_file).parent if parsed_args.log_file else None,
                enable_console=not parsed_args.quiet
            )
            
            # Handle special commands
            if parsed_args.generate_config:
                return await self.generate_config_file(parsed_args)
            
            if parsed_args.interactive:
                return await self.run_interactive_mode(parsed_args)
            
            if parsed_args.web_dashboard:
                return await self.run_web_dashboard(parsed_args)
            
            if parsed_args.api_server:
                return await self.run_api_server(parsed_args)
            
            # Initialize core engine
            self.config_manager = ConfigurationManager(parsed_args.config)
            self.engine = WWYVQCoreEngine(parsed_args.config)
            
            if not await self.engine.initialize():
                self.print_colored("❌ Failed to initialize WWYVQ engine", 'red', bold=True)
                return 1
            
            # Update configuration from CLI arguments
            await self.update_config_from_args(parsed_args)
            
            # Load targets
            targets = await self.load_targets(parsed_args)
            if not targets:
                self.print_colored("❌ No targets specified", 'red', bold=True)
                parser.print_help()
                return 1
            
            # Create job configuration
            job_config = self.create_job_config(parsed_args, targets)
            
            # Execute job
            return await self.execute_job(job_config, parsed_args)
            
        except KeyboardInterrupt:
            self.print_colored("\n🛑 Operation cancelled by user", 'yellow', bold=True)
            return 130
        except Exception as e:
            self.print_colored(f"❌ CLI Error: {e}", 'red', bold=True)
            if parsed_args.debug if 'parsed_args' in locals() else False:
                import traceback
                traceback.print_exc()
            return 1
        finally:
            if self.engine:
                await self.engine.shutdown()
    
    async def load_targets(self, args) -> List[str]:
        """Load targets from various sources"""
        targets = []
        
        # From command line arguments
        if args.targets:
            targets.extend(args.targets)
        
        # From file
        if args.file:
            try:
                with open(args.file, 'r') as f:
                    file_targets = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    targets.extend(file_targets)
                self.print_colored(f"📂 Loaded {len(file_targets)} targets from {args.file}", 'blue')
            except Exception as e:
                self.print_colored(f"❌ Error loading targets from file: {e}", 'red')
        
        # From CIDR
        if args.cidr:
            targets.append(args.cidr)
        
        # Remove duplicates while preserving order
        unique_targets = []
        seen = set()
        for target in targets:
            if target not in seen:
                unique_targets.append(target)
                seen.add(target)
        
        return unique_targets
    
    def create_job_config(self, args, targets: List[str]) -> JobConfiguration:
        """Create job configuration from CLI arguments"""
        # Map CLI mode to ExecutionMode
        mode_mapping = {
            'passive': ExecutionMode.PASSIVE,
            'active': ExecutionMode.ACTIVE,
            'aggressive': ExecutionMode.AGGRESSIVE,
            'stealth': ExecutionMode.STEALTH
        }
        
        job_config = JobConfiguration(
            job_id=args.job_id or None,  # Will auto-generate if None
            name=args.job_name or f"WWYVQ CLI Job - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            mode=mode_mapping.get(args.mode, ExecutionMode.ACTIVE),
            targets=targets,
            max_concurrent=args.threads,
            timeout=args.timeout,
            kubernetes_focus=args.k8s_focus or not args.scrape_only,
            validation_enabled=args.validate and not args.no_validation,
            notifications_enabled=args.notify,
            export_enabled=args.export or args.json or args.csv or args.hosts_file
        )
        
        return job_config
    
    async def update_config_from_args(self, args):
        """Update configuration from CLI arguments"""
        config = self.config_manager.get_config()
        
        # Update exploit configuration
        if hasattr(args, 'rate_limit') and args.rate_limit:
            config.exploit.rate_limit_delay = args.rate_limit
        
        # Update notification configuration
        if args.telegram_token:
            config.notifier.telegram_enabled = True
            config.notifier.telegram_token = args.telegram_token
        
        if args.telegram_chat:
            config.notifier.telegram_chat_id = args.telegram_chat
        
        if args.discord_webhook:
            config.notifier.discord_enabled = True
            config.notifier.discord_webhook_url = args.discord_webhook
        
        if args.valid_only:
            config.notifier.valid_credentials_only = True
        
        # Update export configuration
        if args.output:
            config.exporter.output_directory = args.output
        
        if args.json:
            config.exporter.json_export = True
        
        if args.csv:
            config.exporter.csv_export = True
        
        if args.hosts_file:
            config.exporter.create_host_file = True
        
        # Save updated configuration
        await self.config_manager.save_config()
    
    async def execute_job(self, job_config: JobConfiguration, args) -> int:
        """Execute the main job"""
        try:
            self.print_colored(f"🚀 Starting WWYVQ job: {job_config.name}", 'green', bold=True)
            self.print_colored(f"🎯 Targets: {len(job_config.targets)}", 'blue')
            self.print_colored(f"⚡ Mode: {job_config.mode.value}", 'cyan')
            self.print_colored(f"🔧 Max Concurrent: {job_config.max_concurrent}", 'yellow')
            
            # Create job
            job_id = await self.engine.create_job(job_config)
            self.print_colored(f"📋 Job ID: {job_id}", 'purple')
            
            # Start progress monitoring
            if not args.quiet:
                progress_task = asyncio.create_task(self.monitor_progress(job_id))
            
            # Execute job
            start_time = datetime.utcnow()
            results = await self.engine.execute_job(job_id)
            end_time = datetime.utcnow()
            
            # Stop progress monitoring
            if not args.quiet:
                progress_task.cancel()
            
            # Display results
            await self.display_results(results, start_time, end_time, args)
            
            self.print_colored("✅ WWYVQ job completed successfully", 'green', bold=True)
            return 0
            
        except Exception as e:
            self.print_colored(f"❌ Job execution failed: {e}", 'red', bold=True)
            return 1
    
    async def monitor_progress(self, job_id: str):
        """Monitor job progress"""
        try:
            while True:
                job_info = await self.engine.job_manager.get_job_status(job_id)
                if job_info:
                    print(f"\r🔄 Progress: {job_info.progress:.1f}% | Target: {job_info.current_target or 'N/A'}", end='', flush=True)
                
                await asyncio.sleep(2)
                
        except asyncio.CancelledError:
            print()  # New line after progress
    
    async def display_results(self, results: Dict[str, Any], start_time: datetime, 
                            end_time: datetime, args):
        """Display job results"""
        duration = end_time - start_time
        
        print("\n" + "="*60)
        self.print_colored("📊 WWYVQ RESULTS SUMMARY", 'cyan', bold=True)
        print("="*60)
        
        # Timing information
        self.print_colored(f"⏱️  Duration: {duration.total_seconds():.1f} seconds", 'blue')
        
        # Exploitation results
        if 'exploitation' in results:
            exploitation = results['exploitation']
            self.print_colored("\n🎯 EXPLOITATION RESULTS:", 'yellow', bold=True)
            print(f"   • Targets Processed: {exploitation.get('targets_processed', 0)}")
            print(f"   • Clusters Found: {exploitation.get('clusters_found', 0)}")
            print(f"   • Clusters Exploited: {exploitation.get('clusters_exploited', 0)}")
            print(f"   • Credentials Found: {exploitation.get('credentials_found', 0)}")
            print(f"   • Vulnerabilities Found: {exploitation.get('vulnerabilities_found', 0)}")
        
        # Validation results
        if 'validation' in results:
            validation = results['validation']
            self.print_colored("\n🔍 VALIDATION RESULTS:", 'green', bold=True)
            print(f"   • Credentials Validated: {validation.get('credentials_validated', 0)}")
            print(f"   • Valid Credentials: {len(validation.get('valid_credentials', []))}")
            print(f"   • Invalid Credentials: {len(validation.get('invalid_credentials', []))}")
            
            # Show valid credentials if not too many
            valid_credentials = validation.get('valid_credentials', [])
            if valid_credentials and len(valid_credentials) <= 10:
                self.print_colored("\n✅ VALID CREDENTIALS:", 'green', bold=True)
                for i, cred in enumerate(valid_credentials, 1):
                    print(f"   {i}. {cred.get('type', 'unknown')} - {cred.get('service', 'unknown')} ({cred.get('confidence', 0):.1f}%)")
        
        # Notification results
        if 'notifications' in results:
            notifications = results['notifications']
            self.print_colored("\n📢 NOTIFICATION RESULTS:", 'purple', bold=True)
            print(f"   • Notifications Sent: {notifications.get('notifications_sent', 0)}")
        
        # Export results
        if 'exports' in results:
            exports = results['exports']
            self.print_colored("\n📊 EXPORT RESULTS:", 'cyan', bold=True)
            print(f"   • Exports Created: {exports.get('exports_generated', 0)}")
        
        print("="*60)
    
    async def generate_config_file(self, args) -> int:
        """Generate sample configuration file"""
        try:
            config_manager = ConfigurationManager("./wwyvq_sample_config.yaml")
            success = config_manager.create_sample_config()
            
            if success:
                self.print_colored("✅ Sample configuration created: wwyvq_sample_config.yaml", 'green', bold=True)
                self.print_colored("📝 Edit the file to customize your settings", 'blue')
                return 0
            else:
                self.print_colored("❌ Failed to create sample configuration", 'red', bold=True)
                return 1
                
        except Exception as e:
            self.print_colored(f"❌ Error generating config: {e}", 'red', bold=True)
            return 1
    
    async def run_interactive_mode(self, args) -> int:
        """Run interactive mode"""
        self.print_colored("🔧 Interactive mode not yet implemented", 'yellow', bold=True)
        self.print_colored("Coming in future version...", 'blue')
        return 0
    
    async def run_web_dashboard(self, args) -> int:
        """Run web dashboard"""
        self.print_colored("🌐 Web dashboard not yet implemented", 'yellow', bold=True)
        self.print_colored("Coming in future version...", 'blue')
        return 0
    
    async def run_api_server(self, args) -> int:
        """Run API server"""
        self.print_colored("🔌 API server not yet implemented", 'yellow', bold=True)
        self.print_colored("Coming in future version...", 'blue')
        return 0


async def main():
    """Main CLI entry point"""
    cli = WWYVQCLIInterface()
    exit_code = await cli.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())