from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from database.enquiry_repository import EnquiryRepository
from database.followup_repository import FollowupRepository
from models import FollowupCreate, FollowupUpdate

router = APIRouter(prefix="/api", tags=["followups"])


@router.post("/followup")
def create_followup(followup: FollowupCreate) -> Dict[str, Any]:
    """Create a new follow-up record"""
    try:
        # Verify that enquiry exists
        enquiry = EnquiryRepository.get_by_id(followup.enquiry_id)
        if not enquiry:
            raise HTTPException(status_code=404, detail="Enquiry not found")

        followup_data = {
            "enquiry_id": followup.enquiry_id,
            "followup_date": followup.followup_date,
            "status": followup.status,
            "notes": followup.notes or "",
            "next_followup_date": followup.next_followup_date,
            "handled_by": followup.handled_by,
        }

        followup_id = FollowupRepository.create(followup_data)

        return {
            "message": "Follow-up recorded successfully",
            "followup_id": followup_id,
            "status": "success",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/followups")
def get_all_followups() -> Dict[str, Any]:
    """Get all follow-up records"""
    try:
        followups = FollowupRepository.get_all()
        return {"followups": followups, "total": len(followups)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/followups/enquiry/{enquiry_id}")
def get_followups_by_enquiry(enquiry_id: int) -> Dict[str, Any]:
    """Get all follow-ups for a specific enquiry"""
    try:
        # Verify enquiry exists
        enquiry = EnquiryRepository.get_by_id(enquiry_id)
        if not enquiry:
            raise HTTPException(status_code=404, detail="Enquiry not found")

        followups = FollowupRepository.get_by_enquiry_id(enquiry_id)
        return {
            "enquiry": enquiry,
            "followups": followups,
            "total_followups": len(followups),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/followups/tracker")
def get_followup_tracker() -> Dict[str, Any]:
    """Get enquiries with follow-up summary for the tracker interface"""
    try:
        enquiries = FollowupRepository.get_enquiries_with_followup_summary()
        return {"enquiries": enquiries, "total": len(enquiries)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/followups/overdue")
def get_overdue_followups() -> Dict[str, Any]:
    """Get enquiries with overdue follow-ups"""
    try:
        overdue = FollowupRepository.get_overdue_followups()
        return {"overdue_followups": overdue, "total": len(overdue)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/followups/stats")
def get_followup_stats() -> Dict[str, Any]:
    """Get follow-up statistics"""
    try:
        stats = FollowupRepository.get_followup_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.put("/followup/{followup_id}")
def update_followup(
    followup_id: int, followup_update: FollowupUpdate
) -> Dict[str, Any]:
    """Update a follow-up record"""
    try:
        # Convert Pydantic model to dict, excluding None values
        update_data = {k: v for k, v in followup_update.dict().items() if v is not None}

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        success = FollowupRepository.update(followup_id, update_data)
        if not success:
            raise HTTPException(status_code=404, detail="Follow-up not found")

        return {"message": "Follow-up updated successfully", "status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.delete("/followup/{followup_id}")
def delete_followup(followup_id: int) -> Dict[str, Any]:
    """Delete a follow-up record"""
    try:
        success = FollowupRepository.delete(followup_id)
        if not success:
            raise HTTPException(status_code=404, detail="Follow-up not found")

        return {"message": "Follow-up deleted successfully", "status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
