#!/usr/bin/env python3
"""
WWYVQ Framework v2 - Session Manager
Author: wKayaa
Date: 2025-01-15

Gestionnaire de sessions avec persistance et récupération d'état.
"""

import json
import uuid
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict


@dataclass
class SessionData:
    """Données de session"""
    session_id: str
    created_at: datetime
    last_activity: datetime
    user_info: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)
    targets: List[str] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)


class SessionManager:
    """
    Gestionnaire de sessions d'exploitation
    
    Responsabilités:
    - Création et gestion des sessions
    - Persistance des données de session
    - Récupération d'état après interruption
    - Nettoyage des sessions expirées
    """
    
    def __init__(self, config_manager):
        """
        Initialise le gestionnaire de sessions
        
        Args:
            config_manager: Gestionnaire de configuration
        """
        self.config_manager = config_manager
        self.sessions_dir = Path("sessions")
        self.sessions_dir.mkdir(exist_ok=True)
        
        self.active_sessions: Dict[str, SessionData] = {}
        self.current_session_id: Optional[str] = None
        
        # Configuration de nettoyage automatique
        self.cleanup_interval = 3600  # 1 heure
        self.last_cleanup = time.time()
    
    async def initialize(self):
        """Initialise le gestionnaire de sessions"""
        # Chargement des sessions existantes
        await self._load_existing_sessions()
        
        # Nettoyage initial
        await self._cleanup_expired_sessions()
        
        print("✅ Session Manager initialized")
    
    async def create_session(self, user_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Crée une nouvelle session
        
        Args:
            user_info: Informations utilisateur optionnelles
            
        Returns:
            str: ID de la session créée
        """
        session_id = str(uuid.uuid4())[:8]
        current_time = datetime.utcnow()
        
        session_data = SessionData(
            session_id=session_id,
            created_at=current_time,
            last_activity=current_time,
            user_info=user_info or {},
            configuration=self._get_session_config(),
            statistics=self._init_session_stats()
        )
        
        self.active_sessions[session_id] = session_data
        self.current_session_id = session_id
        
        # Sauvegarde de la session
        await self._save_session(session_data)
        
        print(f"🆕 Session created: {session_id}")
        return session_id
    
    async def restore_session(self, session_id: str) -> bool:
        """
        Restaure une session existante
        
        Args:
            session_id: ID de la session à restaurer
            
        Returns:
            bool: True si la restauration réussit
        """
        session_path = self.sessions_dir / f"{session_id}.json"
        
        if not session_path.exists():
            print(f"❌ Session {session_id} not found")
            return False
        
        try:
            with open(session_path, 'r', encoding='utf-8') as f:
                session_dict = json.load(f)
            
            # Conversion des dates
            session_dict['created_at'] = datetime.fromisoformat(session_dict['created_at'])
            session_dict['last_activity'] = datetime.fromisoformat(session_dict['last_activity'])
            
            session_data = SessionData(**session_dict)
            
            # Vérification de l'expiration
            if self._is_session_expired(session_data):
                print(f"⚠️ Session {session_id} has expired")
                return False
            
            # Mise à jour de l'activité
            session_data.last_activity = datetime.utcnow()
            
            self.active_sessions[session_id] = session_data
            self.current_session_id = session_id
            
            await self._save_session(session_data)
            
            print(f"🔄 Session restored: {session_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to restore session {session_id}: {e}")
            return False
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]):
        """
        Met à jour une session
        
        Args:
            session_id: ID de la session
            updates: Dictionnaire des mises à jour
        """
        if session_id not in self.active_sessions:
            print(f"❌ Session {session_id} not found")
            return
        
        session = self.active_sessions[session_id]
        session.last_activity = datetime.utcnow()
        
        # Application des mises à jour
        for key, value in updates.items():
            if key == 'targets':
                session.targets = value
            elif key == 'results':
                session.results.update(value)
            elif key == 'statistics':
                session.statistics.update(value)
            elif key == 'metadata':
                session.metadata.update(value)
            elif key == 'status':
                session.status = value
        
        await self._save_session(session)
    
    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Récupère une session
        
        Args:
            session_id: ID de la session
            
        Returns:
            SessionData ou None si non trouvée
        """
        return self.active_sessions.get(session_id)
    
    async def get_current_session(self) -> Optional[SessionData]:
        """
        Récupère la session courante
        
        Returns:
            SessionData ou None si aucune session active
        """
        if self.current_session_id:
            return self.active_sessions.get(self.current_session_id)
        return None
    
    async def list_sessions(self) -> List[Dict[str, Any]]:
        """
        Liste toutes les sessions
        
        Returns:
            List des informations de session
        """
        sessions = []
        
        for session_id, session_data in self.active_sessions.items():
            sessions.append({
                'session_id': session_id,
                'created_at': session_data.created_at.isoformat(),
                'last_activity': session_data.last_activity.isoformat(),
                'status': session_data.status,
                'targets_count': len(session_data.targets),
                'results_count': len(session_data.results),
                'is_current': session_id == self.current_session_id
            })
        
        return sorted(sessions, key=lambda x: x['last_activity'], reverse=True)
    
    async def close_session(self, session_id: str):
        """
        Ferme une session
        
        Args:
            session_id: ID de la session à fermer
        """
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.status = "closed"
            session.last_activity = datetime.utcnow()
            
            await self._save_session(session)
            
            # Supprimer de la mémoire
            del self.active_sessions[session_id]
            
            if self.current_session_id == session_id:
                self.current_session_id = None
            
            print(f"🔒 Session closed: {session_id}")
    
    async def _load_existing_sessions(self):
        """Charge les sessions existantes depuis le disque"""
        session_files = list(self.sessions_dir.glob("*.json"))
        
        for session_file in session_files:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_dict = json.load(f)
                
                # Conversion des dates
                session_dict['created_at'] = datetime.fromisoformat(session_dict['created_at'])
                session_dict['last_activity'] = datetime.fromisoformat(session_dict['last_activity'])
                
                session_data = SessionData(**session_dict)
                
                # Vérifier si la session n'est pas expirée
                if not self._is_session_expired(session_data):
                    self.active_sessions[session_data.session_id] = session_data
                
            except Exception as e:
                print(f"⚠️ Failed to load session {session_file}: {e}")
    
    async def _save_session(self, session_data: SessionData):
        """Sauvegarde une session sur le disque"""
        session_path = self.sessions_dir / f"{session_data.session_id}.json"
        
        try:
            session_dict = asdict(session_data)
            
            # Conversion des dates en string
            session_dict['created_at'] = session_data.created_at.isoformat()
            session_dict['last_activity'] = session_data.last_activity.isoformat()
            
            with open(session_path, 'w', encoding='utf-8') as f:
                json.dump(session_dict, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Failed to save session {session_data.session_id}: {e}")
    
    def _is_session_expired(self, session_data: SessionData) -> bool:
        """Vérifie si une session est expirée"""
        config = self.config_manager.get_config()
        timeout = config.security.session_timeout
        
        last_activity = session_data.last_activity
        expiry_time = last_activity + timedelta(seconds=timeout)
        
        return datetime.utcnow() > expiry_time
    
    async def _cleanup_expired_sessions(self):
        """Nettoie les sessions expirées"""
        current_time = time.time()
        
        # Nettoyage périodique
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        expired_sessions = []
        
        for session_id, session_data in self.active_sessions.items():
            if self._is_session_expired(session_data):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            await self.close_session(session_id)
            
            # Suppression du fichier
            session_path = self.sessions_dir / f"{session_id}.json"
            if session_path.exists():
                session_path.unlink()
        
        if expired_sessions:
            print(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")
        
        self.last_cleanup = current_time
    
    def _get_session_config(self) -> Dict[str, Any]:
        """Récupère la configuration pour la session"""
        config = self.config_manager.get_config()
        return {
            'core': {
                'max_concurrent': config.core.max_concurrent,
                'timeout': config.core.timeout,
                'safe_mode': config.core.safe_mode
            },
            'version': config.version
        }
    
    def _init_session_stats(self) -> Dict[str, Any]:
        """Initialise les statistiques de session"""
        return {
            'targets_processed': 0,
            'clusters_found': 0,
            'clusters_exploited': 0,
            'secrets_extracted': 0,
            'operations_completed': 0,
            'operations_failed': 0,
            'start_time': datetime.utcnow().isoformat()
        }
    
    async def get_session_statistics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les statistiques d'une session
        
        Args:
            session_id: ID de la session
            
        Returns:
            Dict des statistiques ou None
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        stats = session.statistics.copy()
        
        # Calcul de durée
        if 'start_time' in stats:
            start_time = datetime.fromisoformat(stats['start_time'])
            duration = datetime.utcnow() - start_time
            stats['duration_seconds'] = duration.total_seconds()
        
        return stats
    
    async def export_session(self, session_id: str, export_path: str):
        """
        Exporte une session complète
        
        Args:
            session_id: ID de la session
            export_path: Chemin d'export
        """
        session = self.active_sessions.get(session_id)
        if not session:
            print(f"❌ Session {session_id} not found")
            return
        
        export_data = {
            'session_info': asdict(session),
            'export_time': datetime.utcnow().isoformat(),
            'wwyvq_version': '2.0.0'
        }
        
        # Conversion des dates
        export_data['session_info']['created_at'] = session.created_at.isoformat()
        export_data['session_info']['last_activity'] = session.last_activity.isoformat()
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"📁 Session exported: {export_path}")
            
        except Exception as e:
            print(f"❌ Failed to export session: {e}")
    
    async def cleanup(self):
        """Nettoyage final du gestionnaire"""
        # Sauvegarder toutes les sessions actives
        for session_data in self.active_sessions.values():
            await self._save_session(session_data)
        
        print("🧹 Session Manager cleanup completed")