from fastapi import APIRouter, HTTPException
from app.services.vector_store import get_paper_review

router = APIRouter()

@router.get("/review/{paper_id}")
def get_review(paper_id: str):
    """
    Get the final review for a paper.
    Returns the complete review with all agent scores and final decision.
    """
    try:
        review = get_paper_review(paper_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        return review
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/review/{paper_id}/status")
def get_review_status(paper_id: str):
    """
    Poll endpoint to check if review is complete.
    Returns processing status and progress.
    """
    try:
        review = get_paper_review(paper_id)
        print(f"[STATUS] Paper {paper_id}, Review: {review}")
        
        if not review:
            # Paper uploaded but review not complete yet
            return {"status": "processing", "progress": 50}
        
        # Check if review has final decision with a decision field
        final_decision = review.get("final_decision")
        print(f"[STATUS] Final decision: {final_decision}")
        
        if final_decision and final_decision.get("decision"):
            return {
                "status": "complete",
                "progress": 100,
                "review": review
            }
        else:
            # Still processing
            return {
                "status": "processing",
                "progress": 75
            }
    except Exception as e:
        print(f"[STATUS] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review/{job_id}")
def start_review(job_id: str):
    return {
        "job_id": job_id,
        "status": "review started (not implemented)"
    }
