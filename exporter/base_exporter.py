#!/usr/bin/env python3
"""
WWYVQ v2.1 Base Exporter Module
Base class for all export modules

Author: wKayaa
Date: 2025-01-07
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
import json


@dataclass
class ExportResult:
    """Result of export operation"""
    success: bool
    file_path: Optional[str] = None
    export_type: str = "unknown"
    records_exported: int = 0
    file_size_bytes: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseExporterModule(ABC):
    """
    Base class for all export modules
    Provides common functionality and interface
    """
    
    def __init__(self, name: str, description: str = "", file_extension: str = ""):
        """Initialize base exporter module"""
        self.name = name
        self.description = description
        self.file_extension = file_extension
        self.logger = logging.getLogger(f"ExporterModule.{name}")
        self.stats = {
            'exports_created': 0,
            'records_exported': 0,
            'export_errors': 0,
            'total_file_size': 0
        }
        
        # Export configuration
        self.output_directory = Path("./results")
        self.create_subdirectories = True
        self.timestamp_files = True
        self.compression_enabled = False
        self.encryption_enabled = False
    
    @abstractmethod
    async def execute_async(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the module asynchronously"""
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the module synchronously"""
        pass
    
    async def export_data(self, data: Any, filename: Optional[str] = None, 
                         metadata: Optional[Dict[str, Any]] = None) -> ExportResult:
        """Export data to file"""
        try:
            # Generate filename if not provided
            if not filename:
                filename = self._generate_filename(metadata or {})
            
            # Ensure output directory exists
            output_path = self._prepare_output_path(filename)
            
            # Perform the actual export
            result = await self._export_data_impl(data, output_path, metadata or {})
            
            # Update statistics
            if result.success:
                self.stats['exports_created'] += 1
                self.stats['records_exported'] += result.records_exported
                self.stats['total_file_size'] += result.file_size_bytes
            else:
                self.stats['export_errors'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error exporting data: {e}")
            self.stats['export_errors'] += 1
            return ExportResult(
                success=False,
                export_type=self.name,
                error_message=str(e)
            )
    
    @abstractmethod
    async def _export_data_impl(self, data: Any, output_path: Path, 
                               metadata: Dict[str, Any]) -> ExportResult:
        """Implementation of data export"""
        pass
    
    def _generate_filename(self, metadata: Dict[str, Any]) -> str:
        """Generate filename for export"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        job_id = metadata.get('job_id', 'unknown')
        
        if self.timestamp_files:
            filename = f"{self.name.lower()}_{job_id}_{timestamp}{self.file_extension}"
        else:
            filename = f"{self.name.lower()}_{job_id}{self.file_extension}"
        
        return filename
    
    def _prepare_output_path(self, filename: str) -> Path:
        """Prepare output path and create directories"""
        # Create output directory if it doesn't exist
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectory if enabled
        if self.create_subdirectories:
            timestamp = datetime.utcnow().strftime("%Y%m%d")
            subdir = self.output_directory / timestamp
            subdir.mkdir(parents=True, exist_ok=True)
            return subdir / filename
        else:
            return self.output_directory / filename
    
    def _get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes"""
        try:
            return file_path.stat().st_size if file_path.exists() else 0
        except Exception:
            return 0
    
    def _count_records(self, data: Any) -> int:
        """Count number of records in data"""
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            # Try to find the main data collection
            for key in ['credentials', 'results', 'items', 'data']:
                if key in data and isinstance(data[key], list):
                    return len(data[key])
            return 1  # Single record
        else:
            return 1  # Single record
    
    def get_stats(self) -> Dict[str, Any]:
        """Get module statistics"""
        return {
            'name': self.name,
            'description': self.description,
            'stats': self.stats.copy()
        }
    
    def reset_stats(self):
        """Reset module statistics"""
        self.stats = {
            'exports_created': 0,
            'records_exported': 0,
            'export_errors': 0,
            'total_file_size': 0
        }
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the module with configuration"""
        try:
            self.logger.info(f"🔧 Initializing {self.name} module")
            
            # Update configuration
            self.output_directory = Path(config.get('output_directory', './results'))
            self.create_subdirectories = config.get('create_subdirectories', True)
            self.timestamp_files = config.get('timestamp_files', True)
            self.compression_enabled = config.get('compression', False)
            self.encryption_enabled = config.get('encryption', False)
            
            await self._initialize_impl(config)
            self.logger.info(f"✅ {self.name} module initialized")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {self.name} module: {e}")
            return False
    
    async def _initialize_impl(self, config: Dict[str, Any]) -> None:
        """Implementation of module initialization"""
        pass
    
    async def shutdown(self) -> None:
        """Shutdown the module"""
        try:
            self.logger.info(f"🛑 Shutting down {self.name} module")
            await self._shutdown_impl()
            self.logger.info(f"✅ {self.name} module shutdown complete")
        except Exception as e:
            self.logger.error(f"❌ Error shutting down {self.name} module: {e}")
    
    async def _shutdown_impl(self) -> None:
        """Implementation of module shutdown"""
        pass
    
    def supports_data_type(self, data_type: str) -> bool:
        """Check if module supports this data type"""
        return True  # Default implementation accepts all data types
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats"""
        return [self.file_extension.lstrip('.')]  # Default implementation
    
    async def export_batch(self, data_items: List[Any], 
                          metadata: Optional[Dict[str, Any]] = None) -> List[ExportResult]:
        """Export a batch of data items"""
        try:
            self.logger.info(f"📊 Exporting batch of {len(data_items)} items")
            
            results = []
            for i, data in enumerate(data_items):
                # Generate unique filename for each item
                item_metadata = (metadata or {}).copy()
                item_metadata['batch_index'] = i
                
                result = await self.export_data(data, metadata=item_metadata)
                results.append(result)
            
            self.logger.info(f"✅ Batch export complete: {len(results)} files created")
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Batch export failed: {e}")
            return []
    
    async def create_host_file(self, targets: List[str], 
                              metadata: Optional[Dict[str, Any]] = None) -> ExportResult:
        """Create host file from targets"""
        try:
            # Deduplicate and clean targets
            unique_targets = []
            seen = set()
            
            for target in targets:
                # Extract hostname/IP from target
                clean_target = self._extract_hostname(target)
                if clean_target and clean_target not in seen:
                    unique_targets.append(clean_target)
                    seen.add(clean_target)
            
            # Sort targets
            unique_targets.sort()
            
            # Generate filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            job_id = (metadata or {}).get('job_id', 'unknown')
            filename = f"hosts_{job_id}_{timestamp}.txt"
            
            # Prepare output path
            output_path = self._prepare_output_path(filename)
            
            # Write host file
            with open(output_path, 'w') as f:
                for target in unique_targets:
                    f.write(f"{target}\n")
            
            file_size = self._get_file_size(output_path)
            
            self.logger.info(f"📝 Created host file: {output_path} ({len(unique_targets)} hosts)")
            
            return ExportResult(
                success=True,
                file_path=str(output_path),
                export_type="host_file",
                records_exported=len(unique_targets),
                file_size_bytes=file_size,
                metadata={'format': 'text', 'host_count': len(unique_targets)}
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error creating host file: {e}")
            return ExportResult(
                success=False,
                export_type="host_file",
                error_message=str(e)
            )
    
    def _extract_hostname(self, target: str) -> Optional[str]:
        """Extract hostname or IP from target"""
        try:
            # Remove protocol if present
            if '://' in target:
                target = target.split('://', 1)[1]
            
            # Remove path if present
            if '/' in target:
                target = target.split('/', 1)[0]
            
            # Remove port if present
            if ':' in target and not target.count(':') > 1:  # Not IPv6
                target = target.split(':', 1)[0]
            
            # Basic validation
            if target and len(target) > 0 and '.' in target:
                return target
            
            return None
            
        except Exception:
            return None
    
    def create_metadata(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create metadata for export from context"""
        metadata = {
            'export_timestamp': datetime.utcnow().isoformat(),
            'wwyvq_version': '2.1',
            'exporter': self.name,
            'job_id': context.get('job_id', 'unknown')
        }
        
        # Add job configuration if available
        if 'config' in context:
            config = context['config']
            metadata.update({
                'job_name': getattr(config, 'name', 'unknown'),
                'execution_mode': getattr(config, 'mode', 'unknown').value if hasattr(getattr(config, 'mode', None), 'value') else str(getattr(config, 'mode', 'unknown')),
                'targets_count': len(getattr(config, 'targets', [])),
                'max_concurrent': getattr(config, 'max_concurrent', 0),
                'kubernetes_focus': getattr(config, 'kubernetes_focus', False)
            })
        
        # Add timing information
        if 'start_time' in context:
            metadata['job_start_time'] = context['start_time'].isoformat() if hasattr(context['start_time'], 'isoformat') else str(context['start_time'])
            duration = datetime.utcnow() - context['start_time']
            metadata['job_duration_seconds'] = duration.total_seconds()
        
        return metadata