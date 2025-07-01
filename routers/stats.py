from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from database.stats_repository import StatsRepository

router = APIRouter(prefix="/api", tags=["statistics"])


@router.get("/stats")
def get_stats() -> Dict[str, Any]:
    """Get basic statistics about enquiries and admissions"""
    try:
        return StatsRepository.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
