#!/usr/bin/env python3
"""
WWYVQ Framework v2 - CLI Interface
Author: wKayaa
Date: 2025-01-15

Interface ligne de commande avancée avec couleurs et progression.
"""

import sys
import time
from typing import Dict, List, Optional, Any
from datetime import datetime


class WWYVQCLIInterface:
    """Interface CLI avancée pour WWYVQ v2"""
    
    def __init__(self, engine):
        """
        Initialise l'interface CLI
        
        Args:
            engine: Instance du moteur WWYVQ
        """
        self.engine = engine
        self.show_colors = True
        self.progress_shown = False
        
        # Codes couleurs ANSI
        self.colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'reset': '\033[0m'
        }
    
    def print_banner(self):
        """Affiche le banner du framework"""
        banner = f"""
{self.colors['cyan']}{self.colors['bold']}
╔══════════════════════════════════════════════════════════════════════════════════╗
║                          🚀 WWYVQ FRAMEWORK v2                                 ║
║                     Advanced Kubernetes Security Framework                      ║
║                                                                                  ║
║                           Author: wKayaa                                        ║
║                          Production Ready                                       ║
╚══════════════════════════════════════════════════════════════════════════════════╝
{self.colors['reset']}"""
        print(banner)
    
    def print_info(self, message: str, prefix: str = "ℹ️"):
        """Affiche un message d'information"""
        color = self.colors['blue'] if self.show_colors else ''
        reset = self.colors['reset'] if self.show_colors else ''
        print(f"{color}{prefix} {message}{reset}")
    
    def print_success(self, message: str, prefix: str = "✅"):
        """Affiche un message de succès"""
        color = self.colors['green'] if self.show_colors else ''
        reset = self.colors['reset'] if self.show_colors else ''
        print(f"{color}{prefix} {message}{reset}")
    
    def print_warning(self, message: str, prefix: str = "⚠️"):
        """Affiche un message d'avertissement"""
        color = self.colors['yellow'] if self.show_colors else ''
        reset = self.colors['reset'] if self.show_colors else ''
        print(f"{color}{prefix} {message}{reset}")
    
    def print_error(self, message: str, prefix: str = "❌"):
        """Affiche un message d'erreur"""
        color = self.colors['red'] if self.show_colors else ''
        reset = self.colors['reset'] if self.show_colors else ''
        print(f"{color}{prefix} {message}{reset}")
    
    def print_highlight(self, message: str, prefix: str = "🔥"):
        """Affiche un message en surbrillance"""
        color = self.colors['magenta'] + self.colors['bold'] if self.show_colors else ''
        reset = self.colors['reset'] if self.show_colors else ''
        print(f"{color}{prefix} {message}{reset}")
    
    def show_progress(self, current: int, total: int, operation: str):
        """Affiche une barre de progression"""
        if total == 0:
            return
        
        percent = (current / total) * 100
        bar_length = 50
        filled_length = int(bar_length * current / total)
        
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Effacement de la ligne précédente
        if self.progress_shown:
            print('\r', end='')
        
        progress_text = f"📊 {operation}: |{bar}| {percent:.1f}% ({current}/{total})"
        print(progress_text, end='', flush=True)
        self.progress_shown = True
    
    def clear_progress(self):
        """Efface la ligne de progression"""
        if self.progress_shown:
            print('\r' + ' ' * 100 + '\r', end='')
            self.progress_shown = False
    
    def print_statistics(self, stats: Dict[str, Any]):
        """Affiche les statistiques"""
        print(f"\n{self.colors['cyan']}{self.colors['bold']}📊 Statistics:{self.colors['reset']}")
        
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for subkey, subvalue in value.items():
                    print(f"    {subkey}: {subvalue}")
            else:
                print(f"  {key}: {value}")
    
    def print_results_table(self, results: List[Dict[str, Any]], headers: List[str]):
        """Affiche les résultats sous forme de tableau"""
        if not results:
            self.print_info("No results to display")
            return
        
        # Calcul des largeurs de colonnes
        col_widths = {}
        for header in headers:
            col_widths[header] = len(header)
        
        for result in results:
            for header in headers:
                if header in result:
                    col_widths[header] = max(col_widths[header], len(str(result[header])))
        
        # Affichage du header
        header_line = "│ " + " │ ".join(
            header.ljust(col_widths[header]) for header in headers
        ) + " │"
        
        separator = "├" + "┼".join("─" * (col_widths[header] + 2) for header in headers) + "┤"
        top_line = "┌" + "┬".join("─" * (col_widths[header] + 2) for header in headers) + "┐"
        bottom_line = "└" + "┴".join("─" * (col_widths[header] + 2) for header in headers) + "┘"
        
        print(f"\n{self.colors['cyan']}{top_line}{self.colors['reset']}")
        print(f"{self.colors['cyan']}{header_line}{self.colors['reset']}")
        print(f"{self.colors['cyan']}{separator}{self.colors['reset']}")
        
        # Affichage des résultats
        for result in results:
            row_line = "│ " + " │ ".join(
                str(result.get(header, "")).ljust(col_widths[header]) for header in headers
            ) + " │"
            print(row_line)
        
        print(f"{self.colors['cyan']}{bottom_line}{self.colors['reset']}")
    
    def prompt_user(self, message: str, default: Optional[str] = None) -> str:
        """Demande une entrée utilisateur"""
        prompt = f"{self.colors['yellow']}❓ {message}{self.colors['reset']}"
        if default:
            prompt += f" [{default}]"
        prompt += ": "
        
        try:
            response = input(prompt).strip()
            return response if response else (default or "")
        except KeyboardInterrupt:
            print(f"\n{self.colors['red']}⏹️ Operation cancelled{self.colors['reset']}")
            sys.exit(1)
    
    def confirm(self, message: str, default: bool = False) -> bool:
        """Demande une confirmation"""
        default_str = "Y/n" if default else "y/N"
        response = self.prompt_user(f"{message} ({default_str})", "y" if default else "n")
        
        if response.lower() in ['y', 'yes', 'true', '1']:
            return True
        elif response.lower() in ['n', 'no', 'false', '0']:
            return False
        else:
            return default
    
    def select_option(self, message: str, options: List[str]) -> int:
        """Permet de sélectionner une option"""
        print(f"\n{self.colors['yellow']}❓ {message}{self.colors['reset']}")
        
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        
        while True:
            try:
                response = self.prompt_user("Select option (number)")
                index = int(response) - 1
                
                if 0 <= index < len(options):
                    return index
                else:
                    self.print_error("Invalid option number")
            except ValueError:
                self.print_error("Please enter a valid number")
    
    def show_operation_status(self, operation_id: str):
        """Affiche le statut d'une opération en temps réel"""
        print(f"\n{self.colors['cyan']}📊 Operation Status: {operation_id}{self.colors['reset']}")
        
        last_update = time.time()
        
        while True:
            try:
                # Récupération du statut
                status = self.engine.get_operation_status(operation_id)
                
                if not status:
                    self.print_error(f"Operation {operation_id} not found")
                    break
                
                # Affichage du statut
                current_time = time.time()
                if current_time - last_update > 1:  # Mise à jour chaque seconde
                    self.clear_progress()
                    
                    status_color = {
                        'pending': self.colors['yellow'],
                        'running': self.colors['blue'],
                        'completed': self.colors['green'],
                        'failed': self.colors['red'],
                        'cancelled': self.colors['magenta']
                    }.get(status.status.value, self.colors['white'])
                    
                    print(f"\r{status_color}Status: {status.status.value.upper()}{self.colors['reset']}", end='')
                    
                    if status.status.value == 'running':
                        # Affichage de progression si disponible
                        if 'progress' in status.metadata:
                            progress = status.metadata['progress']
                            self.show_progress(progress['current'], progress['total'], 'Processing')
                    
                    last_update = current_time
                
                # Vérification de fin
                if status.status.value in ['completed', 'failed', 'cancelled']:
                    self.clear_progress()
                    print(f"\n{self.colors['green']}✅ Operation {status.status.value}{self.colors['reset']}")
                    break
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                self.clear_progress()
                print(f"\n{self.colors['yellow']}⏹️ Status monitoring stopped{self.colors['reset']}")
                break
    
    def interactive_session(self):
        """Session interactive"""
        self.print_banner()
        self.print_info("Welcome to WWYVQ Framework v2 Interactive Session")
        self.print_info("Type 'help' for available commands, 'exit' to quit")
        
        while True:
            try:
                command = self.prompt_user("wwyvq>").strip()
                
                if not command:
                    continue
                
                if command.lower() in ['exit', 'quit', 'q']:
                    self.print_info("Goodbye!")
                    break
                
                elif command.lower() == 'help':
                    self.show_help()
                
                elif command.lower() == 'status':
                    self.show_engine_status()
                
                elif command.lower() == 'stats':
                    stats = self.engine.get_engine_stats()
                    self.print_statistics(stats)
                
                elif command.lower().startswith('scan '):
                    # Commande de scan rapide
                    target = command[5:].strip()
                    if target:
                        self.print_info(f"Scanning target: {target}")
                        # TODO: Lancer le scan
                    else:
                        self.print_error("Please specify a target")
                
                else:
                    self.print_error(f"Unknown command: {command}")
                    self.print_info("Type 'help' for available commands")
            
            except KeyboardInterrupt:
                print()
                continue
            except EOFError:
                print()
                break
    
    def show_help(self):
        """Affiche l'aide"""
        help_text = f"""
{self.colors['cyan']}{self.colors['bold']}Available Commands:{self.colors['reset']}
  help                 - Show this help message
  status               - Show engine status
  stats                - Show engine statistics
  scan <target>        - Quick scan of target
  exit/quit/q          - Exit interactive session

{self.colors['cyan']}{self.colors['bold']}Examples:{self.colors['reset']}
  scan 192.168.1.0/24  - Scan CIDR range
  scan example.com     - Scan single host
"""
        print(help_text)
    
    def show_engine_status(self):
        """Affiche le statut du moteur"""
        stats = self.engine.get_engine_stats()
        
        print(f"\n{self.colors['cyan']}{self.colors['bold']}🔧 Engine Status:{self.colors['reset']}")
        print(f"  Engine ID: {stats['engine_id']}")
        print(f"  Status: {stats['status']}")
        print(f"  Uptime: {stats['uptime_seconds']:.2f} seconds")
        print(f"  Active Operations: {stats['active_operations']}")
        print(f"  Modules Loaded: {stats['modules_loaded']}")
        print(f"  Operations Completed: {stats['operations_completed']}")
        print(f"  Operations Failed: {stats['operations_failed']}")
    
    def disable_colors(self):
        """Désactive les couleurs"""
        self.show_colors = False
        for key in self.colors:
            self.colors[key] = ''