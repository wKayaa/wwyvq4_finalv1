#!/usr/bin/env python3
"""
🌐 Massive CIDR Generator for 6-Hour Hunt
Generate comprehensive target lists for maximum coverage
"""

import ipaddress
import random
from pathlib import Path

class MassiveCIDRGenerator:
    def __init__(self):
        self.cloud_ranges = {
            # AWS IP Ranges (principales régions)
            "aws": [
                "13.32.0.0/15", "13.224.0.0/14", "13.248.0.0/16",
                "15.177.0.0/18", "15.200.0.0/16", "18.130.0.0/16",
                "18.144.0.0/15", "18.188.0.0/16", "18.208.0.0/13",
                "3.80.0.0/12", "3.208.0.0/12", "34.192.0.0/12",
                "35.152.0.0/16", "35.160.0.0/13", "44.192.0.0/11",
                "52.0.0.0/11", "52.32.0.0/11", "52.64.0.0/12",
                "54.64.0.0/11", "54.144.0.0/12", "54.224.0.0/12"
            ],
            
            # Google Cloud Platform
            "gcp": [
                "8.8.8.0/24", "8.8.4.0/24", "8.34.208.0/20",
                "8.35.192.0/20", "23.236.48.0/20", "23.251.128.0/19",
                "34.64.0.0/10", "35.184.0.0/13", "35.192.0.0/14",
                "35.196.0.0/15", "35.198.0.0/16", "35.199.0.0/17",
                "104.154.0.0/15", "104.196.0.0/14", "107.167.160.0/19",
                "107.178.192.0/18", "130.211.0.0/22", "146.148.0.0/17"
            ],
            
            # Microsoft Azure
            "azure": [
                "13.64.0.0/11", "13.96.0.0/13", "13.104.0.0/14",
                "20.0.0.0/8", "23.96.0.0/13", "40.64.0.0/10",
                "52.96.0.0/12", "52.112.0.0/14", "52.120.0.0/14",
                "52.224.0.0/11", "65.52.0.0/14", "70.37.0.0/17",
                "104.40.0.0/13", "137.116.0.0/16", "138.91.0.0/16",
                "191.232.0.0/13", "207.68.128.0/18"
            ],
            
            # DigitalOcean
            "digitalocean": [
                "104.131.0.0/16", "107.170.0.0/16", "128.199.0.0/16",
                "134.209.0.0/16", "138.197.0.0/16", "138.68.0.0/16",
                "139.59.0.0/16", "142.93.0.0/16", "143.110.0.0/16",
                "146.190.0.0/16", "157.230.0.0/16", "159.65.0.0/16",
                "159.89.0.0/16", "161.35.0.0/16", "164.90.0.0/16",
                "165.22.0.0/16", "167.71.0.0/16", "167.99.0.0/16"
            ],
            
            # Vultr
            "vultr": [
                "45.32.0.0/16", "45.63.0.0/16", "45.76.0.0/16",
                "66.42.0.0/16", "95.179.0.0/16", "104.156.224.0/19",
                "108.61.0.0/16", "136.244.96.0/19", "140.82.0.0/16",
                "144.202.0.0/16", "149.28.0.0/16", "155.138.128.0/17",
                "192.81.208.0/20", "198.13.32.0/19", "207.148.64.0/18"
            ]
        }
        
        # Corporate/Enterprise ranges (communes)
        self.enterprise_ranges = [
            "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
            "100.64.0.0/10",  # Carrier-grade NAT
        ]
        
        # Internet ranges avec probabilité haute de K8s
        self.internet_ranges = [
            "1.1.1.0/24", "1.0.0.0/24",  # Cloudflare
            "8.8.8.0/24",  # Google DNS
            "208.67.222.0/24",  # OpenDNS
            "185.199.108.0/22",  # GitHub Pages
            "151.101.0.0/16",  # Fastly CDN
            "199.232.0.0/16",  # Akamai
        ]

    def generate_massive_targets(self, output_file="targets_massive_6h.txt"):
        """Generate massive target list for 6-hour hunt"""
        all_targets = []
        
        print("🌐 Generating massive CIDR target list...")
        
        # Cloud provider ranges
        for provider, ranges in self.cloud_ranges.items():
            print(f"📡 Adding {provider.upper()} ranges: {len(ranges)} subnets")
            all_targets.extend(ranges)
        
        # Enterprise ranges (subdivided for better coverage)
        print("🏢 Adding enterprise ranges...")
        for base_range in self.enterprise_ranges:
            network = ipaddress.IPv4Network(base_range)
            # Subdivide into /22 for better scanning
            if network.prefixlen <= 20:
                subnets = list(network.subnets(new_prefix=22))
                all_targets.extend([str(subnet) for subnet in subnets[:100]])  # Limit per range
            else:
                all_targets.append(base_range)
        
        # Internet ranges
        print("🌍 Adding internet ranges...")
        all_targets.extend(self.internet_ranges)
        
        # Generate additional random ranges (for comprehensive coverage)
        print("🎲 Generating additional discovery ranges...")
        additional_ranges = self._generate_discovery_ranges(500)
        all_targets.extend(additional_ranges)
        
        # Remove duplicates and shuffle
        unique_targets = list(set(all_targets))
        random.shuffle(unique_targets)
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write(f"# Massive CIDR Target List for 6-Hour Hunt\n")
            f.write(f"# Generated: 2025-06-24 09:57:49 UTC\n")
            f.write(f"# Total ranges: {len(unique_targets)}\n")
            f.write(f"# Estimated IPs: {self._estimate_ip_count(unique_targets)}\n\n")
            
            for target in unique_targets:
                f.write(f"{target}\n")
        
        print(f"✅ Generated {len(unique_targets)} target ranges")
        print(f"📊 Estimated total IPs: {self._estimate_ip_count(unique_targets):,}")
        print(f"💾 Saved to: {output_file}")
        
        return unique_targets

    def _generate_discovery_ranges(self, count=500):
        """Generate additional ranges for discovery"""
        ranges = []
        
        # Common hosting provider patterns
        hosting_patterns = [
            (1, 255, 22),    # Class A with /22
            (5, 255, 22),    # Various providers
            (23, 255, 20),   # Akamai and others
            (31, 255, 20),   # Various
            (37, 255, 20),   # RIPE region
            (46, 255, 20),   # Europe
            (62, 255, 20),   # Europe
            (77, 255, 20),   # Europe
            (78, 255, 20),   # Europe
            (80, 255, 20),   # Europe
            (81, 255, 20),   # Europe
            (82, 255, 20),   # Europe
            (83, 255, 20),   # Europe
            (84, 255, 20),   # Europe
            (85, 255, 20),   # Europe
            (86, 255, 20),   # Europe
            (87, 255, 20),   # Europe
            (88, 255, 20),   # Europe
            (89, 255, 20),   # Europe
            (90, 255, 20),   # Europe
            (91, 255, 20),   # Europe
            (92, 255, 20),   # Europe
            (93, 255, 20),   # Europe
            (94, 255, 20),   # Europe
            (95, 255, 20),   # Europe
        ]
        
        for first_octet, max_second, prefix in hosting_patterns:
            if len(ranges) >= count:
                break
                
            # Generate ranges in this block
            for _ in range(min(10, count - len(ranges))):
                second_octet = random.randint(1, max_second)
                third_octet = random.randint(0, 255)
                
                cidr = f"{first_octet}.{second_octet}.{third_octet}.0/{prefix}"
                ranges.append(cidr)
        
        return ranges

    def _estimate_ip_count(self, ranges):
        """Estimate total IP count in ranges"""
        total = 0
        for range_str in ranges:
            try:
                network = ipaddress.IPv4Network(range_str, strict=False)
                total += network.num_addresses
            except:
                total += 1  # Single IP
        return total

    def generate_kubernetes_focused_targets(self, output_file="k8s_focused_targets.txt"):
        """Generate K8s-focused target list"""
        k8s_targets = []
        
        # Known K8s service ports and patterns
        k8s_ports = [6443, 8443, 10250, 8080, 9443, 2379, 2380]
        
        # Cloud provider K8s service ranges
        k8s_cloud_ranges = [
            # EKS ranges (AWS)
            "34.192.0.0/12",  # us-east-1 EKS
            "52.0.0.0/11",    # us-east-1 EKS
            "18.208.0.0/13",  # us-east-1 EKS
            
            # GKE ranges (GCP)
            "34.64.0.0/10",   # GKE clusters
            "35.184.0.0/13",  # GKE nodes
            
            # AKS ranges (Azure)
            "20.0.0.0/8",     # AKS clusters
            "52.224.0.0/11",  # AKS nodes
        ]
        
        k8s_targets.extend(k8s_cloud_ranges)
        
        # Add common enterprise K8s ranges
        enterprise_k8s = [
            "10.0.0.0/16",    # Common K8s internal
            "10.1.0.0/16",
            "10.2.0.0/16", 
            "10.10.0.0/16",
            "10.20.0.0/16",
            "10.100.0.0/16",
            "10.200.0.0/16",
            "172.16.0.0/16",  # Docker default
            "172.17.0.0/16",
            "172.18.0.0/16",
            "172.20.0.0/16",
            "192.168.0.0/24",
            "192.168.1.0/24",
            "192.168.10.0/24",
            "192.168.100.0/24"
        ]
        
        k8s_targets.extend(enterprise_k8s)
        
        with open(output_file, 'w') as f:
            f.write("# Kubernetes-Focused Target List\n")
            f.write("# High-probability K8s ranges\n\n")
            for target in k8s_targets:
                f.write(f"{target}\n")
        
        print(f"✅ Generated {len(k8s_targets)} K8s-focused targets")
        print(f"💾 Saved to: {output_file}")
        
        return k8s_targets

if __name__ == "__main__":
    generator = MassiveCIDRGenerator()
    
    # Generate massive target list
    generator.generate_massive_targets("targets_massive_6h.txt")
    
    # Generate K8s-focused list
    generator.generate_kubernetes_focused_targets("k8s_focused_targets.txt")
    
    print("\n🚀 Target generation complete!")
    print("📁 Files created:")
    print("  - targets_massive_6h.txt (comprehensive)")
    print("  - k8s_focused_targets.txt (K8s-specific)")