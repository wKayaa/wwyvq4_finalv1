#!/usr/bin/env python3
"""
WWYVQ v2.1 JSON Exporter Module
Export data in JSON format with structured organization

Author: wKayaa
Date: 2025-01-07
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from .base_exporter import BaseExporterModule, ExportResult


class JsonExporterModule(BaseExporterModule):
    """
    JSON export module with structured data organization
    Creates professional JSON reports with metadata
    """
    
    def __init__(self):
        super().__init__(
            name="JsonExporter",
            description="Export data in JSON format with structured organization",
            file_extension=".json"
        )
        
        # JSON formatting options
        self.pretty_print = True
        self.indent_size = 2
        self.sort_keys = True
        self.ensure_ascii = False
    
    async def execute_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute JSON export asynchronously"""
        try:
            exports_created = 0
            export_results = []
            
            # Create comprehensive export data structure
            export_data = self._build_export_data(context)
            
            # Create metadata
            metadata = self.create_metadata(context)
            
            # Export main results file
            main_result = await self.export_data(export_data, metadata=metadata)
            if main_result.success:
                exports_created += 1
                export_results.append(main_result)
            
            # Export credentials separately if any
            if 'credentials' in export_data and export_data['credentials']:
                creds_metadata = metadata.copy()
                creds_metadata['export_type'] = 'credentials_only'
                
                credentials_result = await self.export_data(
                    {'credentials': export_data['credentials'], 'metadata': metadata},
                    filename=self._generate_filename(creds_metadata).replace('.json', '_credentials.json'),
                    metadata=creds_metadata
                )
                if credentials_result.success:
                    exports_created += 1
                    export_results.append(credentials_result)
            
            # Export valid credentials only
            valid_credentials = [
                cred for cred in export_data.get('credentials', [])
                if cred.get('validation_status') == 'valid'
            ]
            
            if valid_credentials:
                valid_metadata = metadata.copy()
                valid_metadata['export_type'] = 'valid_credentials_only'
                
                valid_result = await self.export_data(
                    {'valid_credentials': valid_credentials, 'metadata': metadata},
                    filename=self._generate_filename(valid_metadata).replace('.json', '_valid_credentials.json'),
                    metadata=valid_metadata
                )
                if valid_result.success:
                    exports_created += 1
                    export_results.append(valid_result)
            
            # Create host file if targets exist
            if 'targets' in export_data and export_data['targets']:
                host_result = await self.create_host_file(export_data['targets'], metadata)
                if host_result.success:
                    exports_created += 1
                    export_results.append(host_result)
            
            return {
                'exports_created': exports_created,
                'export_results': [
                    {
                        'file_path': result.file_path,
                        'export_type': result.export_type,
                        'records_exported': result.records_exported,
                        'file_size_bytes': result.file_size_bytes
                    }
                    for result in export_results if result.success
                ],
                'json_exporter_stats': self.get_stats()
            }
            
        except Exception as e:
            self.logger.error(f"❌ JSON export execution failed: {e}")
            return {'error': str(e)}
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute JSON export synchronously"""
        return asyncio.run(self.execute_async(context))
    
    async def _export_data_impl(self, data: Any, output_path: Path, 
                               metadata: Dict[str, Any]) -> ExportResult:
        """Implementation of JSON data export"""
        try:
            # Prepare data for JSON serialization
            json_data = self._prepare_json_data(data, metadata)
            
            # Write JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                if self.pretty_print:
                    json.dump(
                        json_data, 
                        f, 
                        indent=self.indent_size,
                        sort_keys=self.sort_keys,
                        ensure_ascii=self.ensure_ascii,
                        default=self._json_serializer
                    )
                else:
                    json.dump(
                        json_data, 
                        f, 
                        ensure_ascii=self.ensure_ascii,
                        default=self._json_serializer
                    )
            
            # Get file information
            file_size = self._get_file_size(output_path)
            records_count = self._count_records(data)
            
            self.logger.info(f"📄 JSON export created: {output_path} ({records_count} records, {file_size} bytes)")
            
            return ExportResult(
                success=True,
                file_path=str(output_path),
                export_type="json",
                records_exported=records_count,
                file_size_bytes=file_size,
                metadata={'format': 'json', 'pretty_print': self.pretty_print}
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error exporting JSON data to {output_path}: {e}")
            return ExportResult(
                success=False,
                export_type="json",
                error_message=str(e)
            )
    
    def _build_export_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive export data structure"""
        export_data = {
            'wwyvq_version': '2.1',
            'export_timestamp': datetime.utcnow().isoformat(),
            'job_info': {},
            'execution_summary': {},
            'targets': [],
            'credentials': [],
            'vulnerabilities': [],
            'clusters': [],
            'statistics': {}
        }
        
        # Job information
        if 'job_id' in context:
            export_data['job_info']['job_id'] = context['job_id']
        
        if 'config' in context:
            config = context['config']
            export_data['job_info'].update({
                'job_name': getattr(config, 'name', 'unknown'),
                'execution_mode': str(getattr(config, 'mode', 'unknown')),
                'max_concurrent': getattr(config, 'max_concurrent', 0),
                'timeout': getattr(config, 'timeout', 0),
                'kubernetes_focus': getattr(config, 'kubernetes_focus', False),
                'validation_enabled': getattr(config, 'validation_enabled', False),
                'notifications_enabled': getattr(config, 'notifications_enabled', False)
            })
            
            # Store targets
            export_data['targets'] = getattr(config, 'targets', [])
        
        # Execution timing
        if 'start_time' in context:
            start_time = context['start_time']
            export_data['job_info']['start_time'] = start_time.isoformat() if hasattr(start_time, 'isoformat') else str(start_time)
            
            duration = datetime.utcnow() - start_time
            export_data['job_info']['duration_seconds'] = duration.total_seconds()
            export_data['job_info']['duration_formatted'] = self._format_duration(duration.total_seconds())
        
        # Results from different phases
        if 'results' in context:
            results = context['results']
            
            # Exploitation results
            if 'exploitation' in results:
                exploitation = results['exploitation']
                export_data['execution_summary']['exploitation'] = exploitation
                
                # Extract credentials
                if 'credentials' in exploitation:
                    export_data['credentials'].extend(exploitation['credentials'])
                
                # Extract vulnerabilities
                if 'vulnerabilities' in exploitation:
                    export_data['vulnerabilities'].extend(exploitation['vulnerabilities'])
                
                # Extract cluster information
                if 'clusters' in exploitation:
                    export_data['clusters'].extend(exploitation['clusters'])
            
            # Validation results
            if 'validation' in results:
                validation = results['validation']
                export_data['execution_summary']['validation'] = validation
                
                # Merge validation results with credentials
                valid_credentials = validation.get('valid_credentials', [])
                invalid_credentials = validation.get('invalid_credentials', [])
                
                # Update credential validation status
                for cred in export_data['credentials']:
                    cred['validation_status'] = 'unknown'
                    
                    # Check if it's in valid credentials
                    for valid_cred in valid_credentials:
                        if (cred.get('value') == valid_cred.get('value') and 
                            cred.get('type') == valid_cred.get('type')):
                            cred['validation_status'] = 'valid'
                            cred['validation_details'] = valid_cred.get('details', {})
                            cred['service_info'] = valid_cred.get('service_info', {})
                            break
                    
                    # Check if it's in invalid credentials
                    for invalid_cred in invalid_credentials:
                        if (cred.get('value') == invalid_cred.get('value') and 
                            cred.get('type') == invalid_cred.get('type')):
                            cred['validation_status'] = 'invalid'
                            cred['validation_error'] = invalid_cred.get('error', '')
                            break
            
            # Notification results
            if 'notifications' in results:
                export_data['execution_summary']['notifications'] = results['notifications']
            
            # Export results
            if 'exports' in results:
                export_data['execution_summary']['exports'] = results['exports']
        
        # Calculate statistics
        export_data['statistics'] = self._calculate_statistics(export_data)
        
        return export_data
    
    def _calculate_statistics(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistics from export data"""
        stats = {
            'targets_total': len(export_data.get('targets', [])),
            'credentials_total': len(export_data.get('credentials', [])),
            'credentials_valid': 0,
            'credentials_invalid': 0,
            'credentials_unknown': 0,
            'vulnerabilities_total': len(export_data.get('vulnerabilities', [])),
            'clusters_total': len(export_data.get('clusters', [])),
            'credentials_by_type': {},
            'credentials_by_service': {}
        }
        
        # Count credentials by validation status
        for cred in export_data.get('credentials', []):
            status = cred.get('validation_status', 'unknown')
            if status == 'valid':
                stats['credentials_valid'] += 1
            elif status == 'invalid':
                stats['credentials_invalid'] += 1
            else:
                stats['credentials_unknown'] += 1
            
            # Count by type
            cred_type = cred.get('type', 'unknown')
            stats['credentials_by_type'][cred_type] = stats['credentials_by_type'].get(cred_type, 0) + 1
            
            # Count by service
            service = self._extract_service_from_type(cred_type)
            stats['credentials_by_service'][service] = stats['credentials_by_service'].get(service, 0) + 1
        
        return stats
    
    def _extract_service_from_type(self, credential_type: str) -> str:
        """Extract service name from credential type"""
        if credential_type.startswith('aws_'):
            return 'aws'
        elif credential_type.startswith('sendgrid_'):
            return 'sendgrid'
        elif credential_type.startswith('mailgun_'):
            return 'mailgun'
        elif credential_type.startswith('smtp_'):
            return 'smtp'
        elif credential_type.startswith('twilio_'):
            return 'twilio'
        elif credential_type.startswith('github_'):
            return 'github'
        elif credential_type.startswith('slack_'):
            return 'slack'
        elif credential_type.startswith('discord_'):
            return 'discord'
        elif credential_type.startswith('database_'):
            return 'database'
        elif credential_type.startswith('kubernetes_'):
            return 'kubernetes'
        elif credential_type.startswith('docker_'):
            return 'docker'
        elif credential_type.startswith('jwt_'):
            return 'jwt'
        elif 'api' in credential_type:
            return 'api'
        else:
            return 'unknown'
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        elif minutes > 0:
            return f"{int(minutes)}m {int(seconds)}s"
        else:
            return f"{seconds:.1f}s"
    
    def _prepare_json_data(self, data: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for JSON serialization"""
        if isinstance(data, dict):
            # Add metadata to the data
            json_data = data.copy()
            json_data['export_metadata'] = metadata
            return json_data
        else:
            # Wrap non-dict data
            return {
                'data': data,
                'export_metadata': metadata
            }
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for datetime and other objects"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        elif hasattr(obj, 'value'):  # For enums
            return obj.value
        else:
            return str(obj)
    
    async def _initialize_impl(self, config: Dict[str, Any]) -> None:
        """Initialize JSON exporter configuration"""
        self.pretty_print = config.get('json_pretty_print', True)
        self.indent_size = config.get('json_indent_size', 2)
        self.sort_keys = config.get('json_sort_keys', True)
        self.ensure_ascii = config.get('json_ensure_ascii', False)
    
    def supports_data_type(self, data_type: str) -> bool:
        """Check if module supports this data type"""
        # JSON can handle most data types
        return True
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats"""
        return ["json"]