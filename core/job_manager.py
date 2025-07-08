#!/usr/bin/env python3
"""
WWYVQ v2.1 Job Manager
Manages job execution, tracking, and coordination

Author: wKayaa
Date: 2025-01-07
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


class JobStatus(Enum):
    """Job execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class JobResult:
    """Job execution result"""
    job_id: str
    status: JobStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    targets_processed: int = 0
    targets_successful: int = 0
    targets_failed: int = 0


@dataclass
class JobInfo:
    """Job information and metadata"""
    job_id: str
    name: str
    created_at: datetime
    started_at: Optional[datetime] = None
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0
    current_target: Optional[str] = None
    targets_total: int = 0
    targets_completed: int = 0
    estimated_completion: Optional[datetime] = None


class JobManager:
    """
    WWYVQ v2.1 Job Manager
    Handles job lifecycle, execution tracking, and coordination
    """
    
    def __init__(self, max_concurrent_jobs: int = 5):
        """Initialize job manager"""
        self.max_concurrent_jobs = max_concurrent_jobs
        self.logger = logging.getLogger("JobManager")
        
        # Job tracking
        self.jobs: Dict[str, JobInfo] = {}
        self.job_results: Dict[str, JobResult] = {}
        self.running_jobs: Dict[str, asyncio.Task] = {}
        
        # Job queue
        self.job_queue: asyncio.Queue = asyncio.Queue()
        
        # Statistics
        self.total_jobs_created = 0
        self.total_jobs_completed = 0
        self.total_jobs_failed = 0
        
        # Callbacks
        self.job_callbacks: Dict[str, List[Callable]] = {}
    
    async def initialize(self) -> None:
        """Initialize job manager"""
        try:
            self.logger.info("🔧 Initializing Job Manager...")
            
            # Start job processor
            asyncio.create_task(self._process_job_queue())
            
            self.logger.info("✅ Job Manager initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize job manager: {e}")
            raise
    
    async def create_job(self, job_config: Any) -> str:
        """Create a new job"""
        try:
            job_id = job_config.job_id
            
            # Create job info
            job_info = JobInfo(
                job_id=job_id,
                name=job_config.name,
                created_at=datetime.utcnow(),
                targets_total=len(job_config.targets)
            )
            
            # Store job
            self.jobs[job_id] = job_info
            self.total_jobs_created += 1
            
            # Add to queue
            await self.job_queue.put(job_config)
            
            self.logger.info(f"📋 Created job: {job_id} - {job_config.name}")
            return job_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create job: {e}")
            raise
    
    async def start_job(self, job_id: str) -> bool:
        """Start a specific job"""
        try:
            if job_id not in self.jobs:
                self.logger.error(f"❌ Job {job_id} not found")
                return False
            
            job_info = self.jobs[job_id]
            
            if job_info.status != JobStatus.PENDING:
                self.logger.error(f"❌ Job {job_id} is not pending (status: {job_info.status})")
                return False
            
            # Update job status
            job_info.status = JobStatus.RUNNING
            job_info.started_at = datetime.utcnow()
            
            self.logger.info(f"🚀 Started job: {job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start job {job_id}: {e}")
            return False
    
    async def stop_job(self, job_id: str) -> bool:
        """Stop a running job"""
        try:
            if job_id not in self.jobs:
                self.logger.error(f"❌ Job {job_id} not found")
                return False
            
            job_info = self.jobs[job_id]
            
            if job_info.status != JobStatus.RUNNING:
                self.logger.error(f"❌ Job {job_id} is not running (status: {job_info.status})")
                return False
            
            # Cancel the job task if running
            if job_id in self.running_jobs:
                self.running_jobs[job_id].cancel()
                del self.running_jobs[job_id]
            
            # Update job status
            job_info.status = JobStatus.CANCELLED
            
            # Create result
            result = JobResult(
                job_id=job_id,
                status=JobStatus.CANCELLED,
                start_time=job_info.started_at or datetime.utcnow(),
                end_time=datetime.utcnow()
            )
            
            if result.start_time:
                result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            
            self.job_results[job_id] = result
            
            self.logger.info(f"🛑 Stopped job: {job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to stop job {job_id}: {e}")
            return False
    
    async def get_job_status(self, job_id: str) -> Optional[JobInfo]:
        """Get current status of a job"""
        return self.jobs.get(job_id)
    
    async def get_job_result(self, job_id: str) -> Optional[JobResult]:
        """Get result of a completed job"""
        return self.job_results.get(job_id)
    
    async def update_job_progress(self, job_id: str, progress: float, current_target: Optional[str] = None) -> None:
        """Update job progress"""
        try:
            if job_id not in self.jobs:
                return
            
            job_info = self.jobs[job_id]
            job_info.progress = min(100.0, max(0.0, progress))
            
            if current_target:
                job_info.current_target = current_target
            
            # Update targets completed
            job_info.targets_completed = int((job_info.progress / 100.0) * job_info.targets_total)
            
            # Estimate completion time
            if job_info.started_at and job_info.progress > 0:
                elapsed = datetime.utcnow() - job_info.started_at
                estimated_total = elapsed.total_seconds() * (100.0 / job_info.progress)
                job_info.estimated_completion = job_info.started_at + timedelta(seconds=estimated_total)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update job progress for {job_id}: {e}")
    
    async def complete_job(self, job_id: str, results: Dict[str, Any], errors: List[str] = None) -> None:
        """Mark job as completed"""
        try:
            if job_id not in self.jobs:
                self.logger.error(f"❌ Job {job_id} not found")
                return
            
            job_info = self.jobs[job_id]
            job_info.status = JobStatus.COMPLETED
            job_info.progress = 100.0
            
            # Create result
            result = JobResult(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                start_time=job_info.started_at or datetime.utcnow(),
                end_time=datetime.utcnow(),
                results=results,
                errors=errors or []
            )
            
            if result.start_time:
                result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            
            self.job_results[job_id] = result
            self.total_jobs_completed += 1
            
            # Remove from running jobs
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]
            
            # Execute callbacks
            await self._execute_job_callbacks(job_id, "completed", result)
            
            self.logger.info(f"✅ Job {job_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to complete job {job_id}: {e}")
    
    async def fail_job(self, job_id: str, error: str) -> None:
        """Mark job as failed"""
        try:
            if job_id not in self.jobs:
                self.logger.error(f"❌ Job {job_id} not found")
                return
            
            job_info = self.jobs[job_id]
            job_info.status = JobStatus.FAILED
            
            # Create result
            result = JobResult(
                job_id=job_id,
                status=JobStatus.FAILED,
                start_time=job_info.started_at or datetime.utcnow(),
                end_time=datetime.utcnow(),
                errors=[error]
            )
            
            if result.start_time:
                result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            
            self.job_results[job_id] = result
            self.total_jobs_failed += 1
            
            # Remove from running jobs
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]
            
            # Execute callbacks
            await self._execute_job_callbacks(job_id, "failed", result)
            
            self.logger.error(f"❌ Job {job_id} failed: {error}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to fail job {job_id}: {e}")
    
    async def add_job_callback(self, job_id: str, callback: Callable) -> None:
        """Add callback for job events"""
        if job_id not in self.job_callbacks:
            self.job_callbacks[job_id] = []
        
        self.job_callbacks[job_id].append(callback)
    
    async def _execute_job_callbacks(self, job_id: str, event: str, result: JobResult) -> None:
        """Execute job callbacks"""
        try:
            if job_id not in self.job_callbacks:
                return
            
            for callback in self.job_callbacks[job_id]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(job_id, event, result)
                    else:
                        callback(job_id, event, result)
                except Exception as e:
                    self.logger.error(f"❌ Job callback failed: {e}")
                    
        except Exception as e:
            self.logger.error(f"❌ Failed to execute job callbacks: {e}")
    
    async def _process_job_queue(self) -> None:
        """Process job queue"""
        try:
            while True:
                # Wait for job
                job_config = await self.job_queue.get()
                
                # Check if we can start more jobs
                if len(self.running_jobs) >= self.max_concurrent_jobs:
                    # Wait for a slot to become available
                    await asyncio.sleep(1)
                    await self.job_queue.put(job_config)  # Put back in queue
                    continue
                
                # Start job
                job_id = job_config.job_id
                await self.start_job(job_id)
                
                # Create job task
                task = asyncio.create_task(self._execute_job(job_config))
                self.running_jobs[job_id] = task
                
                # Mark task as done
                self.job_queue.task_done()
                
        except asyncio.CancelledError:
            self.logger.info("Job queue processor cancelled")
        except Exception as e:
            self.logger.error(f"❌ Job queue processor failed: {e}")
    
    async def _execute_job(self, job_config: Any) -> None:
        """Execute a job (placeholder - will be implemented by core engine)"""
        try:
            job_id = job_config.job_id
            
            # Simulate job execution
            await asyncio.sleep(1)
            
            # Complete job
            await self.complete_job(job_id, {"status": "executed"}, [])
            
        except Exception as e:
            await self.fail_job(job_config.job_id, str(e))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get job manager statistics"""
        return {
            'total_jobs_created': self.total_jobs_created,
            'total_jobs_completed': self.total_jobs_completed,
            'total_jobs_failed': self.total_jobs_failed,
            'running_jobs': len(self.running_jobs),
            'pending_jobs': self.job_queue.qsize(),
            'max_concurrent_jobs': self.max_concurrent_jobs
        }
    
    def get_all_jobs(self) -> List[JobInfo]:
        """Get information about all jobs"""
        return list(self.jobs.values())
    
    def get_running_jobs(self) -> List[JobInfo]:
        """Get information about running jobs"""
        return [job for job in self.jobs.values() if job.status == JobStatus.RUNNING]
    
    async def cleanup_old_jobs(self, max_age_hours: int = 24) -> int:
        """Clean up old completed jobs"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            jobs_to_remove = []
            
            for job_id, job_info in self.jobs.items():
                if job_info.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                    if job_info.created_at < cutoff_time:
                        jobs_to_remove.append(job_id)
            
            # Remove old jobs
            for job_id in jobs_to_remove:
                del self.jobs[job_id]
                if job_id in self.job_results:
                    del self.job_results[job_id]
                if job_id in self.job_callbacks:
                    del self.job_callbacks[job_id]
            
            self.logger.info(f"🧹 Cleaned up {len(jobs_to_remove)} old jobs")
            return len(jobs_to_remove)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to cleanup old jobs: {e}")
            return 0