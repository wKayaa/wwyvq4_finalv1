#!/usr/bin/env python3
"""
WWYVQ Framework v2 - Logger
Author: wKayaa
Date: 2025-01-15

Système de logging professionnel avec niveaux et rotation.
"""

import logging
import logging.handlers
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class LogLevel(Enum):
    """Niveaux de log"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """Entrée de log"""
    timestamp: datetime
    level: LogLevel
    message: str
    module: str
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = None


class WWYVQLogger:
    """
    Système de logging professionnel pour WWYVQ v2
    
    Fonctionnalités:
    - Logging sur console et fichier
    - Rotation automatique des fichiers
    - Niveaux de log configurables
    - Formatage professionnel
    - Logging structuré avec métadonnées
    """
    
    def __init__(self, config_manager):
        """
        Initialise le système de logging
        
        Args:
            config_manager: Gestionnaire de configuration
        """
        self.config_manager = config_manager
        self.loggers: Dict[str, logging.Logger] = {}
        self.log_entries: List[LogEntry] = []
        
        # Configuration du logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure le système de logging"""
        config = self.config_manager.get_config()
        log_config = config.logging
        
        # Création du répertoire de logs
        log_path = Path(log_config.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configuration du logger principal
        self.main_logger = logging.getLogger('wwyvq_v2')
        self.main_logger.setLevel(getattr(logging, log_config.level))
        
        # Suppression des handlers existants
        self.main_logger.handlers.clear()
        
        # Handler console
        if log_config.console_enabled:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, log_config.level))
            console_formatter = self._create_console_formatter()
            console_handler.setFormatter(console_formatter)
            self.main_logger.addHandler(console_handler)
        
        # Handler fichier avec rotation
        if log_config.file_enabled:
            file_handler = logging.handlers.RotatingFileHandler(
                log_config.file_path,
                maxBytes=log_config.max_file_size,
                backupCount=log_config.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, log_config.level))
            file_formatter = self._create_file_formatter()
            file_handler.setFormatter(file_formatter)
            self.main_logger.addHandler(file_handler)
        
        # Empêcher la propagation vers le logger racine
        self.main_logger.propagate = False
        
        print("✅ WWYVQ Logger initialized")
    
    def _create_console_formatter(self) -> logging.Formatter:
        """Crée le formateur pour la console"""
        return logging.Formatter(
            '%(asctime)s | %(levelname)8s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
    
    def _create_file_formatter(self) -> logging.Formatter:
        """Crée le formateur pour les fichiers"""
        return logging.Formatter(
            '%(asctime)s | %(levelname)8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Récupère ou crée un logger pour un module
        
        Args:
            name: Nom du logger/module
            
        Returns:
            logging.Logger: Logger configuré
        """
        if name not in self.loggers:
            logger = logging.getLogger(f'wwyvq_v2.{name}')
            logger.setLevel(self.main_logger.level)
            logger.handlers = self.main_logger.handlers
            logger.propagate = False
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def debug(self, message: str, module: str = "core", session_id: Optional[str] = None, **kwargs):
        """
        Log niveau DEBUG
        
        Args:
            message: Message à logger
            module: Module source
            session_id: ID de session optionnel
            **kwargs: Métadonnées additionnelles
        """
        self._log(LogLevel.DEBUG, message, module, session_id, kwargs)
    
    def info(self, message: str, module: str = "core", session_id: Optional[str] = None, **kwargs):
        """
        Log niveau INFO
        
        Args:
            message: Message à logger
            module: Module source
            session_id: ID de session optionnel
            **kwargs: Métadonnées additionnelles
        """
        self._log(LogLevel.INFO, message, module, session_id, kwargs)
    
    def warning(self, message: str, module: str = "core", session_id: Optional[str] = None, **kwargs):
        """
        Log niveau WARNING
        
        Args:
            message: Message à logger
            module: Module source
            session_id: ID de session optionnel
            **kwargs: Métadonnées additionnelles
        """
        self._log(LogLevel.WARNING, message, module, session_id, kwargs)
    
    def error(self, message: str, module: str = "core", session_id: Optional[str] = None, **kwargs):
        """
        Log niveau ERROR
        
        Args:
            message: Message à logger
            module: Module source
            session_id: ID de session optionnel
            **kwargs: Métadonnées additionnelles
        """
        self._log(LogLevel.ERROR, message, module, session_id, kwargs)
    
    def critical(self, message: str, module: str = "core", session_id: Optional[str] = None, **kwargs):
        """
        Log niveau CRITICAL
        
        Args:
            message: Message à logger
            module: Module source
            session_id: ID de session optionnel
            **kwargs: Métadonnées additionnelles
        """
        self._log(LogLevel.CRITICAL, message, module, session_id, kwargs)
    
    def _log(self, level: LogLevel, message: str, module: str, session_id: Optional[str], metadata: Dict[str, Any]):
        """
        Log interne
        
        Args:
            level: Niveau de log
            message: Message
            module: Module source
            session_id: ID de session
            metadata: Métadonnées
        """
        # Création de l'entrée de log
        log_entry = LogEntry(
            timestamp=datetime.utcnow(),
            level=level,
            message=message,
            module=module,
            session_id=session_id,
            metadata=metadata
        )
        
        # Stockage pour recherche
        self.log_entries.append(log_entry)
        
        # Limitation du nombre d'entrées en mémoire
        if len(self.log_entries) > 10000:
            self.log_entries = self.log_entries[-5000:]
        
        # Logging via le système Python
        logger = self.get_logger(module)
        log_message = self._format_log_message(message, session_id, metadata)
        
        if level == LogLevel.DEBUG:
            logger.debug(log_message)
        elif level == LogLevel.INFO:
            logger.info(log_message)
        elif level == LogLevel.WARNING:
            logger.warning(log_message)
        elif level == LogLevel.ERROR:
            logger.error(log_message)
        elif level == LogLevel.CRITICAL:
            logger.critical(log_message)
    
    def _format_log_message(self, message: str, session_id: Optional[str], metadata: Dict[str, Any]) -> str:
        """
        Formate le message de log
        
        Args:
            message: Message original
            session_id: ID de session
            metadata: Métadonnées
            
        Returns:
            str: Message formaté
        """
        formatted = message
        
        # Ajout de l'ID de session
        if session_id:
            formatted = f"[{session_id}] {formatted}"
        
        # Ajout des métadonnées importantes
        if metadata:
            meta_parts = []
            for key, value in metadata.items():
                if key in ['operation_id', 'target', 'duration', 'status']:
                    meta_parts.append(f"{key}={value}")
            
            if meta_parts:
                formatted = f"{formatted} | {' | '.join(meta_parts)}"
        
        return formatted
    
    def search_logs(self, query: str, level: Optional[LogLevel] = None, 
                   module: Optional[str] = None, session_id: Optional[str] = None,
                   limit: int = 100) -> List[LogEntry]:
        """
        Recherche dans les logs
        
        Args:
            query: Terme de recherche
            level: Niveau de log à filtrer
            module: Module à filtrer
            session_id: Session à filtrer
            limit: Nombre max de résultats
            
        Returns:
            List[LogEntry]: Entrées trouvées
        """
        results = []
        query_lower = query.lower()
        
        for entry in reversed(self.log_entries):  # Plus récent en premier
            if len(results) >= limit:
                break
            
            # Filtres
            if level and entry.level != level:
                continue
            
            if module and entry.module != module:
                continue
            
            if session_id and entry.session_id != session_id:
                continue
            
            # Recherche dans le message
            if query_lower in entry.message.lower():
                results.append(entry)
        
        return results
    
    def get_recent_logs(self, limit: int = 100, level: Optional[LogLevel] = None) -> List[LogEntry]:
        """
        Récupère les logs récents
        
        Args:
            limit: Nombre max de logs
            level: Niveau de log à filtrer
            
        Returns:
            List[LogEntry]: Logs récents
        """
        recent_logs = []
        
        for entry in reversed(self.log_entries):
            if len(recent_logs) >= limit:
                break
            
            if level and entry.level != level:
                continue
            
            recent_logs.append(entry)
        
        return recent_logs
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """
        Récupère les statistiques des logs
        
        Returns:
            Dict: Statistiques
        """
        stats = {
            'total_entries': len(self.log_entries),
            'by_level': {},
            'by_module': {},
            'recent_activity': 0
        }
        
        # Statistiques par niveau
        for level in LogLevel:
            stats['by_level'][level.value] = sum(
                1 for entry in self.log_entries if entry.level == level
            )
        
        # Statistiques par module
        for entry in self.log_entries:
            module = entry.module
            if module not in stats['by_module']:
                stats['by_module'][module] = 0
            stats['by_module'][module] += 1
        
        # Activité récente (dernière heure)
        one_hour_ago = datetime.utcnow().timestamp() - 3600
        stats['recent_activity'] = sum(
            1 for entry in self.log_entries 
            if entry.timestamp.timestamp() > one_hour_ago
        )
        
        return stats
    
    def export_logs(self, file_path: str, format_type: str = "json", 
                   filters: Optional[Dict[str, Any]] = None):
        """
        Exporte les logs
        
        Args:
            file_path: Chemin du fichier d'export
            format_type: Format (json, csv, txt)
            filters: Filtres à appliquer
        """
        try:
            # Application des filtres
            entries_to_export = self.log_entries
            
            if filters:
                filtered_entries = []
                for entry in entries_to_export:
                    if self._matches_filters(entry, filters):
                        filtered_entries.append(entry)
                entries_to_export = filtered_entries
            
            # Export selon le format
            if format_type.lower() == "json":
                self._export_json(entries_to_export, file_path)
            elif format_type.lower() == "csv":
                self._export_csv(entries_to_export, file_path)
            elif format_type.lower() == "txt":
                self._export_txt(entries_to_export, file_path)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
            
            print(f"📁 Exported {len(entries_to_export)} log entries to {file_path}")
            
        except Exception as e:
            print(f"❌ Failed to export logs: {e}")
    
    def _matches_filters(self, entry: LogEntry, filters: Dict[str, Any]) -> bool:
        """Vérifie si une entrée correspond aux filtres"""
        if 'level' in filters and entry.level.value != filters['level']:
            return False
        
        if 'module' in filters and entry.module != filters['module']:
            return False
        
        if 'session_id' in filters and entry.session_id != filters['session_id']:
            return False
        
        if 'query' in filters and filters['query'].lower() not in entry.message.lower():
            return False
        
        return True
    
    def _export_json(self, entries: List[LogEntry], file_path: str):
        """Exporte en JSON"""
        import json
        
        data = []
        for entry in entries:
            data.append({
                'timestamp': entry.timestamp.isoformat(),
                'level': entry.level.value,
                'message': entry.message,
                'module': entry.module,
                'session_id': entry.session_id,
                'metadata': entry.metadata
            })
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _export_csv(self, entries: List[LogEntry], file_path: str):
        """Exporte en CSV"""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Level', 'Module', 'Session', 'Message'])
            
            for entry in entries:
                writer.writerow([
                    entry.timestamp.isoformat(),
                    entry.level.value,
                    entry.module,
                    entry.session_id or '',
                    entry.message
                ])
    
    def _export_txt(self, entries: List[LogEntry], file_path: str):
        """Exporte en TXT"""
        with open(file_path, 'w', encoding='utf-8') as f:
            for entry in entries:
                session_part = f" [{entry.session_id}]" if entry.session_id else ""
                f.write(f"{entry.timestamp.isoformat()} | {entry.level.value:8s} | {entry.module}{session_part} | {entry.message}\n")
    
    def set_level(self, level: str):
        """
        Change le niveau de log
        
        Args:
            level: Nouveau niveau (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        try:
            log_level = getattr(logging, level.upper())
            self.main_logger.setLevel(log_level)
            
            # Mise à jour des handlers
            for handler in self.main_logger.handlers:
                handler.setLevel(log_level)
            
            # Mise à jour des loggers modules
            for logger in self.loggers.values():
                logger.setLevel(log_level)
            
            print(f"📊 Log level changed to {level.upper()}")
            
        except AttributeError:
            print(f"❌ Invalid log level: {level}")
    
    def clear_logs(self):
        """Efface les logs en mémoire"""
        self.log_entries.clear()
        print("🧹 Log entries cleared")
    
    def reload_config(self):
        """Recharge la configuration du logging"""
        self._setup_logging()
        print("🔄 Logger configuration reloaded")