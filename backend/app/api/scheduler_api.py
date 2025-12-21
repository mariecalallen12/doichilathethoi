"""
Scheduler Management API
Endpoints for managing automated scheduled tasks
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel
from ..tasks.scheduler import (
    scheduler_manager,
    add_custom_job,
    remove_custom_job,
    list_scheduled_jobs,
    get_job_info
)
from ..dependencies import get_current_user
import logging

router = APIRouter(prefix="/scheduler", tags=["scheduler"])
logger = logging.getLogger(__name__)

class JobCreate(BaseModel):
    job_id: str
    trigger_type: str = "interval"  # "interval" or "cron"
    trigger_args: Dict[str, Any]
    description: str = None

class JobUpdate(BaseModel):
    trigger_type: str = None
    trigger_args: Dict[str, Any] = None

@router.get("/jobs")
async def get_all_jobs(current_user: dict = Depends(get_current_user)):
    """Get list of all scheduled jobs"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")
    
    return {
        "jobs": list_scheduled_jobs(),
        "total": len(scheduler_manager.jobs)
    }

@router.get("/jobs/{job_id}")
async def get_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get details of a specific job"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")
    
    job_info = get_job_info(job_id)
    if not job_info:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = job_info["job"]
    return {
        "id": job_id,
        "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
        "trigger_type": job_info["trigger_type"],
        "trigger_args": job_info["trigger_args"],
        "added_at": job_info["added_at"].isoformat()
    }

@router.post("/jobs")
async def create_job(
    job_data: JobCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new scheduled job"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")
    
    try:
        # For custom jobs, you need to provide the actual function
        # This is a simplified example - in production, you'd have a registry of allowed functions
        raise HTTPException(
            status_code=501,
            detail="Creating custom jobs via API not implemented. Use predefined jobs."
        )
    except Exception as e:
        logger.error(f"Failed to create job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a scheduled job"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")
    
    # Don't allow deletion of core system jobs
    protected_jobs = [
        "market_data_refresh",
        "system_health_check",
        "alert_check"
    ]
    
    if job_id in protected_jobs:
        raise HTTPException(
            status_code=403,
            detail=f"Cannot delete protected system job: {job_id}"
        )
    
    try:
        remove_custom_job(job_id)
        return {"status": "deleted", "job_id": job_id}
    except Exception as e:
        logger.error(f"Failed to delete job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/{job_id}/pause")
async def pause_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Pause a scheduled job"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")
    
    try:
        job_info = get_job_info(job_id)
        if not job_info:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job = job_info["job"]
        job.pause()
        
        logger.info(f"Job '{job_id}' paused by admin {current_user.get('email')}")
        return {"status": "paused", "job_id": job_id}
    except Exception as e:
        logger.error(f"Failed to pause job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/{job_id}/resume")
async def resume_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Resume a paused job"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")
    
    try:
        job_info = get_job_info(job_id)
        if not job_info:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job = job_info["job"]
        job.resume()
        
        logger.info(f"Job '{job_id}' resumed by admin {current_user.get('email')}")
        return {"status": "resumed", "job_id": job_id}
    except Exception as e:
        logger.error(f"Failed to resume job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/{job_id}/run")
async def trigger_job_now(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Manually trigger a job to run immediately"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")
    
    try:
        job_info = get_job_info(job_id)
        if not job_info:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job = job_info["job"]
        
        # Trigger job to run now
        scheduler_manager.scheduler.modify_job(
            job_id,
            next_run_time=None  # Run immediately
        )
        
        logger.info(f"Job '{job_id}' manually triggered by admin {current_user.get('email')}")
        return {"status": "triggered", "job_id": job_id}
    except Exception as e:
        logger.error(f"Failed to trigger job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_scheduler_status(current_user: dict = Depends(get_current_user)):
    """Get scheduler status"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin only")
    
    return {
        "running": scheduler_manager.is_running,
        "total_jobs": len(scheduler_manager.jobs),
        "job_list": list(scheduler_manager.jobs.keys())
    }
