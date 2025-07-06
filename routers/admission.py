from typing import Any, Dict

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from database.admission_repository import AdmissionRepository
from file_handler import FileHandler

router = APIRouter(prefix="/api", tags=["admissions"])


@router.post("/admission")
async def create_admission(
    firstName: str = Form(...),
    middleName: str = Form(""),
    lastName: str = Form(...),
    dateOfBirth: str = Form(...),
    gender: str = Form(...),
    maritalStatus: str = Form(...),
    motherTongue: str = Form(...),
    aadharNumber: str = Form(...),
    correspondenceAddress: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    district: str = Form(...),
    mobileNumber: str = Form(...),
    alternateMobileNumber: str = Form(""),
    category: str = Form(...),
    educationalQualification: str = Form(...),
    courseName: str = Form(...),
    timing: str = Form(...),
    certificateName: str = Form(...),
    referredBy: str = Form(""),
    photo: UploadFile = File(...),
    signature: UploadFile = File(...),
) -> Dict[str, Any]:
    """Create a new admission with file uploads"""
    try:
        # Save uploaded files
        photo_filename, signature_filename = FileHandler.save_admission_files(
            mobileNumber, photo, signature
        )

        # Prepare admission data
        admission_data = {
            "firstName": firstName,
            "middleName": middleName,
            "lastName": lastName,
            "dateOfBirth": dateOfBirth,
            "gender": gender,
            "maritalStatus": maritalStatus,
            "motherTongue": motherTongue,
            "aadharNumber": aadharNumber,
            "correspondenceAddress": correspondenceAddress,
            "city": city,
            "state": state,
            "district": district,
            "mobileNumber": mobileNumber,
            "alternateMobileNumber": alternateMobileNumber,
            "category": category,
            "educationalQualification": educationalQualification,
            "courseName": courseName,
            "timing": timing,
            "certificateName": certificateName,
            "referredBy": referredBy,
            "photoFilename": photo_filename,
            "signatureFilename": signature_filename,
        }

        # Save to database
        admission_id = AdmissionRepository.create(admission_data)

        return {
            "message": "Admission completed successfully",
            "admission_id": admission_id,
            "status": "success",
            "photo_filename": photo_filename,
            "signature_filename": signature_filename,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating admission: {str(e)}"
        )


@router.get("/admissions")
def get_all_admissions() -> Dict[str, Any]:
    """Get all admissions (for admin purposes)"""
    try:
        admissions = AdmissionRepository.get_all()
        return {"admissions": admissions, "total": len(admissions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/admission/{admission_id}")
def get_admission(admission_id: int) -> Dict[str, Any]:
    """Get a specific admission by ID"""
    try:
        admission = AdmissionRepository.get_by_id(admission_id)
        if not admission:
            raise HTTPException(status_code=404, detail="Admission not found")
        return admission
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
