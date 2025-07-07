#!/usr/bin/env python3
"""
📊 Real-Time Statistics Manager
Tracks scanning progress, hits, and performance metrics in real-time
Author: wKayaa | 2025
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class ScanSession:
    """Individual scan session tracking"""
    session_id: str
    operator_name: str
    crack_id: str
    start_time: datetime
    targets: List[str] = field(default_factory=list)
    timeout: int = 17
    threads: int = 100000
    status: str = "running"
    
    # Progress tracking
    hits: int = 0
    checked_paths: int = 0
    checked_urls: int = 0
    invalid_urls: int = 0
    total_urls: int = 0
    target_total: int = 42925357
    
    # Performance metrics
    urls_per_second: float = 0.0
    last_update: datetime = field(default_factory=datetime.utcnow)
    errors: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'session_id': self.session_id,
            'operator_name': self.operator_name,
            'crack_id': self.crack_id,
            'start_time': self.start_time.isoformat(),
            'targets_count': len(self.targets),
            'timeout': self.timeout,
            'threads': self.threads,
            'status': self.status,
            'hits': self.hits,
            'checked_paths': self.checked_paths,
            'checked_urls': self.checked_urls,
            'invalid_urls': self.invalid_urls,
            'total_urls': self.total_urls,
            'target_total': self.target_total,
            'urls_per_second': self.urls_per_second,
            'last_update': self.last_update.isoformat(),
            'errors': self.errors,
            'progression': self.get_progression(),
            'eta': self.get_eta(),
            'duration': self.get_duration()
        }
    
    def get_progression(self) -> float:
        """Calculate progression percentage"""
        if self.target_total == 0:
            return 0.0
        return (self.total_urls / self.target_total) * 100
    
    def get_eta(self) -> str:
        """Calculate estimated time to completion"""
        if self.urls_per_second <= 0:
            return "∞"
        
        remaining_urls = self.target_total - self.total_urls
        if remaining_urls <= 0:
            return "00d 00h 00m 00s"
        
        eta_seconds = remaining_urls / self.urls_per_second
        
        days = int(eta_seconds // 86400)
        hours = int((eta_seconds % 86400) // 3600)
        minutes = int((eta_seconds % 3600) // 60)
        seconds = int(eta_seconds % 60)
        
        return f"{days:02d}d {hours:02d}h {minutes:02d}m {seconds:02d}s"
    
    def get_duration(self) -> str:
        """Get session duration"""
        delta = datetime.utcnow() - self.start_time
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days:02d}d {hours:02d}h {minutes:02d}m {seconds:02d}s"

class RealTimeStatsManager:
    """Real-time statistics manager for credential hunting operations"""
    
    def __init__(self):
        self.sessions: Dict[str, ScanSession] = {}
        self.global_stats = {
            'total_sessions': 0,
            'total_hits': 0,
            'total_targets_processed': 0,
            'total_errors': 0,
            'active_sessions': 0,
            'start_time': datetime.utcnow()
        }
        
        # Performance tracking
        self.performance_history = []
        self.update_interval = 5  # seconds
        self.last_stats_update = time.time()
        
    def create_session(self, session_id: str, operator_name: str, crack_id: str, 
                      targets: List[str], timeout: int = 17, threads: int = 100000) -> ScanSession:
        """Create a new scan session"""
        session = ScanSession(
            session_id=session_id,
            operator_name=operator_name,
            crack_id=crack_id,
            start_time=datetime.utcnow(),
            targets=targets,
            timeout=timeout,
            threads=threads,
            target_total=len(targets) * 1000  # Estimate URLs per target
        )
        
        self.sessions[session_id] = session
        self.global_stats['total_sessions'] += 1
        self.global_stats['active_sessions'] += 1
        
        logger.info(f"📊 Created scan session {session_id} for {operator_name}")
        return session
    
    def update_session_progress(self, session_id: str, **kwargs):
        """Update session progress"""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found")
            return
        
        session = self.sessions[session_id]
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        # Update last update time
        session.last_update = datetime.utcnow()
        
        # Calculate performance metrics
        self._update_performance_metrics(session)
        
        logger.debug(f"📊 Updated session {session_id} progress")
    
    def record_hit(self, session_id: str, credential_type: str, service: str):
        """Record a successful credential hit"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        session.hits += 1
        session.last_update = datetime.utcnow()
        
        self.global_stats['total_hits'] += 1
        
        logger.info(f"🎯 Hit recorded for session {session_id}: {service} {credential_type}")
    
    def record_url_check(self, session_id: str, url: str, valid: bool = True):
        """Record a URL check"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        session.checked_urls += 1
        session.total_urls += 1
        
        if not valid:
            session.invalid_urls += 1
        
        session.last_update = datetime.utcnow()
        
    def record_path_check(self, session_id: str, path: str):
        """Record a path check"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        session.checked_paths += 1
        session.last_update = datetime.utcnow()
    
    def record_error(self, session_id: str, error_type: str, error_message: str):
        """Record an error"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        session.errors += 1
        session.last_update = datetime.utcnow()
        
        self.global_stats['total_errors'] += 1
        
    def end_session(self, session_id: str):
        """End a scan session"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        session.status = "completed"
        session.last_update = datetime.utcnow()
        
        self.global_stats['active_sessions'] -= 1
        
        logger.info(f"📊 Session {session_id} completed")
    
    def pause_session(self, session_id: str):
        """Pause a scan session"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        session.status = "paused"
        session.last_update = datetime.utcnow()
        
    def resume_session(self, session_id: str):
        """Resume a scan session"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        session.status = "running"
        session.last_update = datetime.utcnow()
        
    def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific session"""
        if session_id not in self.sessions:
            return None
        
        return self.sessions[session_id].to_dict()
    
    def get_all_sessions_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all sessions"""
        return {
            session_id: session.to_dict() 
            for session_id, session in self.sessions.items()
        }
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global statistics"""
        return {
            **self.global_stats,
            'uptime': str(datetime.utcnow() - self.global_stats['start_time']),
            'sessions': list(self.sessions.keys())
        }
    
    def _update_performance_metrics(self, session: ScanSession):
        """Update performance metrics for a session"""
        current_time = time.time()
        
        # Calculate URLs per second
        if hasattr(session, '_last_url_count') and hasattr(session, '_last_time'):
            time_delta = current_time - session._last_time
            if time_delta > 0:
                url_delta = session.total_urls - session._last_url_count
                session.urls_per_second = url_delta / time_delta
        
        # Store for next calculation
        session._last_url_count = session.total_urls
        session._last_time = current_time
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary"""
        active_sessions = [s for s in self.sessions.values() if s.status == "running"]
        
        total_hits = sum(s.hits for s in self.sessions.values())
        total_urls = sum(s.total_urls for s in self.sessions.values())
        total_errors = sum(s.errors for s in self.sessions.values())
        
        avg_urls_per_second = 0
        if active_sessions:
            avg_urls_per_second = sum(s.urls_per_second for s in active_sessions) / len(active_sessions)
        
        return {
            'active_sessions': len(active_sessions),
            'total_sessions': len(self.sessions),
            'total_hits': total_hits,
            'total_urls_processed': total_urls,
            'total_errors': total_errors,
            'average_urls_per_second': avg_urls_per_second,
            'hit_rate': (total_hits / total_urls * 100) if total_urls > 0 else 0,
            'error_rate': (total_errors / total_urls * 100) if total_urls > 0 else 0,
            'uptime': str(datetime.utcnow() - self.global_stats['start_time'])
        }


# Global instance for shared use
stats_manager = RealTimeStatsManager()

# Export for use in other modules
__all__ = ['RealTimeStatsManager', 'ScanSession', 'stats_manager']