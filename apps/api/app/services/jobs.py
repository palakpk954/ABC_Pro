import uuid
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional, Callable, Any


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class JobInfo:
    def __init__(self, job_id: str, plan_id: Optional[str] = None):
        self.job_id = job_id
        self.plan_id = plan_id
        self.status = JobStatus.PENDING
        self.created_at = datetime.now(timezone.utc)
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None
        self.progress: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "plan_id": self.plan_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "progress": self.progress,
        }


class JobRunner(ABC):
    @abstractmethod
    def submit_job(self, target_func: Callable, plan_id: str, *args, **kwargs) -> str:
        pass

    @abstractmethod
    def get_job(self, job_id: str) -> Optional[JobInfo]:
        pass


class InMemoryBackgroundJobRunner(JobRunner):
    """Thread-safe background job runner implementing JobRunner interface.

    Allows seamless future substitution with Celery or Temporal.
    """
    def __init__(self):
        self._jobs: Dict[str, JobInfo] = {}
        self._lock = threading.Lock()

    def submit_job(self, target_func: Callable, plan_id: str, *args, **kwargs) -> str:
        job_id = str(uuid.uuid4())
        job = JobInfo(job_id=job_id, plan_id=plan_id)
        with self._lock:
            self._jobs[job_id] = job

        def worker():
            with self._lock:
                job.status = JobStatus.RUNNING
                job.progress = 0.1
            try:
                target_func(*args, **kwargs)
                with self._lock:
                    job.status = JobStatus.COMPLETED
                    job.progress = 1.0
                    job.completed_at = datetime.now(timezone.utc)
            except Exception as e:
                with self._lock:
                    job.status = JobStatus.FAILED
                    job.error = str(e)
                    job.completed_at = datetime.now(timezone.utc)

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        return job_id

    def get_job(self, job_id: str) -> Optional[JobInfo]:
        with self._lock:
            return self._jobs.get(job_id)


# Global job runner instance
job_runner = InMemoryBackgroundJobRunner()
