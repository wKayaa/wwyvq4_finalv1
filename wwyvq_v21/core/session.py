#!/usr/bin/env python3
"""
📝 WWYVQ Framework v2.1 - Session Manager
Ultra-Organized Architecture - Advanced Session Management

Features:
- Persistent session storage
- Session recovery and restoration
- Session-based tracking
- Automatic cleanup
- Session metadata management
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class SessionStatus(Enum):
    """Session status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


@dataclass
class SessionMetadata:
    """Session metadata"""
    session_id: str
    created_at: datetime
    updated_at: datetime
    status: SessionStatus
    operation_type: str
    targets_count: int
    results_count: int
    errors_count: int
    config_snapshot: Dict[str, Any]
    custom_data: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status.value,
            'operation_type': self.operation_type,
            'targets_count': self.targets_count,
            'results_count': self.results_count,
            'errors_count': self.errors_count,
            'config_snapshot': self.config_snapshot,
            'custom_data': self.custom_data or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionMetadata':
        """Create from dictionary"""
        return cls(
            session_id=data['session_id'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            status=SessionStatus(data['status']),
            operation_type=data['operation_type'],
            targets_count=data['targets_count'],
            results_count=data['results_count'],
            errors_count=data['errors_count'],
            config_snapshot=data['config_snapshot'],
            custom_data=data.get('custom_data', {})
        )


class SessionManager:
    """
    Advanced session management for WWYVQ v2.1
    
    Features:
    - Persistent session storage
    - Session recovery and restoration
    - Session-based tracking
    - Automatic cleanup
    - Session metadata management
    """
    
    def __init__(self, config_manager):
        """
        Initialize session manager
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager
        self.config = config_manager.get_config()
        
        # Session storage
        self.sessions_dir = Path("./sessions")
        self.sessions_dir.mkdir(exist_ok=True)
        
        # Active sessions
        self.active_sessions: Dict[str, SessionMetadata] = {}
        
        # Current session
        self.current_session: Optional[SessionMetadata] = None
        
        print("✅ Session Manager v2.1 initialized")
    
    async def initialize(self):
        """Initialize session manager"""
        # Load existing sessions
        await self._load_existing_sessions()
        
        # Clean up old sessions
        await self._cleanup_old_sessions()
        
        print("✅ Session Manager initialized")
    
    async def _load_existing_sessions(self):
        """Load existing sessions from disk"""
        try:
            for session_file in self.sessions_dir.glob("*.json"):
                try:
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                    
                    metadata = SessionMetadata.from_dict(session_data.get('metadata', {}))
                    self.active_sessions[metadata.session_id] = metadata
                    
                except Exception as e:
                    print(f"⚠️ Failed to load session {session_file}: {e}")
            
            print(f"✅ Loaded {len(self.active_sessions)} existing sessions")
            
        except Exception as e:
            print(f"❌ Failed to load existing sessions: {e}")
    
    async def _cleanup_old_sessions(self):
        """Clean up old sessions"""
        try:
            # Clean up sessions older than 7 days
            cutoff_time = datetime.utcnow().timestamp() - (7 * 24 * 3600)
            
            sessions_to_remove = []
            for session_id, metadata in self.active_sessions.items():
                if metadata.updated_at.timestamp() < cutoff_time:
                    sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                await self._remove_session(session_id)
            
            if sessions_to_remove:
                print(f"🧹 Cleaned up {len(sessions_to_remove)} old sessions")
                
        except Exception as e:
            print(f"❌ Failed to cleanup old sessions: {e}")
    
    async def create_session(self, operation_type: str = "general", 
                           custom_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new session
        
        Args:
            operation_type: Type of operation
            custom_data: Custom data to store
            
        Returns:
            str: Session ID
        """
        try:
            # Generate session ID
            session_id = str(uuid.uuid4())[:8]
            
            # Create session metadata
            metadata = SessionMetadata(
                session_id=session_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                status=SessionStatus.ACTIVE,
                operation_type=operation_type,
                targets_count=0,
                results_count=0,
                errors_count=0,
                config_snapshot=self._get_config_snapshot(),
                custom_data=custom_data or {}
            )
            
            # Store session
            self.active_sessions[session_id] = metadata
            self.current_session = metadata
            
            # Save to disk
            await self._save_session(session_id)
            
            print(f"✅ Session created: {session_id}")
            return session_id
            
        except Exception as e:
            print(f"❌ Failed to create session: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[SessionMetadata]:
        """Get session metadata"""
        return self.active_sessions.get(session_id)
    
    async def update_session(self, session_id: str, **updates):
        """Update session metadata"""
        if session_id not in self.active_sessions:
            return False
        
        metadata = self.active_sessions[session_id]
        
        # Update fields
        for key, value in updates.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)
        
        # Update timestamp
        metadata.updated_at = datetime.utcnow()
        
        # Save to disk
        await self._save_session(session_id)
        
        return True
    
    async def complete_session(self, session_id: str):
        """Mark session as completed"""
        await self.update_session(session_id, status=SessionStatus.COMPLETED)
    
    async def fail_session(self, session_id: str):
        """Mark session as failed"""
        await self.update_session(session_id, status=SessionStatus.FAILED)
    
    async def cancel_session(self, session_id: str):
        """Cancel session"""
        await self.update_session(session_id, status=SessionStatus.CANCELLED)
    
    async def suspend_session(self, session_id: str):
        """Suspend session"""
        await self.update_session(session_id, status=SessionStatus.SUSPENDED)
    
    async def resume_session(self, session_id: str):
        """Resume session"""
        await self.update_session(session_id, status=SessionStatus.ACTIVE)
    
    async def _save_session(self, session_id: str):
        """Save session to disk"""
        if session_id not in self.active_sessions:
            return
        
        try:
            metadata = self.active_sessions[session_id]
            session_file = self.sessions_dir / f"{session_id}.json"
            
            session_data = {
                'metadata': metadata.to_dict(),
                'results': [],  # Results stored separately
                'logs': []     # Logs stored separately
            }
            
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
        except Exception as e:
            print(f"❌ Failed to save session {session_id}: {e}")
    
    async def _remove_session(self, session_id: str):
        """Remove session"""
        try:
            # Remove from memory
            self.active_sessions.pop(session_id, None)
            
            # Remove from disk
            session_file = self.sessions_dir / f"{session_id}.json"
            if session_file.exists():
                session_file.unlink()
            
        except Exception as e:
            print(f"❌ Failed to remove session {session_id}: {e}")
    
    def _get_config_snapshot(self) -> Dict[str, Any]:
        """Get configuration snapshot"""
        config = self.config_manager.get_config()
        return {
            'core': asdict(config.core),
            'targets': asdict(config.targets),
            'exploit': asdict(config.exploit),
            'scrape': asdict(config.scrape),
            'validator': asdict(config.validator),
            'notifier': asdict(config.notifier),
            'exporter': asdict(config.exporter),
            'interface': asdict(config.interface),
            'logging': asdict(config.logging)
        }
    
    async def list_sessions(self, status: Optional[SessionStatus] = None) -> List[SessionMetadata]:
        """List sessions"""
        sessions = list(self.active_sessions.values())
        
        if status:
            sessions = [s for s in sessions if s.status == status]
        
        # Sort by updated time
        sessions.sort(key=lambda x: x.updated_at, reverse=True)
        
        return sessions
    
    async def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics"""
        stats = {
            'total_sessions': len(self.active_sessions),
            'by_status': {},
            'by_operation_type': {},
            'total_targets': 0,
            'total_results': 0,
            'total_errors': 0
        }
        
        for metadata in self.active_sessions.values():
            # By status
            status = metadata.status.value
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            # By operation type
            op_type = metadata.operation_type
            stats['by_operation_type'][op_type] = stats['by_operation_type'].get(op_type, 0) + 1
            
            # Totals
            stats['total_targets'] += metadata.targets_count
            stats['total_results'] += metadata.results_count
            stats['total_errors'] += metadata.errors_count
        
        return stats
    
    async def export_session(self, session_id: str, format: str = 'json') -> str:
        """Export session data"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        try:
            metadata = self.active_sessions[session_id]
            
            # Load full session data
            session_file = self.sessions_dir / f"{session_id}.json"
            if session_file.exists():
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
            else:
                session_data = {'metadata': metadata.to_dict()}
            
            # Export
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_file = f"session_{session_id}_{timestamp}.{format}"
            
            if format.lower() == 'json':
                with open(export_file, 'w') as f:
                    json.dump(session_data, f, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            return export_file
            
        except Exception as e:
            print(f"❌ Failed to export session {session_id}: {e}")
            raise
    
    def get_current_session(self) -> Optional[SessionMetadata]:
        """Get current session"""
        return self.current_session
    
    def set_current_session(self, session_id: str) -> bool:
        """Set current session"""
        if session_id in self.active_sessions:
            self.current_session = self.active_sessions[session_id]
            return True
        return False
    
    async def close_session(self, session_id: str):
        """Close session"""
        if session_id in self.active_sessions:
            metadata = self.active_sessions[session_id]
            
            # Update status if still active
            if metadata.status == SessionStatus.ACTIVE:
                metadata.status = SessionStatus.COMPLETED
                metadata.updated_at = datetime.utcnow()
                await self._save_session(session_id)
            
            # Clear current session if this was it
            if self.current_session and self.current_session.session_id == session_id:
                self.current_session = None
            
            print(f"✅ Session closed: {session_id}")
    
    async def shutdown(self):
        """Shutdown session manager"""
        print("🛑 Shutting down session manager...")
        
        # Close all active sessions
        for session_id in list(self.active_sessions.keys()):
            await self.close_session(session_id)
        
        print("✅ Session manager shutdown completed")