#!/usr/bin/env python3
"""
🎮 WWYVQV5 ULTIMATE LAUNCHER
Single Command Interface with Intelligent Target Selection

Usage: python ultimate_launcher.py
"""

import asyncio
import sys
from pathlib import Path

# Enhanced imports
try:
    import click
    import rich
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    import questionary
    HAS_ENHANCED_CLI = True
except ImportError:
    HAS_ENHANCED_CLI = False

# Import our ultimate framework
from wwyvq4_ultimate import (
    UltimateKubernetesExploiter,
    EnhancedExploitationConfig,
    ExploitationMode,
    SecurityLevel
)

class UltimateLauncher:
    """Single command launcher with intelligent interface"""
    
    def __init__(self):
        self.console = Console() if HAS_ENHANCED_CLI else None
        
    async def launch(self):
        """Main launcher interface"""
        if self.console:
            await self._enhanced_launch()
        else:
            await self._basic_launch()
    
    async def _enhanced_launch(self):
        """Enhanced launcher with rich interface"""
        # Display welcome banner
        banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║           🚀 WWYVQV5 ULTIMATE LAUNCHER                               ║
║              Single Command - Maximum Power                          ║
║                     Rating: 10/10 ⭐                                 ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

🎯 Ready to launch the ultimate Kubernetes exploitation framework!
🛡️ Enhanced security validation and intelligent targeting included.
        """
        
        self.console.print(Panel(banner, style="bold blue"))
        
        # Quick configuration
        config = await self._quick_configuration()
        
        # Launch framework
        exploiter = UltimateKubernetesExploiter(config)
        await exploiter.run_ultimate_exploitation()
    
    async def _quick_configuration(self):
        """Quick interactive configuration"""
        self.console.print("\n⚙️ Quick Configuration", style="bold cyan")
        
        # Mode selection
        mode_choice = questionary.select(
            "Select exploitation mode:",
            choices=[
                questionary.Choice("🔍 Passive (Detection only)", ExploitationMode.PASSIVE),
                questionary.Choice("🕵️ Reconnaissance (Enhanced discovery)", ExploitationMode.RECONNAISSANCE),
                questionary.Choice("⚡ Active (Standard exploitation)", ExploitationMode.ACTIVE),
                questionary.Choice("🚀 Aggressive (Full capabilities)", ExploitationMode.AGGRESSIVE),
                questionary.Choice("👻 Stealth (Low noise)", ExploitationMode.STEALTH),
                questionary.Choice("🌟 Ultimate (Maximum power)", ExploitationMode.ULTIMATE),
            ]
        ).ask()
        
        # Security level
        security_choice = questionary.select(
            "Select security validation level:",
            choices=[
                questionary.Choice("🔒 Enhanced (Recommended)", SecurityLevel.ENHANCED),
                questionary.Choice("🛡️ Paranoid (Maximum safety)", SecurityLevel.PARANOID),
                questionary.Choice("📋 Standard (Balanced)", SecurityLevel.STANDARD),
                questionary.Choice("⚡ Minimal (Fast)", SecurityLevel.MINIMAL),
            ]
        ).ask()
        
        # Advanced options
        advanced = questionary.confirm("Configure advanced options?").ask()
        
        config = EnhancedExploitationConfig(
            mode=mode_choice,
            security_level=security_choice
        )
        
        if advanced:
            config.max_concurrent_clusters = questionary.text(
                "Maximum concurrent targets:", default="20"
            ).ask()
            config.max_concurrent_clusters = int(config.max_concurrent_clusters)
            
            config.timeout_per_operation = questionary.text(
                "Timeout per operation (seconds):", default="15"
            ).ask()
            config.timeout_per_operation = int(config.timeout_per_operation)
            
            config.cleanup_on_exit = questionary.confirm(
                "Clean up artifacts on exit?", default=True
            ).ask()
        
        return config
    
    async def _basic_launch(self):
        """Basic launcher without enhanced CLI"""
        print("🚀 WWYVQV5 ULTIMATE LAUNCHER - Basic Mode")
        print("="*60)
        
        # Simple configuration
        print("\nModes:")
        print("1. Passive (Detection only)")
        print("2. Active (Standard exploitation)")
        print("3. Aggressive (Full capabilities)")
        print("4. Ultimate (Maximum power)")
        
        mode_choice = input("Select mode (1-4): ").strip()
        mode_map = {
            "1": ExploitationMode.PASSIVE,
            "2": ExploitationMode.ACTIVE,
            "3": ExploitationMode.AGGRESSIVE,
            "4": ExploitationMode.ULTIMATE
        }
        
        mode = mode_map.get(mode_choice, ExploitationMode.ACTIVE)
        
        config = EnhancedExploitationConfig(
            mode=mode,
            security_level=SecurityLevel.ENHANCED
        )
        
        # Launch framework
        exploiter = UltimateKubernetesExploiter(config)
        await exploiter.run_ultimate_exploitation()

async def main():
    """Main entry point"""
    launcher = UltimateLauncher()
    await launcher.launch()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Launch cancelled by user")
    except Exception as e:
        print(f"\n❌ Launch error: {str(e)}")