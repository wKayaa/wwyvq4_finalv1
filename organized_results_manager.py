#!/usr/bin/env python3
"""
📁 Organized Results Manager
Manages structured credential storage in service-specific files
Author: wKayaa | 2025
"""

import os
import json
import csv
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class OrganizedResultsManager:
    """Manages organized credential storage and results"""
    
    def __init__(self, base_results_dir: str = "results"):
        self.base_results_dir = Path(base_results_dir)
        self.session_id = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        self.session_dir = self.base_results_dir / f"session_{self.session_id}"
        
        # Service-specific file mapping
        self.service_files = {
            'AWS': 'aws.txt',
            'SendGrid': 'sendgrid.txt',
            'Mailgun': 'mailgun.txt',
            'Mailjet': 'mailjet.txt',
            'Postmark': 'postmark.txt',
            'Mandrill': 'mandrill.txt',
            'Brevo': 'brevo.txt',
            'SparkPost': 'sparkpost.txt',
            'JWT': 'jwt_tokens.txt',
            'Generic': 'generic_apis.txt',
            'Unknown': 'unknown_credentials.txt'
        }
        
        # Initialize results structure
        self._setup_results_structure()
        
        # Statistics tracking
        self.stats = {
            'total_credentials': 0,
            'valid_credentials': 0,
            'invalid_credentials': 0,
            'services_found': {},
            'session_start': datetime.utcnow(),
            'last_update': datetime.utcnow()
        }
    
    def _setup_results_structure(self):
        """Setup the organized results directory structure"""
        try:
            # Create base results directory
            self.base_results_dir.mkdir(exist_ok=True)
            
            # Create session directory
            self.session_dir.mkdir(exist_ok=True)
            
            # Create service subdirectories
            for service in self.service_files.keys():
                service_dir = self.session_dir / service.lower()
                service_dir.mkdir(exist_ok=True)
            
            # Create additional directories
            additional_dirs = ['json_exports', 'csv_exports', 'raw_dumps', 'validated_only']
            for dir_name in additional_dirs:
                (self.session_dir / dir_name).mkdir(exist_ok=True)
            
            logger.info(f"✅ Results structure created: {self.session_dir}")
            
        except Exception as e:
            logger.error(f"❌ Error setting up results structure: {e}")
            raise
    
    def save_credential(self, validation_result, raw_credential: Optional[Dict] = None):
        """Save a credential to the appropriate service file"""
        try:
            service = validation_result.service
            
            # Update statistics
            self.stats['total_credentials'] += 1
            if validation_result.is_valid:
                self.stats['valid_credentials'] += 1
            else:
                self.stats['invalid_credentials'] += 1
            
            # Update service count
            if service not in self.stats['services_found']:
                self.stats['services_found'][service] = 0
            self.stats['services_found'][service] += 1
            
            # Save to service-specific file
            service_file = self.service_files.get(service, 'unknown_credentials.txt')
            service_path = self.session_dir / service_file
            
            # Create formatted entry
            entry = self._format_credential_entry(validation_result, raw_credential)
            
            # Append to service file
            with open(service_path, 'a', encoding='utf-8') as f:
                f.write(entry + '\n')
            
            # Save to JSON format
            self._save_to_json(validation_result, raw_credential)
            
            # Save to CSV format
            self._save_to_csv(validation_result, raw_credential)
            
            # Save validated credentials separately
            if validation_result.is_valid:
                self._save_validated_credential(validation_result, raw_credential)
            
            # Update host.txt with source information
            self._update_host_file(validation_result, raw_credential)
            
            logger.info(f"💾 Credential saved: {service} -> {service_file}")
            
        except Exception as e:
            logger.error(f"❌ Error saving credential: {e}")
    
    def _format_credential_entry(self, validation_result, raw_credential: Optional[Dict] = None) -> str:
        """Format credential entry for text file"""
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        entry = f"""
{'='*80}
🚨 CREDENTIAL ENTRY #{self.stats['total_credentials']}
{'='*80}
📅 TIMESTAMP: {timestamp}
🔑 SERVICE: {validation_result.service}
📋 TYPE: {validation_result.credential_type}
✅ VALID: {validation_result.is_valid}
📊 CONFIDENCE: {validation_result.confidence_score:.1f}%
🔍 METHOD: {validation_result.validation_method}

🔐 CREDENTIAL DETAILS:
├── Value: {validation_result.value}
├── Permissions: {', '.join(validation_result.permissions) if validation_result.permissions else 'None'}
└── Quota Info: {json.dumps(validation_result.quota_info) if validation_result.quota_info else 'N/A'}

📍 SOURCE INFORMATION:
"""
        
        if raw_credential:
            entry += f"├── URL: {raw_credential.get('source_url', 'Unknown')}\n"
            entry += f"├── Extracted: {raw_credential.get('extracted_at', 'Unknown')}\n"
            entry += f"└── Original Confidence: {raw_credential.get('confidence', 0):.1f}%\n"
        else:
            entry += "└── Source information not available\n"
        
        if validation_result.error_message:
            entry += f"\n⚠️ ERROR: {validation_result.error_message}\n"
        
        entry += f"{'='*80}\n"
        
        return entry
    
    def _save_to_json(self, validation_result, raw_credential: Optional[Dict] = None):
        """Save credential to JSON format"""
        try:
            json_file = self.session_dir / 'json_exports' / f"{validation_result.service.lower()}_credentials.json"
            
            # Create credential object
            credential_obj = {
                'entry_id': self.stats['total_credentials'],
                'timestamp': datetime.utcnow().isoformat(),
                'service': validation_result.service,
                'credential_type': validation_result.credential_type,
                'value': validation_result.value,
                'is_valid': validation_result.is_valid,
                'confidence_score': validation_result.confidence_score,
                'validation_method': validation_result.validation_method,
                'permissions': validation_result.permissions,
                'quota_info': validation_result.quota_info,
                'validated_at': validation_result.validated_at,
                'error_message': validation_result.error_message
            }
            
            if raw_credential:
                credential_obj['source_info'] = raw_credential
            
            # Load existing data or create new
            if json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = []
            
            data.append(credential_obj)
            
            # Save updated data
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"❌ Error saving JSON: {e}")
    
    def _save_to_csv(self, validation_result, raw_credential: Optional[Dict] = None):
        """Save credential to CSV format"""
        try:
            csv_file = self.session_dir / 'csv_exports' / f"{validation_result.service.lower()}_credentials.csv"
            
            # Define CSV headers
            headers = [
                'entry_id', 'timestamp', 'service', 'credential_type', 'value', 
                'is_valid', 'confidence_score', 'validation_method', 'permissions',
                'quota_info', 'validated_at', 'error_message', 'source_url'
            ]
            
            # Check if file exists to write headers
            write_headers = not csv_file.exists()
            
            with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                
                if write_headers:
                    writer.writeheader()
                
                row = {
                    'entry_id': self.stats['total_credentials'],
                    'timestamp': datetime.utcnow().isoformat(),
                    'service': validation_result.service,
                    'credential_type': validation_result.credential_type,
                    'value': validation_result.value,
                    'is_valid': validation_result.is_valid,
                    'confidence_score': validation_result.confidence_score,
                    'validation_method': validation_result.validation_method,
                    'permissions': ', '.join(validation_result.permissions) if validation_result.permissions else '',
                    'quota_info': json.dumps(validation_result.quota_info) if validation_result.quota_info else '',
                    'validated_at': validation_result.validated_at,
                    'error_message': validation_result.error_message or '',
                    'source_url': raw_credential.get('source_url', '') if raw_credential else ''
                }
                
                writer.writerow(row)
            
        except Exception as e:
            logger.error(f"❌ Error saving CSV: {e}")
    
    def _save_validated_credential(self, validation_result, raw_credential: Optional[Dict] = None):
        """Save only validated credentials to separate file"""
        try:
            validated_file = self.session_dir / 'validated_only' / f"{validation_result.service.lower()}_validated.txt"
            
            entry = f"""
🔥 VALIDATED CREDENTIAL #{self.stats['valid_credentials']}
📅 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
🔑 {validation_result.service} | {validation_result.credential_type}
📊 Confidence: {validation_result.confidence_score:.1f}%
🔐 Value: {validation_result.value}
🎯 Permissions: {', '.join(validation_result.permissions) if validation_result.permissions else 'None detected'}
💰 Exploitation Ready: YES
{'='*60}
"""
            
            with open(validated_file, 'a', encoding='utf-8') as f:
                f.write(entry + '\n')
            
        except Exception as e:
            logger.error(f"❌ Error saving validated credential: {e}")
    
    def _update_host_file(self, validation_result, raw_credential: Optional[Dict] = None):
        """Update host.txt with source information"""
        try:
            host_file = self.session_dir / 'host.txt'
            
            if raw_credential and raw_credential.get('source_url'):
                source_url = raw_credential['source_url']
                # Extract host from URL
                if '://' in source_url:
                    host = source_url.split('://')[1].split('/')[0]
                else:
                    host = source_url.split('/')[0]
                
                # Read existing hosts
                existing_hosts = set()
                if host_file.exists():
                    with open(host_file, 'r', encoding='utf-8') as f:
                        existing_hosts = set(line.strip() for line in f if line.strip())
                
                # Add new host if not exists
                if host not in existing_hosts:
                    with open(host_file, 'a', encoding='utf-8') as f:
                        f.write(f"{host}\n")
            
        except Exception as e:
            logger.error(f"❌ Error updating host file: {e}")
    
    def generate_session_summary(self) -> Dict[str, Any]:
        """Generate session summary with statistics"""
        duration = datetime.utcnow() - self.stats['session_start']
        
        summary = {
            'session_id': self.session_id,
            'session_start': self.stats['session_start'].isoformat(),
            'session_duration': str(duration),
            'total_credentials': self.stats['total_credentials'],
            'valid_credentials': self.stats['valid_credentials'],
            'invalid_credentials': self.stats['invalid_credentials'],
            'success_rate': (self.stats['valid_credentials'] / self.stats['total_credentials'] * 100) if self.stats['total_credentials'] > 0 else 0,
            'services_found': self.stats['services_found'],
            'results_directory': str(self.session_dir),
            'generated_at': datetime.utcnow().isoformat()
        }
        
        # Save summary to file
        summary_file = self.session_dir / 'session_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Create human-readable summary
        self._create_readable_summary(summary)
        
        return summary
    
    def _create_readable_summary(self, summary: Dict[str, Any]):
        """Create human-readable summary file"""
        try:
            readable_file = self.session_dir / 'SUMMARY.txt'
            
            content = f"""
🏁 WWYVQ CREDENTIAL HUNTING SESSION COMPLETE
{'='*80}

📊 SESSION STATISTICS:
├── Session ID: {summary['session_id']}
├── Duration: {summary['session_duration']}
├── Total Credentials: {summary['total_credentials']}
├── Valid Credentials: {summary['valid_credentials']}
├── Invalid Credentials: {summary['invalid_credentials']}
└── Success Rate: {summary['success_rate']:.1f}%

🎯 SERVICES DISCOVERED:
"""
            
            for service, count in summary['services_found'].items():
                content += f"├── {service}: {count} credentials\n"
            
            content += f"""
📁 RESULTS ORGANIZATION:
├── Session Directory: {summary['results_directory']}
├── Service Files: {len(self.service_files)} categories
├── JSON Exports: Available in json_exports/
├── CSV Exports: Available in csv_exports/
├── Validated Only: Available in validated_only/
└── Host Information: host.txt

📋 FILE STRUCTURE:
"""
            
            for service, filename in self.service_files.items():
                service_file = self.session_dir / filename
                if service_file.exists():
                    size = service_file.stat().st_size
                    content += f"├── {filename}: {size} bytes\n"
            
            content += f"""
🚀 EXPLOITATION READY:
├── Validated Credentials: {summary['valid_credentials']}
├── Immediate Use: YES
├── Monetization Potential: ${summary['valid_credentials'] * 50} - ${summary['valid_credentials'] * 200}
└── Risk Level: {'HIGH' if summary['valid_credentials'] > 5 else 'MEDIUM' if summary['valid_credentials'] > 0 else 'LOW'}

👨‍💻 OPERATOR: wKayaa
🚀 FRAMEWORK: WWYVQ v5.0
📅 COMPLETED: {summary['generated_at']}

#WWYVQ #CredentialHunting #OrganizedResults #wKayaa
{'='*80}
"""
            
            with open(readable_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
        except Exception as e:
            logger.error(f"❌ Error creating readable summary: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        self.stats['last_update'] = datetime.utcnow()
        return self.stats.copy()
    
    def cleanup_old_sessions(self, days_to_keep: int = 7):
        """Clean up old session directories"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            for session_dir in self.base_results_dir.iterdir():
                if session_dir.is_dir() and session_dir.name.startswith('session_'):
                    try:
                        # Extract date from session name
                        date_part = session_dir.name.split('_')[1]
                        session_date = datetime.strptime(date_part, '%Y%m%d')
                        
                        if session_date < cutoff_date:
                            shutil.rmtree(session_dir)
                            logger.info(f"🧹 Cleaned up old session: {session_dir.name}")
                    except (ValueError, IndexError):
                        # Skip directories that don't match expected format
                        continue
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up old sessions: {e}")