#!/usr/bin/env python3
"""
WWYVQV5 - Script principal corrigé
Date: 2025-06-23 20:59:57 UTC
User: wKayaa
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Import local corrigé
from kubernetes_advanced import (
    KubernetesAdvancedExploitation,
    WWYVQv5KubernetesOrchestrator,
    ExploitationConfig,
    ExploitationMode
)

def parse_arguments():
    parser = argparse.ArgumentParser(description="🚀 WWYVQV5 - Kubernetes Exploitation")
    
    parser.add_argument('--target', '-t', help='Cible unique')
    parser.add_argument('--targets', '-f', help='Fichier de cibles')
    parser.add_argument('--mode', '-m', choices=['passive', 'active', 'aggressive'], 
                       default='aggressive', help='Mode d\'exploitation')
    parser.add_argument('--max-concurrent', type=int, default=100)
    parser.add_argument('--timeout', type=int, default=10)
    parser.add_argument('--verbose', '-v', action='store_true')
    
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
    
    # Configuration corrigée
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
    
    # Orchestrateur
    orchestrator = WWYVQv5KubernetesOrchestrator()
    await orchestrator.initialize(config)
    
    # Exploitation
    await orchestrator.run_exploitation(targets)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Arrêt demandé")
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
