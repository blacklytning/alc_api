from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from models import StudentEnquiry
from database import EnquiryRepository

router = APIRouter(prefix="/api", tags=["enquiries"])


@router.post("/enquiry")
def create_enquiry(enquiry: StudentEnquiry) -> Dict[str, Any]:
    """Create a new student enquiry"""
    try:
        enquiry_id = EnquiryRepository.create(enquiry)
        return {
            "message": "Enquiry submitted successfully",
            "enquiry_id": enquiry_id,
            "status": "success",
        }
    except Exception as e:
        # Return success message even on error (as per original code)
        return {
            "message": "Enquiry submitted successfully",
            "status": "success",
        }


@router.get("/enquiries")
def get_all_enquiries() -> Dict[str, Any]:
    """Get all enquiries (for admin purposes)"""
    try:
        enquiries = EnquiryRepository.get_all()
        return {"enquiries": enquiries, "total": len(enquiries)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/enquiry/{enquiry_id}")
def get_enquiry(enquiry_id: int) -> Dict[str, Any]:
    """Get a specific enquiry by ID"""
    try:
        enquiry = EnquiryRepository.get_by_id(enquiry_id)
        if not enquiry:
            raise HTTPException(status_code=404, detail="Enquiry not found")
        return enquiry
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
