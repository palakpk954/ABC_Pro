from fastapi import APIRouter, HTTPException, Depends
from app.api.deps import get_current_user
from app.models import User
from app.services.jobs import job_runner

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/{job_id}")
def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
):
    job = job_runner.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.to_dict()
