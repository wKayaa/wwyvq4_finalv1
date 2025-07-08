#!/usr/bin/env python3
"""
WWYVQ Framework v2 - Main Entry Point
Author: wKayaa
Date: 2025-01-15

Point d'entrée principal du framework WWYVQ v2.
"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import List, Optional

# Ajout du chemin vers le framework
sys.path.insert(0, str(Path(__file__).parent))

from wwyvq_v2.core import WWYVQEngine, ConfigurationManager, SessionManager, TargetManager, WWYVQLogger
from wwyvq_v2.core.engine import ExecutionMode
from wwyvq_v2.interfaces.cli import WWYVQCLIInterface


def create_parser() -> argparse.ArgumentParser:
    """Crée le parseur d'arguments"""
    parser = argparse.ArgumentParser(
        description="WWYVQ Framework v2 - Advanced Kubernetes Security Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan standard
  python wwyvq.py scan --targets targets.txt

  # Exploitation agressive
  python wwyvq.py exploit --targets targets.txt --mode aggressive --concurrent 200

  # Validation uniquement
  python wwyvq.py validate --credentials creds.json

  # Interface web
  python wwyvq.py web --port 8080

  # Configuration
  python wwyvq.py config --profile production
        """
    )
    
    # Sous-commandes
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Commande scan
    scan_parser = subparsers.add_parser('scan', help='Scan for Kubernetes clusters')
    scan_parser.add_argument('--targets', '-t', required=True, help='Targets file or CIDR')
    scan_parser.add_argument('--mode', '-m', choices=['passive', 'standard', 'aggressive'], 
                           default='standard', help='Scan mode')
    scan_parser.add_argument('--concurrent', '-c', type=int, default=100, 
                           help='Concurrent connections')
    scan_parser.add_argument('--timeout', type=int, default=30, help='Timeout per target')
    scan_parser.add_argument('--output', '-o', help='Output file')
    
    # Commande exploit
    exploit_parser = subparsers.add_parser('exploit', help='Exploit Kubernetes clusters')
    exploit_parser.add_argument('--targets', '-t', required=True, help='Targets file or CIDR')
    exploit_parser.add_argument('--mode', '-m', choices=['passive', 'standard', 'aggressive'], 
                               default='standard', help='Exploit mode')
    exploit_parser.add_argument('--concurrent', '-c', type=int, default=50, 
                               help='Concurrent connections')
    exploit_parser.add_argument('--stealth', action='store_true', help='Stealth mode')
    exploit_parser.add_argument('--no-deploy', action='store_true', help='No pod deployment')
    exploit_parser.add_argument('--output', '-o', help='Output directory')
    
    # Commande validate
    validate_parser = subparsers.add_parser('validate', help='Validate credentials')
    validate_parser.add_argument('--credentials', '-c', required=True, help='Credentials file')
    validate_parser.add_argument('--services', '-s', help='Services to validate')
    validate_parser.add_argument('--concurrent', type=int, default=10, help='Concurrent validations')
    validate_parser.add_argument('--output', '-o', help='Output file')
    
    # Commande web
    web_parser = subparsers.add_parser('web', help='Start web interface')
    web_parser.add_argument('--port', '-p', type=int, default=8080, help='Web server port')
    web_parser.add_argument('--host', default='127.0.0.1', help='Web server host')
    web_parser.add_argument('--debug', action='store_true', help='Debug mode')
    
    # Commande config
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument('--profile', help='Load configuration profile')
    config_parser.add_argument('--create-profile', help='Create new profile')
    config_parser.add_argument('--show', action='store_true', help='Show current configuration')
    config_parser.add_argument('--validate', action='store_true', help='Validate configuration')
    config_parser.add_argument('--reset', action='store_true', help='Reset to defaults')
    
    # Options globales
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Log level')
    parser.add_argument('--session-id', help='Session ID to restore')
    parser.add_argument('--safe-mode', action='store_true', help='Enable safe mode')
    parser.add_argument('--version', action='version', version='WWYVQ Framework v2.0.0')
    
    return parser


async def main():
    """Fonction principale"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialisation du moteur
    engine = WWYVQEngine(args.config)
    
    # Configuration du niveau de log
    if hasattr(args, 'log_level'):
        engine.logger.set_level(args.log_level)
    
    # Mode sécurisé
    if args.safe_mode:
        engine.config_manager.update_config({
            'core': {'safe_mode': True}
        })
    
    # Initialisation
    if not await engine.initialize():
        print("❌ Failed to initialize WWYVQ Engine")
        sys.exit(1)
    
    try:
        # Gestion des commandes
        if args.command == 'scan':
            await handle_scan_command(engine, args)
        elif args.command == 'exploit':
            await handle_exploit_command(engine, args)
        elif args.command == 'validate':
            await handle_validate_command(engine, args)
        elif args.command == 'web':
            await handle_web_command(engine, args)
        elif args.command == 'config':
            await handle_config_command(engine, args)
        else:
            print(f"❌ Unknown command: {args.command}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⏹️ Operation interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    finally:
        await engine.shutdown()


async def handle_scan_command(engine: WWYVQEngine, args):
    """Gestion de la commande scan"""
    print(f"🔍 Starting scan operation...")
    
    # Chargement des cibles
    targets = load_targets(args.targets)
    
    # Configuration du mode
    mode = ExecutionMode(args.mode)
    
    # Exécution du scan
    result = await engine.execute_operation(
        operation_type='scan',
        targets=targets,
        mode=mode,
        concurrent=args.concurrent,
        timeout=args.timeout,
        output=args.output
    )
    
    print(f"✅ Scan completed: {result.operation_id}")
    print_operation_summary(result)


async def handle_exploit_command(engine: WWYVQEngine, args):
    """Gestion de la commande exploit"""
    print(f"🚀 Starting exploit operation...")
    
    # Chargement des cibles
    targets = load_targets(args.targets)
    
    # Configuration du mode
    mode = ExecutionMode(args.mode)
    
    # Exécution de l'exploitation
    result = await engine.execute_operation(
        operation_type='exploit',
        targets=targets,
        mode=mode,
        concurrent=args.concurrent,
        stealth=args.stealth,
        no_deploy=args.no_deploy,
        output=args.output
    )
    
    print(f"✅ Exploit completed: {result.operation_id}")
    print_operation_summary(result)


async def handle_validate_command(engine: WWYVQEngine, args):
    """Gestion de la commande validate"""
    print(f"🔍 Starting validation operation...")
    
    # Chargement des credentials
    credentials = load_credentials(args.credentials)
    
    # Exécution de la validation
    result = await engine.execute_operation(
        operation_type='validate',
        targets=credentials,
        concurrent=args.concurrent,
        services=args.services,
        output=args.output
    )
    
    print(f"✅ Validation completed: {result.operation_id}")
    print_operation_summary(result)


async def handle_web_command(engine: WWYVQEngine, args):
    """Gestion de la commande web"""
    print(f"🌐 Starting web interface...")
    
    # Import de l'interface web
    try:
        from wwyvq_v2.interfaces.web import WWYVQWebInterface
        
        web_interface = WWYVQWebInterface(engine)
        await web_interface.start(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
        
    except ImportError:
        print("❌ Web interface not available")
        sys.exit(1)


async def handle_config_command(engine: WWYVQEngine, args):
    """Gestion de la commande config"""
    config_manager = engine.config_manager
    
    if args.profile:
        config_manager.load_profile(args.profile)
        print(f"✅ Profile '{args.profile}' loaded")
    
    elif args.create_profile:
        # Création d'un profil interactif
        print(f"Creating profile '{args.create_profile}'...")
        # TODO: Implémenter la création interactive
        
    elif args.show:
        # Affichage de la configuration
        config = config_manager.get_config()
        print("\n📋 Current Configuration:")
        print(f"  Version: {config.version}")
        print(f"  Safe Mode: {config.core.safe_mode}")
        print(f"  Max Concurrent: {config.core.max_concurrent}")
        print(f"  Timeout: {config.core.timeout}")
        
    elif args.validate:
        # Validation de la configuration
        if config_manager.validate_config():
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration validation failed")
            sys.exit(1)
    
    elif args.reset:
        # Reset à la configuration par défaut
        config_manager.reset_to_defaults()
        print("🔄 Configuration reset to defaults")
    
    else:
        print("❌ No configuration action specified")


def load_targets(targets_input: str) -> List[str]:
    """Charge les cibles depuis un fichier ou une chaîne"""
    if Path(targets_input).exists():
        # Chargement depuis un fichier
        with open(targets_input, 'r', encoding='utf-8') as f:
            targets = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    else:
        # Cibles multiples séparées par des virgules ou cible unique
        if ',' in targets_input:
            targets = [target.strip() for target in targets_input.split(',')]
        else:
            targets = [targets_input]
    
    print(f"📊 Loaded {len(targets)} targets")
    return targets


def load_credentials(credentials_input: str) -> List[str]:
    """Charge les credentials depuis un fichier"""
    if Path(credentials_input).exists():
        with open(credentials_input, 'r', encoding='utf-8') as f:
            import json
            credentials = json.load(f)
    else:
        print(f"❌ Credentials file not found: {credentials_input}")
        sys.exit(1)
    
    print(f"📊 Loaded {len(credentials)} credentials")
    return credentials


def print_operation_summary(result):
    """Affiche le résumé d'une opération"""
    print(f"\n📊 Operation Summary:")
    print(f"  Operation ID: {result.operation_id}")
    print(f"  Type: {result.operation_type}")
    print(f"  Status: {result.status.value}")
    print(f"  Start: {result.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if result.end_time:
        duration = result.end_time - result.start_time
        print(f"  Duration: {duration.total_seconds():.2f} seconds")
    
    if result.results:
        print(f"  Results: {len(result.results)} items")
    
    if result.errors:
        print(f"  Errors: {len(result.errors)}")
        for error in result.errors[:3]:  # Afficher les 3 premières erreurs
            print(f"    - {error}")


if __name__ == "__main__":
    # Vérification de Python 3.7+
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        sys.exit(1)
    
    # Exécution du main
    asyncio.run(main())