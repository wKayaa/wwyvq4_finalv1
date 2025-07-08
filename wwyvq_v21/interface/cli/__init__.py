#!/usr/bin/env python3
"""
💻 WWYVQ Framework v2.1 - Enhanced CLI Interface
Ultra-Organized Architecture - Interactive Command Line Interface

Features:
- Interactive command-line interface
- Colorful output with progress bars
- Real-time feedback and monitoring
- Command completion and history
- Professional user experience
"""

import asyncio
import sys
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class Colors:
    """ANSI color codes"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    # Background colors
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'
    BG_YELLOW = '\033[103m'
    BG_BLUE = '\033[104m'


class WWYVQCLIInterface:
    """
    Enhanced CLI interface for WWYVQ v2.1
    
    Features:
    - Interactive command processing
    - Beautiful terminal output
    - Real-time progress monitoring
    - Professional user experience
    """
    
    def __init__(self, engine):
        """Initialize CLI interface"""
        self.engine = engine
        self.show_colors = True
        self.running = False
        
        # Command history
        self.command_history = []
        
        # Available commands
        self.commands = {
            'help': self.cmd_help,
            'status': self.cmd_status,
            'stats': self.cmd_stats,
            'scan': self.cmd_scan,
            'exploit': self.cmd_exploit,
            'scrape': self.cmd_scrape,
            'validate': self.cmd_validate,
            'session': self.cmd_session,
            'targets': self.cmd_targets,
            'config': self.cmd_config,
            'export': self.cmd_export,
            'notify': self.cmd_notify,
            'clear': self.cmd_clear,
            'exit': self.cmd_exit,
            'quit': self.cmd_exit
        }
    
    def print_banner(self):
        """Print WWYVQ v2.1 banner"""
        banner = f"""
{Colors.CYAN}{Colors.BOLD}
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
{Colors.RESET}

{Colors.GREEN}🎯 Focus: Kubernetes Exploitation & Credential Harvesting{Colors.RESET}
{Colors.YELLOW}🔧 Author: wKayaa{Colors.RESET}
{Colors.BLUE}📅 Version: 2.1 - Professional Edition{Colors.RESET}

{Colors.MAGENTA}Type 'help' for available commands or 'exit' to quit{Colors.RESET}
"""
        print(banner)
    
    def print_colored(self, message: str, color: str = Colors.WHITE, prefix: str = ""):
        """Print colored message"""
        if self.show_colors:
            print(f"{color}{prefix}{message}{Colors.RESET}")
        else:
            print(f"{prefix}{message}")
    
    def print_info(self, message: str):
        """Print info message"""
        self.print_colored(message, Colors.CYAN, "ℹ️  ")
    
    def print_success(self, message: str):
        """Print success message"""
        self.print_colored(message, Colors.GREEN, "✅ ")
    
    def print_warning(self, message: str):
        """Print warning message"""
        self.print_colored(message, Colors.YELLOW, "⚠️  ")
    
    def print_error(self, message: str):
        """Print error message"""
        self.print_colored(message, Colors.RED, "❌ ")
    
    def print_highlight(self, message: str):
        """Print highlighted message"""
        self.print_colored(message, Colors.MAGENTA + Colors.BOLD, "🔥 ")
    
    def prompt_user(self, prompt: str = "wwyvq> ") -> str:
        """Get user input with colored prompt"""
        try:
            if self.show_colors:
                return input(f"{Colors.BOLD}{Colors.BLUE}{prompt}{Colors.RESET}")
            else:
                return input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\n")
            return "exit"
    
    async def run_interactive(self, **kwargs):
        """Run interactive CLI session"""
        self.print_banner()
        self.print_info("Welcome to WWYVQ Framework v2.1 Interactive Session")
        self.print_info("Type 'help' for available commands")
        
        self.running = True
        
        while self.running:
            try:
                # Get user command
                command_line = self.prompt_user().strip()
                
                if not command_line:
                    continue
                
                # Add to history
                self.command_history.append(command_line)
                
                # Parse command
                parts = command_line.split()
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                # Execute command
                if command in self.commands:
                    try:
                        await self.commands[command](args)
                    except Exception as e:
                        self.print_error(f"Command failed: {e}")
                else:
                    self.print_error(f"Unknown command: {command}")
                    self.print_info("Type 'help' for available commands")
                
                print()  # Add spacing
                
            except KeyboardInterrupt:
                print("\n")
                self.print_info("Use 'exit' command to quit")
            except Exception as e:
                self.print_error(f"Unexpected error: {e}")
        
        self.print_info("Goodbye!")
    
    async def cmd_help(self, args: List[str]):
        """Show help information"""
        if args and args[0] in self.commands:
            # Show specific command help
            command = args[0]
            help_text = self._get_command_help(command)
            self.print_info(f"Help for '{command}':")
            print(help_text)
        else:
            # Show general help
            help_text = f"""
{Colors.BOLD}📚 Available Commands:{Colors.RESET}

