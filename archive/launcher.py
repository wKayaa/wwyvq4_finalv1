#!/usr/bin/env python3
"""
🚀 AIO EXPLOIT FRAMEWORK LAUNCHER
Author: wKayaa
Date: 2025-06-23 22:47:56 UTC
Repository: wKayaa/wwyvq4_finalv1
"""

import asyncio
import argparse
import threading
import sys
from pathlib import Path

from framework import ModularOrchestrator, WebInterface, APIServer

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='🚀 AIO Exploit/Scan/Check/Export Framework - wKayaa',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python launcher.py --mode scan --file targets_massive_optimized.txt --threads 500
  python launcher.py --mode exploit --threads 1000 --telegram-token YOUR_TOKEN
  python launcher.py --mode all --web --api --threads 800
  python launcher.py --mode mail --file targets_goldmine.txt --threads 200
        '''
    )
    
    # Core options
    parser.add_argument('--mode', choices=['scan', 'exploit', 'mail', 'all'], 
                       default='exploit', help='Operation mode')
    parser.add_argument('--file', '-f', default='targets_massive_optimized.txt',
                       help='Target file path')
    parser.add_argument('--threads', type=int, default=500,
                       help='Number of concurrent threads')
    
    # Interface options
    parser.add_argument('--web', action='store_true',
                       help='Start web interface on port 5000')
    parser.add_argument('--api', action='store_true',
                       help='Start HTTP API server on port 8080')
    
    # Integration options
    parser.add_argument('--telegram-token', help='Telegram bot token')
    parser.add_argument('--telegram-chat', help='Telegram chat ID')
    
    # Output options
    parser.add_argument('--output', '-o', help='Output directory')
    parser.add_argument('--config', '-c', default='framework_config.yaml',
                       help='Configuration file')
    
    return parser.parse_args()

async def main():
    args = parse_arguments()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║               🚀 AIO EXPLOIT FRAMEWORK v1.0                 ║
║                      wKayaa Production                       ║
║               Date: 2025-06-23 22:47:56 UTC                 ║
║               Repository: wKayaa/wwyvq4_finalv1              ║
╚══════════════════════════════════════════════════════════════╝

🎯 Mode: {args.mode.upper()}
📁 Targets: {args.file}
⚡ Threads: {args.threads}
🌐 Web UI: {'✅' if args.web else '❌'}
🔌 HTTP API: {'✅' if args.api else '❌'}
📱 Telegram: {'✅' if args.telegram_token else '❌'}
    """)
    
    # Initialize orchestrator
    orchestrator = ModularOrchestrator(args.config)
    
    # Update config with CLI args
    if args.telegram_token:
        orchestrator.config["integrations"]["telegram_enabled"] = True
        orchestrator.config["integrations"]["telegram_token"] = args.telegram_token
        orchestrator.config["integrations"]["telegram_chat_id"] = args.telegram_chat
    
    orchestrator.config["performance"]["max_threads"] = args.threads
    
    # Start web interface
    if args.web:
        web_interface = WebInterface(orchestrator)
        web_thread = threading.Thread(target=web_interface.run)
        web_thread.daemon = True
        web_thread.start()
        print("🌐 Web interface: http://localhost:5000")
    
    # Start API server
    if args.api:
        api_server = APIServer(orchestrator)
        api_thread = threading.Thread(target=api_server.run)
        api_thread.daemon = True
        api_thread.start()
        print("🔌 HTTP API: http://localhost:8080")
    
    # Load targets
    targets = orchestrator.load_targets(args.file)
    if not targets:
        print("❌ No targets loaded")
        return
    
    print(f"📊 Loaded {len(targets)} targets")
    
    # Execute based on mode
    try:
        if args.mode == 'scan':
            print("🔍 Starting target scanning...")
            # Use your existing scanning logic here
            
        elif args.mode == 'exploit':
            print("⚡ Starting K8s exploitation...")
            results = await orchestrator.run_k8s_exploitation(targets)
            
        elif args.mode == 'mail':
            print("📧 Starting email hunting...")
            results = await orchestrator.run_mail_hunting(targets)
            
        elif args.mode == 'all':
            print("🚀 Starting full exploitation pipeline...")
            results = await orchestrator.run_full_exploitation(targets, 'all')
        
        print("✅ Operation completed successfully")
        
        # Keep running if web/api interfaces are active
        if args.web or args.api:
            print("\n🌐 Interfaces are running. Press Ctrl+C to stop.")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n⏹️ Shutting down...")
        
    except KeyboardInterrupt:
        print("\n⏹️ Operation interrupted by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())