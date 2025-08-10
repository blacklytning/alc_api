from typing import Any, Dict, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, ValidationError

router = APIRouter(prefix="/api", tags=["admissions"])


# Model for learner credentials
class LearnerCredentials(BaseModel):
    learner_code: str
    era_id: str
    era_password: str


# Endpoint to update learner credentials
@router.put("/admission/{admission_id}/credentials")
def update_learner_credentials(admission_id: int, creds: LearnerCredentials):
    success = AdmissionRepository.update_credentials(
        admission_id, creds.learner_code, creds.era_id, creds.era_password
    )
    if not success:
        raise HTTPException(
            status_code=404, detail="Admission not found or update failed"
        )
    return {"status": "success"}


from database.admission_repository import AdmissionRepository
from file_handler import FileHandler
from models import StudentAdmission


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
        # Validate admission data using Pydantic model
        admission_model = StudentAdmission(
            firstName=firstName,
            middleName=middleName,
            lastName=lastName,
            dateOfBirth=dateOfBirth,
            gender=gender,
            maritalStatus=maritalStatus,
            motherTongue=motherTongue,
            aadharNumber=aadharNumber,
            correspondenceAddress=correspondenceAddress,
            city=city,
            state=state,
            district=district,
            mobileNumber=mobileNumber,
            alternateMobileNumber=alternateMobileNumber,
            category=category,
            educationalQualification=educationalQualification,
            courseName=courseName,
            timing=timing,
            certificateName=certificateName,
            referredBy=referredBy,
        )

        # Save uploaded files
        photo_filename, signature_filename = FileHandler.save_admission_files(
            admission_model.mobileNumber, photo, signature
        )

        # Prepare admission data
        admission_data = {
            "firstName": admission_model.firstName,
            "middleName": admission_model.middleName,
            "lastName": admission_model.lastName,
            "dateOfBirth": admission_model.dateOfBirth,
            "gender": admission_model.gender,
            "maritalStatus": admission_model.maritalStatus,
            "motherTongue": admission_model.motherTongue,
            "aadharNumber": admission_model.aadharNumber,
            "correspondenceAddress": admission_model.correspondenceAddress,
            "city": admission_model.city,
            "state": admission_model.state,
            "district": admission_model.district,
            "mobileNumber": admission_model.mobileNumber,
            "alternateMobileNumber": admission_model.alternateMobileNumber,
            "category": admission_model.category,
            "educationalQualification": admission_model.educationalQualification,
            "courseName": admission_model.courseName,
            "timing": admission_model.timing,
            "certificateName": admission_model.certificateName,
            "referredBy": admission_model.referredBy,
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

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating admission: {str(e)}"
        )


@router.put("/admission/{admission_id}")
async def update_admission(
    admission_id: int,
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
    photo: Optional[UploadFile] = File(None),
    signature: Optional[UploadFile] = File(None),
) -> Dict[str, Any]:
    """Update an existing admission with optional file uploads"""
    try:
        # Get existing admission to check if it exists and get current file names
        existing_admission = AdmissionRepository.get_by_id(admission_id)
        if not existing_admission:
            raise HTTPException(status_code=404, detail="Admission not found")

        # Validate admission data using Pydantic model
        admission_model = StudentAdmission(
            firstName=firstName,
            middleName=middleName,
            lastName=lastName,
            dateOfBirth=dateOfBirth,
            gender=gender,
            maritalStatus=maritalStatus,
            motherTongue=motherTongue,
            aadharNumber=aadharNumber,
            correspondenceAddress=correspondenceAddress,
            city=city,
            state=state,
            district=district,
            mobileNumber=mobileNumber,
            alternateMobileNumber=alternateMobileNumber,
            category=category,
            educationalQualification=educationalQualification,
            courseName=courseName,
            timing=timing,
            certificateName=certificateName,
            referredBy=referredBy,
        )

        # Handle file updates
        photo_filename = None
        signature_filename = None

        if photo or signature:
            photo_filename, signature_filename = FileHandler.update_admission_files(
                mobile_number=admission_model.mobileNumber,
                photo=photo,
                signature=signature,
                old_photo_filename=existing_admission.get("photoFilename"),
                old_signature_filename=existing_admission.get("signatureFilename"),
            )

        # Prepare admission data for update
        admission_data = {
            "firstName": admission_model.firstName,
            "middleName": admission_model.middleName,
            "lastName": admission_model.lastName,
            "dateOfBirth": admission_model.dateOfBirth,
            "gender": admission_model.gender,
            "maritalStatus": admission_model.maritalStatus,
            "motherTongue": admission_model.motherTongue,
            "aadharNumber": admission_model.aadharNumber,
            "correspondenceAddress": admission_model.correspondenceAddress,
            "city": admission_model.city,
            "state": admission_model.state,
            "district": admission_model.district,
            "mobileNumber": admission_model.mobileNumber,
            "alternateMobileNumber": admission_model.alternateMobileNumber,
            "category": admission_model.category,
            "educationalQualification": admission_model.educationalQualification,
            "courseName": admission_model.courseName,
            "timing": admission_model.timing,
            "certificateName": admission_model.certificateName,
            "referredBy": admission_model.referredBy,
        }

        # Add file names if updated
        if photo_filename:
            admission_data["photoFilename"] = photo_filename
        if signature_filename:
            admission_data["signatureFilename"] = signature_filename

        # Update in database
        success = AdmissionRepository.update(admission_id, admission_data)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to update admission")

        return {
            "message": "Admission updated successfully",
            "admission_id": admission_id,
            "status": "success",
            "photo_filename": photo_filename,
            "signature_filename": signature_filename,
        }

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating admission: {str(e)}"
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
