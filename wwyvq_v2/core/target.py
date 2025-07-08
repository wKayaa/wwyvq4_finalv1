#!/usr/bin/env python3
"""
WWYVQ Framework v2 - Target Manager
Author: wKayaa
Date: 2025-01-15

Gestionnaire de cibles avec expansion CIDR et validation.
"""

import ipaddress
import socket
from typing import List, Set, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import json
import re


@dataclass
class Target:
    """Représentation d'une cible"""
    address: str
    port: Optional[int] = None
    protocol: str = "tcp"
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    
    def __str__(self):
        if self.port:
            return f"{self.address}:{self.port}"
        return self.address


@dataclass
class TargetGroup:
    """Groupe de cibles"""
    name: str
    targets: List[Target] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_target(self, target: Target):
        """Ajoute une cible au groupe"""
        self.targets.append(target)
    
    def get_target_count(self) -> int:
        """Retourne le nombre de cibles"""
        return len(self.targets)


class TargetManager:
    """
    Gestionnaire de cibles avec expansion CIDR
    
    Responsabilités:
    - Expansion automatique et manuelle des CIDR
    - Validation et normalisation des cibles
    - Gestion des groupes de cibles
    - Import/export de listes de cibles
    """
    
    def __init__(self, config_manager):
        """
        Initialise le gestionnaire de cibles
        
        Args:
            config_manager: Gestionnaire de configuration
        """
        self.config_manager = config_manager
        self.target_groups: Dict[str, TargetGroup] = {}
        self.excluded_ranges: Set[str] = set()
        
        # Préparation des ranges privés par défaut
        self.private_ranges = [
            ipaddress.IPv4Network('10.0.0.0/8'),
            ipaddress.IPv4Network('172.16.0.0/12'),
            ipaddress.IPv4Network('192.168.0.0/16'),
            ipaddress.IPv4Network('127.0.0.0/8'),
            ipaddress.IPv4Network('169.254.0.0/16'),
            ipaddress.IPv4Network('224.0.0.0/4'),
            ipaddress.IPv4Network('240.0.0.0/4')
        ]
    
    async def initialize(self):
        """Initialise le gestionnaire de cibles"""
        # Chargement des exclusions par défaut
        await self._load_default_exclusions()
        
        print("✅ Target Manager initialized")
    
    async def process_targets(self, targets: List[str]) -> List[Target]:
        """
        Traite une liste de cibles brutes
        
        Args:
            targets: Liste des cibles (IP, CIDR, URLs, etc.)
            
        Returns:
            List[Target]: Liste des cibles traitées
        """
        processed_targets = []
        config = self.config_manager.get_config()
        
        for target_str in targets:
            target_str = target_str.strip()
            
            # Ignorer les commentaires et lignes vides
            if not target_str or target_str.startswith('#'):
                continue
            
            # Traitement selon le type
            if self._is_cidr(target_str):
                # Expansion CIDR
                if config.targets.cidr_expansion:
                    cidr_targets = await self._expand_cidr(target_str)
                    processed_targets.extend(cidr_targets)
                else:
                    # Traiter comme une cible simple
                    processed_targets.append(Target(address=target_str))
            
            elif self._is_url(target_str):
                # Extraction d'URL
                url_targets = await self._process_url(target_str)
                processed_targets.extend(url_targets)
            
            else:
                # Cible simple (IP ou hostname)
                ip_targets = await self._process_single_target(target_str)
                processed_targets.extend(ip_targets)
        
        # Validation et déduplication
        validated_targets = await self._validate_targets(processed_targets)
        
        print(f"🎯 Processed {len(targets)} input targets → {len(validated_targets)} final targets")
        return validated_targets
    
    async def _expand_cidr(self, cidr: str) -> List[Target]:
        """
        Expanse un CIDR en cibles individuelles
        
        Args:
            cidr: Notation CIDR (ex: 192.168.1.0/24)
            
        Returns:
            List[Target]: Liste des IPs du CIDR
        """
        targets = []
        config = self.config_manager.get_config()
        
        try:
            network = ipaddress.IPv4Network(cidr, strict=False)
            
            # Limitation pour éviter l'explosion mémoire
            max_ips = config.targets.max_ips_per_cidr
            host_count = 0
            
            for ip in network.hosts():
                if host_count >= max_ips:
                    print(f"⚠️ CIDR {cidr} limited to {max_ips} IPs")
                    break
                
                # Vérifier les exclusions
                if not self._is_excluded(str(ip)):
                    targets.append(Target(
                        address=str(ip),
                        metadata={'source_cidr': cidr}
                    ))
                    host_count += 1
            
            print(f"📊 CIDR {cidr} expanded to {len(targets)} targets")
            
        except ValueError as e:
            print(f"❌ Invalid CIDR {cidr}: {e}")
        
        return targets
    
    async def _process_url(self, url: str) -> List[Target]:
        """
        Traite une URL et extrait les cibles
        
        Args:
            url: URL à traiter
            
        Returns:
            List[Target]: Cibles extraites
        """
        targets = []
        config = self.config_manager.get_config()
        
        try:
            # Extraction des composants URL
            if '://' in url:
                protocol, rest = url.split('://', 1)
                if '/' in rest:
                    host_port = rest.split('/', 1)[0]
                else:
                    host_port = rest
            else:
                protocol = 'http'
                host_port = url
            
            # Extraction host et port
            if ':' in host_port and not host_port.startswith('['):
                host, port_str = host_port.rsplit(':', 1)
                try:
                    port = int(port_str)
                except ValueError:
                    host = host_port
                    port = 80 if protocol == 'http' else 443
            else:
                host = host_port
                port = 80 if protocol == 'http' else 443
            
            # Résolution DNS si nécessaire
            if not self._is_ip_address(host):
                resolved_ips = await self._resolve_hostname(host)
                for ip in resolved_ips:
                    targets.append(Target(
                        address=ip,
                        port=port,
                        metadata={
                            'hostname': host,
                            'protocol': protocol,
                            'source_url': url
                        }
                    ))
            else:
                targets.append(Target(
                    address=host,
                    port=port,
                    metadata={
                        'protocol': protocol,
                        'source_url': url
                    }
                ))
            
        except Exception as e:
            print(f"❌ Error processing URL {url}: {e}")
        
        return targets
    
    async def _process_single_target(self, target: str) -> List[Target]:
        """
        Traite une cible simple (IP ou hostname)
        
        Args:
            target: Cible à traiter
            
        Returns:
            List[Target]: Cibles traitées
        """
        targets = []
        config = self.config_manager.get_config()
        
        # Vérifier si c'est IP:PORT
        if ':' in target and not target.startswith('['):
            try:
                host, port_str = target.rsplit(':', 1)
                port = int(port_str)
            except ValueError:
                host = target
                port = None
        else:
            host = target
            port = None
        
        # Résolution si nécessaire
        if not self._is_ip_address(host):
            resolved_ips = await self._resolve_hostname(host)
            for ip in resolved_ips:
                if port:
                    targets.append(Target(
                        address=ip,
                        port=port,
                        metadata={'hostname': host}
                    ))
                else:
                    # Ajouter les ports par défaut
                    for default_port in config.targets.default_ports:
                        targets.append(Target(
                            address=ip,
                            port=default_port,
                            metadata={'hostname': host}
                        ))
        else:
            if port:
                targets.append(Target(address=host, port=port))
            else:
                # Ajouter les ports par défaut
                for default_port in config.targets.default_ports:
                    targets.append(Target(address=host, port=default_port))
        
        return targets
    
    async def _resolve_hostname(self, hostname: str) -> List[str]:
        """
        Résout un nom d'hôte en adresses IP
        
        Args:
            hostname: Nom d'hôte à résoudre
            
        Returns:
            List[str]: Adresses IP résolues
        """
        ips = []
        
        try:
            # Résolution DNS
            addr_info = socket.getaddrinfo(hostname, None, socket.AF_INET)
            for info in addr_info:
                ip = info[4][0]
                if ip not in ips:
                    ips.append(ip)
            
            print(f"🔍 Resolved {hostname} → {len(ips)} IPs")
            
        except socket.gaierror as e:
            print(f"❌ DNS resolution failed for {hostname}: {e}")
        
        return ips
    
    async def _validate_targets(self, targets: List[Target]) -> List[Target]:
        """
        Valide et nettoie la liste des cibles
        
        Args:
            targets: Liste des cibles à valider
            
        Returns:
            List[Target]: Cibles validées
        """
        validated = []
        seen = set()
        
        for target in targets:
            # Création de clé unique
            key = f"{target.address}:{target.port}" if target.port else target.address
            
            if key in seen:
                continue  # Doublon
            
            # Vérification exclusions
            if self._is_excluded(target.address):
                continue
            
            # Validation IP
            if not self._is_valid_ip(target.address):
                continue
            
            # Validation port
            if target.port and not self._is_valid_port(target.port):
                continue
            
            validated.append(target)
            seen.add(key)
        
        return validated
    
    def _is_cidr(self, target: str) -> bool:
        """Vérifie si une chaîne est un CIDR"""
        return '/' in target and target.count('/') == 1
    
    def _is_url(self, target: str) -> bool:
        """Vérifie si une chaîne est une URL"""
        return any(target.startswith(proto) for proto in ['http://', 'https://'])
    
    def _is_ip_address(self, address: str) -> bool:
        """Vérifie si une chaîne est une adresse IP"""
        try:
            ipaddress.IPv4Address(address)
            return True
        except ValueError:
            return False
    
    def _is_valid_ip(self, address: str) -> bool:
        """Valide une adresse IP"""
        try:
            ip = ipaddress.IPv4Address(address)
            return not ip.is_reserved
        except ValueError:
            return False
    
    def _is_valid_port(self, port: int) -> bool:
        """Valide un port"""
        return 1 <= port <= 65535
    
    def _is_excluded(self, address: str) -> bool:
        """Vérifie si une adresse est exclue"""
        try:
            ip = ipaddress.IPv4Address(address)
            
            # Vérifier les exclusions personnalisées
            if address in self.excluded_ranges:
                return True
            
            # Vérifier les ranges privés si en mode sécurisé
            if self.config_manager.is_safe_mode():
                for private_range in self.private_ranges:
                    if ip in private_range:
                        return True
            
            return False
            
        except ValueError:
            return True  # Adresse invalide = exclue
    
    async def _load_default_exclusions(self):
        """Charge les exclusions par défaut"""
        # Exclusions communes
        default_exclusions = [
            '0.0.0.0',
            '255.255.255.255',
            '127.0.0.1'
        ]
        
        for exclusion in default_exclusions:
            self.excluded_ranges.add(exclusion)
    
    async def add_target_group(self, name: str, targets: List[str]) -> bool:
        """
        Ajoute un groupe de cibles
        
        Args:
            name: Nom du groupe
            targets: Liste des cibles
            
        Returns:
            bool: True si ajouté avec succès
        """
        if name in self.target_groups:
            print(f"❌ Target group '{name}' already exists")
            return False
        
        processed_targets = await self.process_targets(targets)
        
        group = TargetGroup(name=name)
        for target in processed_targets:
            group.add_target(target)
        
        self.target_groups[name] = group
        print(f"✅ Target group '{name}' added with {len(processed_targets)} targets")
        return True
    
    async def get_target_group(self, name: str) -> Optional[TargetGroup]:
        """
        Récupère un groupe de cibles
        
        Args:
            name: Nom du groupe
            
        Returns:
            TargetGroup ou None si non trouvé
        """
        return self.target_groups.get(name)
    
    async def import_targets_from_file(self, file_path: str) -> List[Target]:
        """
        Importe des cibles depuis un fichier
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            List[Target]: Cibles importées
        """
        targets = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Traitement ligne par ligne
            raw_targets = [line.strip() for line in lines if line.strip()]
            targets = await self.process_targets(raw_targets)
            
            print(f"📁 Imported {len(targets)} targets from {file_path}")
            
        except Exception as e:
            print(f"❌ Failed to import targets from {file_path}: {e}")
        
        return targets
    
    async def export_targets_to_file(self, targets: List[Target], file_path: str):
        """
        Exporte des cibles vers un fichier
        
        Args:
            targets: Liste des cibles
            file_path: Chemin du fichier de sortie
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for target in targets:
                    f.write(f"{target}\n")
            
            print(f"📁 Exported {len(targets)} targets to {file_path}")
            
        except Exception as e:
            print(f"❌ Failed to export targets to {file_path}: {e}")
    
    def get_target_statistics(self) -> Dict[str, Any]:
        """
        Récupère les statistiques des cibles
        
        Returns:
            Dict des statistiques
        """
        total_targets = sum(group.get_target_count() for group in self.target_groups.values())
        
        return {
            'total_groups': len(self.target_groups),
            'total_targets': total_targets,
            'excluded_ranges': len(self.excluded_ranges),
            'groups': {
                name: group.get_target_count() 
                for name, group in self.target_groups.items()
            }
        }
    
    async def add_exclusion(self, exclusion: str):
        """
        Ajoute une exclusion
        
        Args:
            exclusion: IP ou CIDR à exclure
        """
        self.excluded_ranges.add(exclusion)
        print(f"🚫 Added exclusion: {exclusion}")
    
    async def remove_exclusion(self, exclusion: str):
        """
        Supprime une exclusion
        
        Args:
            exclusion: IP ou CIDR à ne plus exclure
        """
        self.excluded_ranges.discard(exclusion)
        print(f"✅ Removed exclusion: {exclusion}")
    
    def get_exclusions(self) -> List[str]:
        """
        Récupère la liste des exclusions
        
        Returns:
            List des exclusions
        """
        return list(self.excluded_ranges)