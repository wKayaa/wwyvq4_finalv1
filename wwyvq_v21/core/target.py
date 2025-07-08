#!/usr/bin/env python3
"""
🎯 WWYVQ Framework v2.1 - Target Manager
Ultra-Organized Architecture - Advanced Target Management

Features:
- CIDR expansion and IP generation
- Target validation and categorization
- DNS resolution with caching
- Port scanning and service detection
- Target deduplication
- Automatic target classification
"""

import asyncio
import socket
import ipaddress
import random
import re
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse
import aiohttp
import aiodns


class TargetType(Enum):
    """Target types"""
    IP = "ip"
    DOMAIN = "domain"
    URL = "url"
    CIDR = "cidr"
    KUBERNETES = "kubernetes"
    UNKNOWN = "unknown"


class TargetStatus(Enum):
    """Target status"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Target:
    """Target information"""
    target: str
    target_type: TargetType
    status: TargetStatus = TargetStatus.PENDING
    ports: List[int] = None
    resolved_ips: List[str] = None
    services: Dict[int, str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.ports is None:
            self.ports = []
        if self.resolved_ips is None:
            self.resolved_ips = []
        if self.services is None:
            self.services = {}
        if self.metadata is None:
            self.metadata = {}


class TargetManager:
    """
    Advanced target management for WWYVQ v2.1
    
    Features:
    - CIDR expansion and IP generation
    - Target validation and categorization
    - DNS resolution with caching
    - Port scanning and service detection
    - Target deduplication
    - Automatic target classification
    """
    
    def __init__(self, config_manager):
        """
        Initialize target manager
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.config = config_manager.get_config().targets
        
        # Target storage
        self.targets: Dict[str, Target] = {}
        self.target_queue: asyncio.Queue = asyncio.Queue()
        
        # DNS resolver
        self.dns_resolver = None
        self.dns_cache: Dict[str, List[str]] = {}
        
        # Port scanning
        self.port_scanner_semaphore = asyncio.Semaphore(100)
        
        # Statistics
        self.stats = {
            'total_targets': 0,
            'resolved_targets': 0,
            'failed_targets': 0,
            'cidr_expanded': 0,
            'k8s_detected': 0,
            'services_detected': 0
        }
        
        print("✅ Target Manager v2.1 initialized")
    
    async def initialize(self):
        """Initialize target manager"""
        # Initialize DNS resolver
        self.dns_resolver = aiodns.DNSResolver()
        
        print("✅ Target Manager initialized")
    
    def _detect_target_type(self, target: str) -> TargetType:
        """Detect target type"""
        target = target.strip()
        
        # Check for CIDR notation
        if '/' in target:
            try:
                ipaddress.ip_network(target, strict=False)
                return TargetType.CIDR
            except:
                pass
        
        # Check for URL
        if target.startswith(('http://', 'https://')):
            return TargetType.URL
        
        # Check for IP address
        try:
            ipaddress.ip_address(target)
            return TargetType.IP
        except:
            pass
        
        # Check for Kubernetes patterns
        k8s_patterns = [
            r'.*:6443$',  # Kubernetes API server
            r'.*:10250$',  # Kubelet
            r'.*:2379$',   # etcd
            r'.*:2380$',   # etcd peer
            r'.*\.k8s\..*',
            r'.*\.kubernetes\..*',
            r'.*-k8s-.*',
            r'.*cluster.*'
        ]
        
        for pattern in k8s_patterns:
            if re.match(pattern, target, re.IGNORECASE):
                return TargetType.KUBERNETES
        
        # Check for domain
        if re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', target):
            return TargetType.DOMAIN
        
        return TargetType.UNKNOWN
    
    async def add_target(self, target: str, ports: Optional[List[int]] = None) -> bool:
        """Add a single target"""
        try:
            target = target.strip()
            if not target:
                return False
            
            # Detect target type
            target_type = self._detect_target_type(target)
            
            # Handle CIDR expansion
            if target_type == TargetType.CIDR:
                expanded_targets = await self._expand_cidr(target)
                for ip in expanded_targets:
                    await self.add_target(ip, ports)
                return True
            
            # Skip if already exists
            if target in self.targets:
                return False
            
            # Create target object
            target_obj = Target(
                target=target,
                target_type=target_type,
                ports=ports or self.config.default_ports.copy()
            )
            
            # Store target
            self.targets[target] = target_obj
            await self.target_queue.put(target)
            
            self.stats['total_targets'] += 1
            
            # Special handling for Kubernetes
            if target_type == TargetType.KUBERNETES:
                self.stats['k8s_detected'] += 1
                target_obj.metadata['kubernetes'] = True
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to add target {target}: {e}")
            return False
    
    async def add_targets(self, targets: List[str]) -> int:
        """Add multiple targets"""
        added_count = 0
        
        for target in targets:
            if await self.add_target(target):
                added_count += 1
        
        return added_count
    
    async def add_targets_from_file(self, file_path: str) -> int:
        """Add targets from file"""
        try:
            with open(file_path, 'r') as f:
                targets = [line.strip() for line in f if line.strip()]
            
            return await self.add_targets(targets)
            
        except Exception as e:
            print(f"❌ Failed to load targets from {file_path}: {e}")
            return 0
    
    async def _expand_cidr(self, cidr: str) -> List[str]:
        """Expand CIDR notation to IP addresses"""
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            
            # Limit expansion to prevent memory issues
            max_ips = min(self.config.max_targets, 10000)
            
            if network.num_addresses > max_ips:
                print(f"⚠️ CIDR {cidr} has {network.num_addresses} IPs, limiting to {max_ips}")
                # Sample random IPs
                all_ips = list(network.hosts())
                if len(all_ips) > max_ips:
                    all_ips = random.sample(all_ips, max_ips)
                ips = [str(ip) for ip in all_ips]
            else:
                ips = [str(ip) for ip in network.hosts()]
            
            # Randomize order if configured
            if self.config.ip_randomization:
                random.shuffle(ips)
            
            self.stats['cidr_expanded'] += len(ips)
            return ips
            
        except Exception as e:
            print(f"❌ Failed to expand CIDR {cidr}: {e}")
            return []
    
    async def resolve_target(self, target: str) -> List[str]:
        """Resolve target to IP addresses"""
        try:
            target_obj = self.targets.get(target)
            if not target_obj:
                return []
            
            # Skip if already resolved
            if target_obj.resolved_ips:
                return target_obj.resolved_ips
            
            # Handle different target types
            if target_obj.target_type == TargetType.IP:
                target_obj.resolved_ips = [target]
            
            elif target_obj.target_type == TargetType.URL:
                parsed = urlparse(target)
                hostname = parsed.hostname
                if hostname:
                    ips = await self._resolve_hostname(hostname)
                    target_obj.resolved_ips = ips
            
            elif target_obj.target_type in [TargetType.DOMAIN, TargetType.KUBERNETES]:
                # Extract hostname from target
                hostname = target.split(':')[0]  # Remove port if present
                ips = await self._resolve_hostname(hostname)
                target_obj.resolved_ips = ips
            
            if target_obj.resolved_ips:
                self.stats['resolved_targets'] += 1
            else:
                self.stats['failed_targets'] += 1
                target_obj.status = TargetStatus.FAILED
            
            return target_obj.resolved_ips
            
        except Exception as e:
            print(f"❌ Failed to resolve target {target}: {e}")
            return []
    
    async def _resolve_hostname(self, hostname: str) -> List[str]:
        """Resolve hostname to IP addresses"""
        # Check cache first
        if hostname in self.dns_cache:
            return self.dns_cache[hostname]
        
        try:
            # Resolve A records
            result = await self.dns_resolver.gethostbyname(hostname, socket.AF_INET)
            ips = [result]
            
            # Cache result
            self.dns_cache[hostname] = ips
            
            return ips
            
        except Exception as e:
            print(f"❌ Failed to resolve hostname {hostname}: {e}")
            return []
    
    async def scan_target_ports(self, target: str) -> Dict[int, str]:
        """Scan target ports"""
        target_obj = self.targets.get(target)
        if not target_obj:
            return {}
        
        # Skip if already scanned
        if target_obj.services:
            return target_obj.services
        
        # Resolve target first
        ips = await self.resolve_target(target)
        if not ips:
            return {}
        
        # Scan ports on first IP
        ip = ips[0]
        services = {}
        
        # Scan each port
        for port in target_obj.ports:
            async with self.port_scanner_semaphore:
                service = await self._scan_port(ip, port)
                if service:
                    services[port] = service
        
        target_obj.services = services
        if services:
            self.stats['services_detected'] += len(services)
        
        return services
    
    async def _scan_port(self, ip: str, port: int) -> Optional[str]:
        """Scan a single port"""
        try:
            # Connect with timeout
            future = asyncio.open_connection(ip, port)
            reader, writer = await asyncio.wait_for(future, timeout=3)
            
            # Close connection
            writer.close()
            await writer.wait_closed()
            
            # Detect service
            service = self._detect_service(port)
            return service
            
        except asyncio.TimeoutError:
            return None
        except Exception:
            return None
    
    def _detect_service(self, port: int) -> str:
        """Detect service by port"""
        common_services = {
            21: 'ftp',
            22: 'ssh',
            23: 'telnet',
            25: 'smtp',
            53: 'dns',
            80: 'http',
            110: 'pop3',
            143: 'imap',
            443: 'https',
            993: 'imaps',
            995: 'pop3s',
            2379: 'etcd',
            2380: 'etcd-peer',
            6443: 'kubernetes-api',
            8080: 'http-alt',
            8443: 'https-alt',
            10250: 'kubelet'
        }
        
        return common_services.get(port, f'port-{port}')
    
    async def get_targets(self, target_type: Optional[TargetType] = None,
                         status: Optional[TargetStatus] = None) -> List[Target]:
        """Get targets with optional filtering"""
        targets = list(self.targets.values())
        
        if target_type:
            targets = [t for t in targets if t.target_type == target_type]
        
        if status:
            targets = [t for t in targets if t.status == status]
        
        return targets
    
    async def get_kubernetes_targets(self) -> List[Target]:
        """Get Kubernetes-specific targets"""
        k8s_targets = []
        
        for target in self.targets.values():
            if (target.target_type == TargetType.KUBERNETES or
                target.metadata.get('kubernetes', False)):
                k8s_targets.append(target)
        
        return k8s_targets
    
    async def prioritize_targets(self) -> List[Target]:
        """Prioritize targets based on type and services"""
        targets = list(self.targets.values())
        
        # Prioritization weights
        priority_weights = {
            TargetType.KUBERNETES: 10,
            TargetType.URL: 8,
            TargetType.DOMAIN: 6,
            TargetType.IP: 4,
            TargetType.CIDR: 2,
            TargetType.UNKNOWN: 1
        }
        
        # Sort by priority
        def get_priority(target):
            base_priority = priority_weights.get(target.target_type, 0)
            
            # Bonus for Kubernetes services
            if target.metadata.get('kubernetes', False):
                base_priority += 5
            
            # Bonus for having services
            if target.services:
                base_priority += len(target.services)
            
            return base_priority
        
        targets.sort(key=get_priority, reverse=True)
        return targets
    
    async def update_target_status(self, target: str, status: TargetStatus):
        """Update target status"""
        if target in self.targets:
            self.targets[target].status = status
    
    async def get_target_statistics(self) -> Dict[str, Any]:
        """Get target statistics"""
        stats = self.stats.copy()
        
        # Add type breakdown
        stats['by_type'] = {}
        stats['by_status'] = {}
        
        for target in self.targets.values():
            # By type
            type_name = target.target_type.value
            stats['by_type'][type_name] = stats['by_type'].get(type_name, 0) + 1
            
            # By status
            status_name = target.status.value
            stats['by_status'][status_name] = stats['by_status'].get(status_name, 0) + 1
        
        return stats
    
    async def export_targets(self, format: str = 'json') -> str:
        """Export targets to file"""
        try:
            from datetime import datetime
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"targets_export_{timestamp}.{format}"
            
            if format.lower() == 'json':
                import json
                
                targets_data = []
                for target in self.targets.values():
                    targets_data.append({
                        'target': target.target,
                        'type': target.target_type.value,
                        'status': target.status.value,
                        'ports': target.ports,
                        'resolved_ips': target.resolved_ips,
                        'services': target.services,
                        'metadata': target.metadata
                    })
                
                with open(filename, 'w') as f:
                    json.dump(targets_data, f, indent=2)
            
            elif format.lower() == 'csv':
                import csv
                
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['target', 'type', 'status', 'ports', 'resolved_ips', 'services'])
                    
                    for target in self.targets.values():
                        writer.writerow([
                            target.target,
                            target.target_type.value,
                            target.status.value,
                            ','.join(map(str, target.ports)),
                            ','.join(target.resolved_ips),
                            ','.join(f"{p}:{s}" for p, s in target.services.items())
                        ])
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            return filename
            
        except Exception as e:
            print(f"❌ Failed to export targets: {e}")
            raise
    
    async def clear_targets(self):
        """Clear all targets"""
        self.targets.clear()
        
        # Clear queue
        while not self.target_queue.empty():
            try:
                self.target_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        # Reset statistics
        self.stats = {
            'total_targets': 0,
            'resolved_targets': 0,
            'failed_targets': 0,
            'cidr_expanded': 0,
            'k8s_detected': 0,
            'services_detected': 0
        }
        
        print("✅ All targets cleared")
    
    async def get_next_target(self) -> Optional[str]:
        """Get next target from queue"""
        try:
            return await asyncio.wait_for(self.target_queue.get(), timeout=1)
        except asyncio.TimeoutError:
            return None
    
    async def shutdown(self):
        """Shutdown target manager"""
        print("🛑 Shutting down target manager...")
        
        # Clear targets
        await self.clear_targets()
        
        print("✅ Target manager shutdown completed")