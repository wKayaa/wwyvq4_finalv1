#!/usr/bin/env python3
"""
🎯 Mega CIDR UHQ List - Ultra-Comprehensive CIDR Database
Author: wKayaa | F8S Pod Exploitation Framework | 2025-01-28

Ultra-comprehensive CIDR list for Kubernetes cluster discovery with:
- 10 major categories with 2000+ ranges
- Intelligent prioritization and scanning strategies
- Geolocation-based targeting
- Stealth mode considerations
- Integration with F8S framework
"""

import json
import ipaddress
import random
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import datetime

@dataclass
class CIDRTarget:
    """Represents a CIDR target with metadata"""
    cidr: str
    category: str
    priority: int
    likelihood: int
    stealth_required: bool
    scan_intensity: str
    organization_type: str
    geographic_region: str
    common_ports: List[int] = field(default_factory=list)
    ipv6: bool = False
    warning: Optional[str] = None

@dataclass
class ScanStrategy:
    """Scanning strategy configuration"""
    concurrent_limit: int
    timeout: int
    retry_count: int
    requires_explicit_consent: bool = False

class MegaCIDRUHQ:
    """Ultra-comprehensive CIDR database and management system"""
    
    def __init__(self, config_path: str = "cidr_categories.json"):
        self.config_path = config_path
        self.categories_data = {}
        self.targets = []
        self.strategies = {}
        self.load_configuration()
        self.generate_targets()
    
    def load_configuration(self):
        """Load CIDR categories configuration"""
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                self.categories_data = data.get('categories', {})
                self.strategies = data.get('scanning_strategies', {})
                self.geographic_regions = data.get('geographic_regions', {})
                print(f"✅ Loaded {len(self.categories_data)} CIDR categories")
        except FileNotFoundError:
            print(f"❌ Configuration file {self.config_path} not found")
            raise
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in configuration file: {e}")
            raise
    
    def generate_targets(self):
        """Generate all CIDR targets with metadata"""
        self.targets = []
        
        for category_name, category_data in self.categories_data.items():
            # Process IPv4 ranges
            for cidr in category_data.get('ipv4_ranges', []):
                target = CIDRTarget(
                    cidr=cidr,
                    category=category_name,
                    priority=category_data.get('priority', 5),
                    likelihood=category_data.get('metadata', {}).get('likelihood', 5),
                    stealth_required=category_data.get('stealth_required', False),
                    scan_intensity=category_data.get('scan_intensity', 'moderate'),
                    organization_type=category_data.get('metadata', {}).get('organization_types', ['unknown'])[0],
                    geographic_region=category_data.get('metadata', {}).get('geographic_distribution', 'unknown'),
                    common_ports=category_data.get('metadata', {}).get('common_ports', []),
                    ipv6=False,
                    warning=category_data.get('metadata', {}).get('warning')
                )
                self.targets.append(target)
            
            # Process IPv6 ranges
            for cidr in category_data.get('ipv6_ranges', []):
                target = CIDRTarget(
                    cidr=cidr,
                    category=category_name,
                    priority=category_data.get('priority', 5),
                    likelihood=category_data.get('metadata', {}).get('likelihood', 5),
                    stealth_required=category_data.get('stealth_required', False),
                    scan_intensity=category_data.get('scan_intensity', 'moderate'),
                    organization_type=category_data.get('metadata', {}).get('organization_types', ['unknown'])[0],
                    geographic_region=category_data.get('metadata', {}).get('geographic_distribution', 'unknown'),
                    common_ports=category_data.get('metadata', {}).get('common_ports', []),
                    ipv6=True,
                    warning=category_data.get('metadata', {}).get('warning')
                )
                self.targets.append(target)
        
        print(f"✅ Generated {len(self.targets)} total CIDR targets")
    
    def get_targets_by_priority(self, min_priority: int = 1, max_priority: int = 10) -> List[CIDRTarget]:
        """Get targets filtered by priority range"""
        return [t for t in self.targets if min_priority <= t.priority <= max_priority]
    
    def get_targets_by_category(self, categories: List[str]) -> List[CIDRTarget]:
        """Get targets filtered by category"""
        return [t for t in self.targets if t.category in categories]
    
    def get_targets_by_region(self, region: str) -> List[CIDRTarget]:
        """Get targets filtered by geographic region"""
        if region not in self.geographic_regions:
            return []
        
        relevant_categories = self.geographic_regions[region]
        return self.get_targets_by_category(relevant_categories)
    
    def get_high_probability_targets(self, min_likelihood: int = 7) -> List[CIDRTarget]:
        """Get high-probability targets for maximum success rate"""
        return [t for t in self.targets if t.likelihood >= min_likelihood]
    
    def get_stealth_safe_targets(self) -> List[CIDRTarget]:
        """Get targets that don't require stealth mode"""
        return [t for t in self.targets if not t.stealth_required]
    
    def get_aggressive_scan_targets(self) -> List[CIDRTarget]:
        """Get targets suitable for aggressive scanning"""
        return [t for t in self.targets if t.scan_intensity == 'aggressive' and not t.stealth_required]
    
    def prioritize_targets(self, targets: List[CIDRTarget]) -> List[CIDRTarget]:
        """Sort targets by priority and likelihood"""
        return sorted(targets, key=lambda t: (t.priority, t.likelihood), reverse=True)
    
    def get_scanning_strategy(self, category: str) -> Optional[ScanStrategy]:
        """Get scanning strategy for a category"""
        for strategy_name, strategy_data in self.strategies.items():
            if category in strategy_data.get('categories', []):
                return ScanStrategy(
                    concurrent_limit=strategy_data.get('concurrent_limit', 50),
                    timeout=strategy_data.get('timeout', 10),
                    retry_count=strategy_data.get('retry_count', 1),
                    requires_explicit_consent=strategy_data.get('requires_explicit_consent', False)
                )
        
        # Default strategy
        return ScanStrategy(concurrent_limit=50, timeout=10, retry_count=1)
    
    def expand_cidr_to_ips(self, cidr: str, max_ips: int = 1000) -> List[str]:
        """Expand CIDR to individual IP addresses"""
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            ips = []
            count = 0
            
            for ip in network.hosts():
                if count >= max_ips:
                    break
                ips.append(str(ip))
                count += 1
            
            return ips
        except ValueError as e:
            print(f"❌ Invalid CIDR {cidr}: {e}")
            return []
    
    def generate_optimized_target_list(self, 
                                     priority_threshold: int = 7,
                                     max_targets: int = 5000,
                                     include_ipv6: bool = False,
                                     stealth_mode: bool = False) -> List[str]:
        """Generate optimized target list for scanning"""
        
        # Filter targets based on criteria
        filtered_targets = self.targets
        
        if not include_ipv6:
            filtered_targets = [t for t in filtered_targets if not t.ipv6]
        
        if stealth_mode:
            filtered_targets = [t for t in filtered_targets if not t.stealth_required]
        
        # Filter by priority
        filtered_targets = [t for t in filtered_targets if t.priority >= priority_threshold]
        
        # Prioritize targets
        prioritized_targets = self.prioritize_targets(filtered_targets)
        
        # Generate IP list
        target_ips = []
        for target in prioritized_targets:
            if len(target_ips) >= max_targets:
                break
            
            # Expand CIDR to IPs
            ips = self.expand_cidr_to_ips(target.cidr, max_ips=100)
            target_ips.extend(ips)
        
        return target_ips[:max_targets]
    
    def get_category_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for each category"""
        stats = {}
        
        for category in self.categories_data.keys():
            category_targets = [t for t in self.targets if t.category == category]
            ipv4_count = len([t for t in category_targets if not t.ipv6])
            ipv6_count = len([t for t in category_targets if t.ipv6])
            
            stats[category] = {
                'total_ranges': len(category_targets),
                'ipv4_ranges': ipv4_count,
                'ipv6_ranges': ipv6_count,
                'priority': category_targets[0].priority if category_targets else 0,
                'stealth_required': category_targets[0].stealth_required if category_targets else False,
                'scan_intensity': category_targets[0].scan_intensity if category_targets else 'unknown'
            }
        
        return stats
    
    def export_targets_for_f8s(self, output_file: str, **kwargs):
        """Export targets in F8S-compatible format"""
        targets = self.generate_optimized_target_list(**kwargs)
        
        with open(output_file, 'w') as f:
            f.write("# F8S Mega CIDR UHQ Target List\n")
            f.write(f"# Generated: {datetime.datetime.now().isoformat()}\n")
            f.write(f"# Total targets: {len(targets)}\n")
            f.write("# Ultra-comprehensive Kubernetes cluster discovery\n\n")
            
            for target in targets:
                f.write(f"{target}\n")
        
        print(f"✅ Exported {len(targets)} targets to {output_file}")
        return targets
    
    def print_summary(self):
        """Print comprehensive summary of CIDR database"""
        print("\n🎯 MEGA CIDR UHQ DATABASE SUMMARY")
        print("=" * 50)
        
        stats = self.get_category_statistics()
        total_targets = sum(s['total_ranges'] for s in stats.values())
        total_ipv4 = sum(s['ipv4_ranges'] for s in stats.values())
        total_ipv6 = sum(s['ipv6_ranges'] for s in stats.values())
        
        print(f"📊 Total CIDR ranges: {total_targets}")
        print(f"🌐 IPv4 ranges: {total_ipv4}")
        print(f"🌐 IPv6 ranges: {total_ipv6}")
        print(f"📁 Categories: {len(stats)}")
        
        print("\n📈 CATEGORY BREAKDOWN:")
        for category, data in stats.items():
            status = "🔒" if data['stealth_required'] else "🔓"
            intensity = data['scan_intensity'].upper()
            print(f"  {status} {category}: {data['total_ranges']} ranges (Priority: {data['priority']}, {intensity})")
        
        print("\n🚀 HIGH-PRIORITY TARGETS:")
        high_priority = self.get_targets_by_priority(min_priority=8)
        print(f"  🎯 {len(high_priority)} high-priority ranges")
        
        high_prob = self.get_high_probability_targets()
        print(f"  💎 {len(high_prob)} high-probability targets")
        
        stealth_safe = self.get_stealth_safe_targets()
        print(f"  🛡️ {len(stealth_safe)} stealth-safe targets")
        
        print("\n⚠️  SECURITY WARNINGS:")
        warning_targets = [t for t in self.targets if t.warning]
        for target in warning_targets[:5]:  # Show first 5
            print(f"  ⚠️  {target.category}: {target.warning}")

def main():
    """Main function for testing and demonstration"""
    print("🚀 Initializing Mega CIDR UHQ System...")
    
    # Initialize the system
    mega_cidr = MegaCIDRUHQ()
    
    # Print summary
    mega_cidr.print_summary()
    
    # Generate optimized target lists
    print("\n🎯 GENERATING OPTIMIZED TARGET LISTS...")
    
    # High-priority, stealth-safe targets
    stealth_targets = mega_cidr.generate_optimized_target_list(
        priority_threshold=8,
        max_targets=1000,
        stealth_mode=True,
        include_ipv6=False
    )
    mega_cidr.export_targets_for_f8s("mega_uhq_stealth.txt", 
                                    priority_threshold=8, 
                                    max_targets=1000, 
                                    stealth_mode=True)
    
    # Aggressive scan targets
    aggressive_targets = mega_cidr.generate_optimized_target_list(
        priority_threshold=9,
        max_targets=2000,
        stealth_mode=False,
        include_ipv6=False
    )
    mega_cidr.export_targets_for_f8s("mega_uhq_aggressive.txt",
                                    priority_threshold=9,
                                    max_targets=2000,
                                    stealth_mode=False)
    
    # Comprehensive list
    comprehensive_targets = mega_cidr.generate_optimized_target_list(
        priority_threshold=5,
        max_targets=5000,
        stealth_mode=False,
        include_ipv6=True
    )
    mega_cidr.export_targets_for_f8s("mega_uhq_comprehensive.txt",
                                    priority_threshold=5,
                                    max_targets=5000,
                                    stealth_mode=False,
                                    include_ipv6=True)
    
    print(f"\n✅ Generated {len(stealth_targets)} stealth targets")
    print(f"✅ Generated {len(aggressive_targets)} aggressive targets") 
    print(f"✅ Generated {len(comprehensive_targets)} comprehensive targets")
    
    print("\n🎯 MEGA CIDR UHQ SYSTEM READY FOR F8S INTEGRATION!")

if __name__ == "__main__":
    main()