#!/usr/bin/env python3
"""
WWYVQ Framework v2 - Results Organizer
Author: wKayaa
Date: 2025-01-15

Module d'organisation et d'export des résultats.
"""

import json
import csv
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
import shutil


@dataclass
class OperationResults:
    """Résultats d'une opération"""
    operation_id: str
    operation_type: str
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "completed"
    targets: List[str] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExportOptions:
    """Options d'export"""
    format_type: str = "json"  # json, csv, html, xml
    include_sensitive: bool = False
    mask_credentials: bool = True
    compress: bool = False
    split_by_service: bool = False


class ResultsOrganizer:
    """
    Organisateur de résultats avec export avancé
    
    Responsabilités:
    - Organisation des résultats par session/service
    - Export multi-format (JSON, CSV, HTML, XML)
    - Statistiques détaillées
    - Archivage et compression
    """
    
    def __init__(self, config_manager, logger, base_results_dir: str = "results"):
        """
        Initialise l'organisateur de résultats
        
        Args:
            config_manager: Gestionnaire de configuration
            logger: Logger WWYVQ
            base_results_dir: Répertoire de base pour les résultats
        """
        self.config_manager = config_manager
        self.logger = logger
        
        # Répertoires
        self.base_results_dir = Path(base_results_dir)
        self.base_results_dir.mkdir(exist_ok=True)
        
        # Stockage des résultats
        self.operation_results: Dict[str, OperationResults] = {}
        self.current_session_dir: Optional[Path] = None
        
        # Statistiques globales
        self.global_stats = {
            'total_operations': 0,
            'total_results': 0,
            'total_exports': 0,
            'created_at': datetime.utcnow().isoformat()
        }
    
    def create_session_directory(self, session_id: str) -> Path:
        """
        Crée un répertoire pour une session
        
        Args:
            session_id: ID de la session
            
        Returns:
            Path: Chemin du répertoire de session
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        session_dir_name = f"session_{session_id}_{timestamp}"
        session_dir = self.base_results_dir / session_dir_name
        
        # Création de la structure
        session_dir.mkdir(exist_ok=True)
        (session_dir / "exports").mkdir(exist_ok=True)
        (session_dir / "logs").mkdir(exist_ok=True)
        (session_dir / "raw_data").mkdir(exist_ok=True)
        (session_dir / "reports").mkdir(exist_ok=True)
        
        self.current_session_dir = session_dir
        
        self.logger.info(
            f"Session directory created: {session_dir}",
            module="exporter.results_organizer",
            session_id=session_id
        )
        
        return session_dir
    
    def store_operation_results(self, operation_results: OperationResults):
        """
        Stocke les résultats d'une opération
        
        Args:
            operation_results: Résultats à stocker
        """
        self.operation_results[operation_results.operation_id] = operation_results
        self.global_stats['total_operations'] += 1
        
        # Sauvegarde immédiate
        if self.current_session_dir:
            self._save_operation_to_disk(operation_results)
        
        self.logger.info(
            f"Operation results stored: {operation_results.operation_id}",
            module="exporter.results_organizer",
            operation_type=operation_results.operation_type
        )
    
    def _save_operation_to_disk(self, operation_results: OperationResults):
        """Sauvegarde les résultats sur disque"""
        if not self.current_session_dir:
            return
        
        raw_data_dir = self.current_session_dir / "raw_data"
        file_path = raw_data_dir / f"{operation_results.operation_id}.json"
        
        try:
            # Conversion en dictionnaire sérialisable
            data = asdict(operation_results)
            data['start_time'] = operation_results.start_time.isoformat()
            if operation_results.end_time:
                data['end_time'] = operation_results.end_time.isoformat()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(
                f"Failed to save operation results: {e}",
                module="exporter.results_organizer"
            )
    
    def export_results(self, export_options: ExportOptions, 
                      operation_ids: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Exporte les résultats selon les options spécifiées
        
        Args:
            export_options: Options d'export
            operation_ids: IDs des opérations à exporter (toutes si None)
            
        Returns:
            Dict: Chemins des fichiers exportés
        """
        if not self.current_session_dir:
            raise ValueError("No active session directory")
        
        # Sélection des opérations à exporter
        if operation_ids:
            operations_to_export = {
                op_id: self.operation_results[op_id] 
                for op_id in operation_ids 
                if op_id in self.operation_results
            }
        else:
            operations_to_export = self.operation_results
        
        exports_dir = self.current_session_dir / "exports"
        exported_files = {}
        
        # Export selon le format
        if export_options.format_type.lower() == "json":
            exported_files.update(self._export_json(operations_to_export, exports_dir, export_options))
        
        elif export_options.format_type.lower() == "csv":
            exported_files.update(self._export_csv(operations_to_export, exports_dir, export_options))
        
        elif export_options.format_type.lower() == "html":
            exported_files.update(self._export_html(operations_to_export, exports_dir, export_options))
        
        elif export_options.format_type.lower() == "xml":
            exported_files.update(self._export_xml(operations_to_export, exports_dir, export_options))
        
        else:
            raise ValueError(f"Unsupported export format: {export_options.format_type}")
        
        # Compression si demandée
        if export_options.compress:
            exported_files.update(self._compress_exports(exported_files, exports_dir))
        
        self.global_stats['total_exports'] += len(exported_files)
        
        self.logger.info(
            f"Results exported: {len(exported_files)} files",
            module="exporter.results_organizer",
            format_type=export_options.format_type
        )
        
        return exported_files
    
    def _export_json(self, operations: Dict[str, OperationResults], 
                    exports_dir: Path, options: ExportOptions) -> Dict[str, str]:
        """Exporte en format JSON"""
        exported_files = {}
        
        if options.split_by_service:
            # Export par service
            services_data = self._group_by_service(operations)
            
            for service, data in services_data.items():
                filename = f"results_{service}.json"
                file_path = exports_dir / filename
                
                export_data = self._prepare_export_data(data, options)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                exported_files[service] = str(file_path)
        
        else:
            # Export global
            filename = f"results_all_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            file_path = exports_dir / filename
            
            export_data = self._prepare_export_data(operations, options)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            exported_files['all'] = str(file_path)
        
        return exported_files
    
    def _export_csv(self, operations: Dict[str, OperationResults], 
                   exports_dir: Path, options: ExportOptions) -> Dict[str, str]:
        """Exporte en format CSV"""
        exported_files = {}
        
        # Extract all results for CSV
        all_results = []
        for operation in operations.values():
            for result_type, results in operation.results.items():
                if isinstance(results, list):
                    for result in results:
                        if isinstance(result, dict):
                            flat_result = self._flatten_dict(result)
                            flat_result.update({
                                'operation_id': operation.operation_id,
                                'operation_type': operation.operation_type,
                                'session_id': operation.session_id,
                                'result_type': result_type
                            })
                            all_results.append(flat_result)
        
        if all_results:
            filename = f"results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            file_path = exports_dir / filename
            
            # Get all unique fields
            all_fields = set()
            for result in all_results:
                all_fields.update(result.keys())
            
            # Mask sensitive data if requested
            if options.mask_credentials:
                all_results = self._mask_sensitive_data(all_results)
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(all_fields))
                writer.writeheader()
                writer.writerows(all_results)
            
            exported_files['csv'] = str(file_path)
        
        return exported_files
    
    def _export_html(self, operations: Dict[str, OperationResults], 
                    exports_dir: Path, options: ExportOptions) -> Dict[str, str]:
        """Exporte en format HTML"""
        exported_files = {}
        
        filename = f"results_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
        file_path = exports_dir / filename
        
        html_content = self._generate_html_report(operations, options)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        exported_files['html'] = str(file_path)
        
        return exported_files
    
    def _export_xml(self, operations: Dict[str, OperationResults], 
                   exports_dir: Path, options: ExportOptions) -> Dict[str, str]:
        """Exporte en format XML"""
        exported_files = {}
        
        filename = f"results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xml"
        file_path = exports_dir / filename
        
        xml_content = self._generate_xml(operations, options)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        exported_files['xml'] = str(file_path)
        
        return exported_files
    
    def _group_by_service(self, operations: Dict[str, OperationResults]) -> Dict[str, Dict]:
        """Groupe les résultats par service"""
        services_data = {}
        
        for operation in operations.values():
            for result_type, results in operation.results.items():
                if isinstance(results, list):
                    for result in results:
                        if isinstance(result, dict):
                            service = result.get('service', 'unknown')
                            
                            if service not in services_data:
                                services_data[service] = {}
                            
                            if operation.operation_id not in services_data[service]:
                                services_data[service][operation.operation_id] = operation
        
        return services_data
    
    def _prepare_export_data(self, data: Union[Dict[str, OperationResults], Dict], 
                           options: ExportOptions) -> Dict[str, Any]:
        """Prépare les données pour l'export"""
        if isinstance(data, dict) and all(isinstance(v, OperationResults) for v in data.values()):
            # Conversion des OperationResults
            export_data = {
                'metadata': {
                    'export_time': datetime.utcnow().isoformat(),
                    'wwyvq_version': '2.0.0',
                    'operations_count': len(data)
                },
                'operations': {}
            }
            
            for op_id, operation in data.items():
                op_data = asdict(operation)
                op_data['start_time'] = operation.start_time.isoformat()
                if operation.end_time:
                    op_data['end_time'] = operation.end_time.isoformat()
                
                # Masquage des données sensibles
                if options.mask_credentials:
                    op_data = self._mask_sensitive_data([op_data])[0]
                
                # Exclusion des données sensibles
                if not options.include_sensitive:
                    op_data = self._filter_sensitive_data(op_data)
                
                export_data['operations'][op_id] = op_data
        
        else:
            export_data = data
        
        return export_data
    
    def _mask_sensitive_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Masque les données sensibles"""
        sensitive_fields = ['password', 'token', 'api_key', 'secret', 'key', 'auth']
        
        masked_data = []
        for item in data:
            masked_item = {}
            for key, value in item.items():
                if any(sensitive in key.lower() for sensitive in sensitive_fields):
                    if isinstance(value, str) and len(value) > 6:
                        masked_item[key] = value[:3] + "*" * (len(value) - 6) + value[-3:]
                    else:
                        masked_item[key] = "*" * len(str(value))
                else:
                    masked_item[key] = value
            masked_data.append(masked_item)
        
        return masked_data
    
    def _filter_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filtre les données sensibles"""
        sensitive_fields = ['password', 'token', 'api_key', 'secret', 'private_key']
        
        filtered_data = {}
        for key, value in data.items():
            if not any(sensitive in key.lower() for sensitive in sensitive_fields):
                if isinstance(value, dict):
                    filtered_data[key] = self._filter_sensitive_data(value)
                elif isinstance(value, list):
                    filtered_data[key] = [
                        self._filter_sensitive_data(item) if isinstance(item, dict) else item
                        for item in value
                    ]
                else:
                    filtered_data[key] = value
        
        return filtered_data
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """Applatit un dictionnaire imbriqué"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                items.append((new_key, json.dumps(v) if v else ''))
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _generate_html_report(self, operations: Dict[str, OperationResults], 
                            options: ExportOptions) -> str:
        """Génère un rapport HTML"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>WWYVQ Framework v2 - Results Report</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ background: #ecf0f1; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .operation {{ border: 1px solid #bdc3c7; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .operation-header {{ background: #3498db; color: white; padding: 10px; margin: -15px -15px 15px -15px; border-radius: 5px 5px 0 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f2f2f2; }}
        .success {{ color: #27ae60; }}
        .error {{ color: #e74c3c; }}
        .warning {{ color: #f39c12; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 WWYVQ Framework v2 - Results Report</h1>
        <p>Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
    </div>
    
    <div class="summary">
        <h2>📊 Summary</h2>
        <ul>
            <li><strong>Total Operations:</strong> {len(operations)}</li>
            <li><strong>Export Options:</strong> {options.format_type.upper()}, Mask Credentials: {options.mask_credentials}</li>
        </ul>
    </div>
"""
        
        # Ajout des opérations
        for operation in operations.values():
            html += f"""
    <div class="operation">
        <div class="operation-header">
            <h3>{operation.operation_type.upper()} - {operation.operation_id}</h3>
        </div>
        
        <table>
            <tr><th>Session ID</th><td>{operation.session_id}</td></tr>
            <tr><th>Start Time</th><td>{operation.start_time.strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
            <tr><th>Status</th><td class="{'success' if operation.status == 'completed' else 'error'}">{operation.status.upper()}</td></tr>
            <tr><th>Targets Count</th><td>{len(operation.targets)}</td></tr>
        </table>
        
        <h4>Results:</h4>
        <pre>{json.dumps(operation.results, indent=2)}</pre>
        
        <h4>Statistics:</h4>
        <pre>{json.dumps(operation.statistics, indent=2)}</pre>
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        return html
    
    def _generate_xml(self, operations: Dict[str, OperationResults], 
                     options: ExportOptions) -> str:
        """Génère un export XML"""
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<wwyvq_results>
    <metadata>
        <export_time>{datetime.utcnow().isoformat()}</export_time>
        <wwyvq_version>2.0.0</wwyvq_version>
        <operations_count>{len(operations)}</operations_count>
    </metadata>
    
    <operations>
"""
        
        for operation in operations.values():
            xml += f"""
        <operation id="{operation.operation_id}">
            <type>{operation.operation_type}</type>
            <session_id>{operation.session_id}</session_id>
            <start_time>{operation.start_time.isoformat()}</start_time>
            <status>{operation.status}</status>
            <targets_count>{len(operation.targets)}</targets_count>
            <results>{json.dumps(operation.results)}</results>
            <statistics>{json.dumps(operation.statistics)}</statistics>
        </operation>
"""
        
        xml += """
    </operations>
</wwyvq_results>
"""
        
        return xml
    
    def _compress_exports(self, exported_files: Dict[str, str], 
                         exports_dir: Path) -> Dict[str, str]:
        """Compresse les fichiers exportés"""
        import zipfile
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"wwyvq_results_{timestamp}.zip"
        zip_path = exports_dir / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for name, file_path in exported_files.items():
                zipf.write(file_path, Path(file_path).name)
        
        # Suppression des fichiers originaux
        for file_path in exported_files.values():
            Path(file_path).unlink()
        
        return {'compressed': str(zip_path)}
    
    def generate_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Génère un résumé de session
        
        Args:
            session_id: ID de la session
            
        Returns:
            Dict: Résumé de la session
        """
        session_operations = {
            op_id: op for op_id, op in self.operation_results.items()
            if op.session_id == session_id
        }
        
        # Statistiques globales
        total_operations = len(session_operations)
        total_targets = sum(len(op.targets) for op in session_operations.values())
        
        # Statistiques par type d'opération
        operation_types = {}
        for operation in session_operations.values():
            op_type = operation.operation_type
            if op_type not in operation_types:
                operation_types[op_type] = 0
            operation_types[op_type] += 1
        
        # Temps total
        start_times = [op.start_time for op in session_operations.values()]
        end_times = [op.end_time for op in session_operations.values() if op.end_time]
        
        total_duration = None
        if start_times and end_times:
            total_duration = max(end_times) - min(start_times)
        
        summary = {
            'session_id': session_id,
            'total_operations': total_operations,
            'total_targets': total_targets,
            'operation_types': operation_types,
            'total_duration': str(total_duration) if total_duration else None,
            'session_directory': str(self.current_session_dir) if self.current_session_dir else None,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        # Sauvegarde du résumé
        if self.current_session_dir:
            summary_file = self.current_session_dir / "session_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return summary
    
    def cleanup_old_sessions(self, days_to_keep: int = 7):
        """
        Nettoie les anciennes sessions
        
        Args:
            days_to_keep: Nombre de jours à conserver
        """
        cutoff_date = datetime.utcnow().timestamp() - (days_to_keep * 24 * 3600)
        
        for session_dir in self.base_results_dir.iterdir():
            if session_dir.is_dir() and session_dir.name.startswith('session_'):
                try:
                    if session_dir.stat().st_mtime < cutoff_date:
                        shutil.rmtree(session_dir)
                        self.logger.info(
                            f"Cleaned up old session directory: {session_dir.name}",
                            module="exporter.results_organizer"
                        )
                except Exception as e:
                    self.logger.error(
                        f"Failed to cleanup session directory {session_dir}: {e}",
                        module="exporter.results_organizer"
                    )
    
    def get_organizer_statistics(self) -> Dict[str, Any]:
        """
        Récupère les statistiques de l'organisateur
        
        Returns:
            Dict: Statistiques
        """
        return {
            'total_operations': len(self.operation_results),
            'current_session_dir': str(self.current_session_dir) if self.current_session_dir else None,
            'global_stats': self.global_stats,
            'base_results_dir': str(self.base_results_dir)
        }