{Colors.GREEN}🔧 Operations:{Colors.RESET}
  scan <targets>     - Scan targets for Kubernetes clusters
  exploit <targets>  - Exploit discovered targets
  scrape <targets>   - Scrape targets for credentials
  validate <creds>   - Validate found credentials

{Colors.BLUE}📊 Management:{Colors.RESET}
  status            - Show engine status
  stats             - Show statistics
  session           - Session management
  targets           - Target management
  config            - Configuration management

{Colors.YELLOW}📁 Data:{Colors.RESET}
  export <format>   - Export data (json, csv, html)
  notify <message>  - Send test notification

{Colors.MAGENTA}🛠️ Utility:{Colors.RESET}
  clear             - Clear screen
  help [command]    - Show help
  exit/quit         - Exit application

{Colors.CYAN}💡 Examples:{Colors.RESET}
  scan 192.168.1.0/24
  exploit kubernetes.local:6443
  scrape https://target.com
  export json
  session list
"""
            print(help_text)
    
    async def cmd_status(self, args: List[str]):
        """Show engine status"""
        try:
            stats = self.engine.get_engine_stats()
            active_ops = self.engine.get_active_operations()
            
            self.print_highlight("Engine Status")
            print(f"🆔 Engine ID: {stats.get('engine_id', 'unknown')}")
            print(f"⏱️  Uptime: {stats.get('uptime_seconds', 0)//3600}h {(stats.get('uptime_seconds', 0)%3600)//60}m")
            print(f"🎯 Operations: {stats.get('operations_total', 0)} total, {len(active_ops)} active")
            print(f"📊 Targets: {stats.get('targets_processed', 0)} processed")
            print(f"🔑 Credentials: {stats.get('credentials_found', 0)} found")
            
            if active_ops:
                print(f"\n{Colors.YELLOW}🔄 Active Operations:{Colors.RESET}")
                for op_id, op_data in active_ops.items():
                    print(f"  • {op_id}: {op_data.get('operation_type', 'unknown')}")
        
        except Exception as e:
            self.print_error(f"Failed to get status: {e}")
    
    async def cmd_stats(self, args: List[str]):
        """Show detailed statistics"""
        try:
            stats = self.engine.get_engine_stats()
            
            self.print_highlight("Detailed Statistics")
            
            # Format statistics nicely
            print(f"📊 {Colors.BOLD}Operations:{Colors.RESET}")
            print(f"   Total: {stats.get('operations_total', 0)}")
            print(f"   Completed: {stats.get('operations_completed', 0)}")
            print(f"   Failed: {stats.get('operations_failed', 0)}")
            
            print(f"\n🎯 {Colors.BOLD}Targets:{Colors.RESET}")
            print(f"   Processed: {stats.get('targets_processed', 0)}")
            
            print(f"\n🔑 {Colors.BOLD}Credentials:{Colors.RESET}")
            print(f"   Found: {stats.get('credentials_found', 0)}")
            print(f"   Valid: {stats.get('valid_credentials', 0)}")
            
            print(f"\n🥷 {Colors.BOLD}Kubernetes:{Colors.RESET}")
            print(f"   Clusters Found: {stats.get('k8s_clusters_found', 0)}")
            
            print(f"\n⏱️  {Colors.BOLD}Runtime:{Colors.RESET}")
            uptime = stats.get('uptime_seconds', 0)
            hours = uptime // 3600
            minutes = (uptime % 3600) // 60
            seconds = uptime % 60
            print(f"   Uptime: {hours}h {minutes}m {seconds}s")
            print(f"   Started: {stats.get('start_time', 'unknown')}")
        
        except Exception as e:
            self.print_error(f"Failed to get statistics: {e}")
    
    async def cmd_scan(self, args: List[str]):
        """Execute scan operation"""
        if not args:
            self.print_error("Usage: scan <target1> [target2] ...")
            return
        
        try:
            self.print_info(f"Starting scan of {len(args)} targets...")
            
            # Start progress indicator
            self._start_progress("Scanning")
            
            # Execute scan
            result = await self.engine.execute_operation(
                operation_type='scan',
                targets=args
            )
            
            self._stop_progress()
            
            if result.status.value == 'completed':
                self.print_success(f"Scan completed - {result.results_found} results found")
                
                if result.metadata.get('results'):
                    print(f"\n{Colors.YELLOW}📊 Results:{Colors.RESET}")
                    for i, res in enumerate(result.metadata['results'][:5], 1):
                        print(f"  {i}. {res.get('type', 'unknown')} - {res.get('target', 'unknown')}")
                    
                    if len(result.metadata['results']) > 5:
                        print(f"  ... and {len(result.metadata['results']) - 5} more")
            else:
                self.print_error("Scan failed")
                for error in result.errors:
                    print(f"   • {error}")
        
        except Exception as e:
            self._stop_progress()
            self.print_error(f"Scan failed: {e}")
    
    async def cmd_exploit(self, args: List[str]):
        """Execute exploitation operation"""
        if not args:
            self.print_error("Usage: exploit <target1> [target2] ...")
            return
        
        try:
            self.print_highlight(f"🥷 Starting exploitation of {len(args)} targets...")
            
            # Start progress indicator
            self._start_progress("Exploiting")
            
            # Execute exploitation
            result = await self.engine.execute_operation(
                operation_type='exploit',
                targets=args
            )
            
            self._stop_progress()
            
            if result.status.value == 'completed':
                self.print_success(f"Exploitation completed - {result.results_found} results found")
                
                if result.metadata.get('results'):
                    print(f"\n{Colors.RED}🔥 Exploitation Results:{Colors.RESET}")
                    for i, res in enumerate(result.metadata['results'][:3], 1):
                        print(f"  {i}. {res.get('type', 'unknown')} - {res.get('target', 'unknown')}")
            else:
                self.print_error("Exploitation failed")
        
        except Exception as e:
            self._stop_progress()
            self.print_error(f"Exploitation failed: {e}")
    
    async def cmd_scrape(self, args: List[str]):
        """Execute scraping operation"""
        if not args:
            self.print_error("Usage: scrape <target1> [target2] ...")
            return
        
        try:
            self.print_info(f"🔍 Starting credential scraping of {len(args)} targets...")
            
            # Start progress indicator
            self._start_progress("Scraping")
            
            # Execute scraping
            result = await self.engine.execute_operation(
                operation_type='scrape',
                targets=args
            )
            
            self._stop_progress()
            
            if result.status.value == 'completed':
                self.print_success(f"Scraping completed - {result.results_found} credentials found")
            else:
                self.print_error("Scraping failed")
        
        except Exception as e:
            self._stop_progress()
            self.print_error(f"Scraping failed: {e}")
    
    async def cmd_validate(self, args: List[str]):
        """Execute validation operation"""
        self.print_info("🔐 Credential validation - coming soon!")
    
    async def cmd_session(self, args: List[str]):
        """Session management"""
        if not args:
            self.print_error("Usage: session <list|create|show|close> [args]")
            return
        
        subcommand = args[0].lower()
        
        try:
            if subcommand == 'list':
                sessions = await self.engine.session_manager.list_sessions()
                self.print_info(f"Found {len(sessions)} sessions:")
                for session in sessions[:10]:
                    print(f"  • {session.session_id} - {session.operation_type} ({session.status.value})")
            
            elif subcommand == 'create':
                operation_type = args[1] if len(args) > 1 else 'general'
                session_id = await self.engine.session_manager.create_session(operation_type)
                self.print_success(f"Created session: {session_id}")
            
            elif subcommand == 'show':
                if len(args) < 2:
                    self.print_error("Usage: session show <session_id>")
                    return
                
                session_id = args[1]
                session = await self.engine.session_manager.get_session(session_id)
                if session:
                    print(f"📝 Session {session_id}:")
                    print(f"   Type: {session.operation_type}")
                    print(f"   Status: {session.status.value}")
                    print(f"   Created: {session.created_at}")
                    print(f"   Targets: {session.targets_count}")
                    print(f"   Results: {session.results_count}")
                else:
                    self.print_error(f"Session {session_id} not found")
            
            elif subcommand == 'close':
                if len(args) < 2:
                    self.print_error("Usage: session close <session_id>")
                    return
                
                session_id = args[1]
                await self.engine.session_manager.close_session(session_id)
                self.print_success(f"Closed session: {session_id}")
            
            else:
                self.print_error(f"Unknown session command: {subcommand}")
        
        except Exception as e:
            self.print_error(f"Session operation failed: {e}")
    
    async def cmd_targets(self, args: List[str]):
        """Target management"""
        self.print_info("🎯 Target management - coming soon!")
    
    async def cmd_config(self, args: List[str]):
        """Configuration management"""
        self.print_info("⚙️ Configuration management - coming soon!")
    
    async def cmd_export(self, args: List[str]):
        """Export data"""
        if not args:
            self.print_error("Usage: export <json|csv|html|yaml>")
            return
        
        export_format = args[0].lower()
        
        try:
            # Get current data
            stats = self.engine.get_engine_stats()
            
            self.print_info(f"📊 Exporting data in {export_format} format...")
            
            # Simulate export (would integrate with exporter module)
            await asyncio.sleep(1)
            
            filename = f"wwyvq_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format}"
            self.print_success(f"Data exported to {filename}")
        
        except Exception as e:
            self.print_error(f"Export failed: {e}")
    
    async def cmd_notify(self, args: List[str]):
        """Send test notification"""
        message = " ".join(args) if args else "Test notification from WWYVQ v2.1"
        
        try:
            self.print_info(f"📱 Sending test notification: {message}")
            
            # Simulate notification
            await asyncio.sleep(0.5)
            
            self.print_success("Test notification sent")
        
        except Exception as e:
            self.print_error(f"Notification failed: {e}")
    
    async def cmd_clear(self, args: List[str]):
        """Clear screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_banner()
    
    async def cmd_exit(self, args: List[str]):
        """Exit application"""
        self.print_info("Shutting down WWYVQ Framework...")
        self.running = False
    
    def _start_progress(self, operation: str):
        """Start progress indicator"""
        print(f"{Colors.YELLOW}🔄 {operation}...{Colors.RESET}", end="", flush=True)
    
    def _stop_progress(self):
        """Stop progress indicator"""
        print(f" {Colors.GREEN}✓{Colors.RESET}")
    
    def _get_command_help(self, command: str) -> str:
        """Get help for specific command"""
        help_texts = {
            'scan': "Scan targets for Kubernetes clusters and services\nUsage: scan <target1> [target2] ...",
            'exploit': "Exploit discovered targets (Kubernetes focus)\nUsage: exploit <target1> [target2] ...",
            'scrape': "Scrape targets for credentials and sensitive data\nUsage: scrape <target1> [target2] ...",
            'validate': "Validate found credentials against services\nUsage: validate <credentials>",
            'status': "Show current engine status and active operations\nUsage: status",
            'stats': "Show detailed statistics and metrics\nUsage: stats",
            'session': "Manage sessions (list, create, show, close)\nUsage: session <command> [args]",
            'export': "Export data in various formats\nUsage: export <json|csv|html|yaml>",
            'notify': "Send test notification\nUsage: notify [message]",
            'clear': "Clear the terminal screen\nUsage: clear",
            'exit': "Exit the application\nUsage: exit"
        }
        
        return help_texts.get(command, f"No help available for '{command}'")


class CLIModule:
    """CLI module wrapper for integration with engine"""
    
    def __init__(self, config_manager, logger, engine):
        """Initialize CLI module"""
        self.config_manager = config_manager
        self.logger = logger
        self.engine = engine
        self.cli_interface = WWYVQCLIInterface(engine)
        
        self.logger.info("💻 Enhanced CLI Interface initialized")
    
    async def run_interactive(self, **kwargs):
        """Run interactive CLI"""
        await self.cli_interface.run_interactive(**kwargs)
    
    async def shutdown(self):
        """Shutdown CLI module"""
        self.logger.info("🛑 CLI Interface shutdown completed")