from typing import Optional

from pydantic import BaseModel, Field


class StudentEnquiry(BaseModel):
    firstName: str
    middleName: Optional[str] = ""
    lastName: str
    dateOfBirth: str
    gender: str
    maritalStatus: str
    motherTongue: str
    aadharNumber: str
    correspondenceAddress: str
    city: str
    state: str
    district: str
    mobileNumber: str
    alternateMobileNumber: Optional[str] = ""
    category: str
    educationalQualification: str
    courseName: str
    timing: str
    handledBy: str


class StudentAdmission(BaseModel):
    firstName: str
    middleName: Optional[str] = ""
    lastName: str
    dateOfBirth: str
    gender: str
    maritalStatus: str
    motherTongue: str
    aadharNumber: str
    correspondenceAddress: str
    city: str
    state: str
    district: str
    mobileNumber: str
    alternateMobileNumber: Optional[str] = ""
    category: str
    educationalQualification: str
    courseName: str
    timing: str
    certificateName: str
    referredBy: Optional[str] = ""


class Course(BaseModel):
    courseName: str = Field(..., min_length=1, max_length=255)
    fees: int = Field(..., gt=0, description="Course fees must be greater than 0")


class CourseUpdate(BaseModel):
    courseName: Optional[str] = Field(None, min_length=1, max_length=255)
    fees: Optional[int] = Field(
        None, gt=0, description="Course fees must be greater than 0"
    )


class CourseResponse(BaseModel):
    id: int
    courseName: str
    fees: int
    createdAt: str
    updatedAt: Optional[str] = None


class FollowupCreate(BaseModel):
    enquiry_id: int = Field(..., description="ID of the related enquiry")
    followup_date: str = Field(
        ..., description="Date when follow-up was conducted (YYYY-MM-DD)"
    )
    status: str = Field(..., description="Current status after follow-up")
    notes: Optional[str] = Field("", description="Follow-up notes")
    next_followup_date: Optional[str] = Field(
        None, description="Next planned follow-up date (YYYY-MM-DD)"
    )
    handled_by: str = Field(..., description="Staff member who handled the follow-up")


class FollowupUpdate(BaseModel):
    followup_date: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    next_followup_date: Optional[str] = None
    handled_by: Optional[str] = None


class FollowupResponse(BaseModel):
    id: int
    enquiry_id: int
    followup_date: str
    status: str
    notes: str
    next_followup_date: Optional[str]
    handled_by: str
    created_at: str
    updated_at: Optional[str]


class EnquiryWithFollowups(BaseModel):
    id: int
    firstName: str
    middleName: Optional[str]
    lastName: str
    mobileNumber: str
    courseName: str
    enquiryDate: str
    currentStatus: str
    lastFollowup: Optional[str]
    nextFollowup: Optional[str]
    followupCount: int
    latestNotes: Optional[str]
    followups: list[FollowupResponse]


class InstituteSettings(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    address: Optional[str] = ""
    phone: Optional[str] = ""
    email: Optional[str] = ""
    website: Optional[str] = ""


class InstituteSettingsResponse(BaseModel):
    id: int
    name: str
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    logo: Optional[str]
    created_at: str
    updated_at: Optional[str]


class DatabaseStatsResponse(BaseModel):
    lastBackup: Optional[str]
    databaseSize: int
    totalRecords: int
    backupHistory: list
