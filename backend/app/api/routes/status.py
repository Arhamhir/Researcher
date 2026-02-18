from fastapi import APIRouter

router = APIRouter()

@router.get("/status/{job_id}")
def check_status(job_id: str):
    return {
        "job_id": job_id,
        "status": "uploaded"
    }
