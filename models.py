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
    certificateName: str
    referredBy: Optional[str] = ""
    joinedWhatsApp: bool = False
    admissionDate: str
    dateOfBirth: str
    aadharNumber: str
    correspondenceAddress: str
    city: str
    state: str
    district: str
    mobileNumber: str
    alternateMobileNumber: Optional[str] = ""
    educationalQualification: str
    courseName: str


class Course(BaseModel):
    courseName: str = Field(..., min_length=1, max_length=255)
    fees: int = Field(..., gt=0, description="Course fees must be greater than 0")


class CourseUpdate(BaseModel):
    courseName: Optional[str] = Field(None, min_length=1, max_length=255)
    fees: Optional[int] = Field(None, gt=0, description="Course fees must be greater than 0")


class CourseResponse(BaseModel):
    id: int
    courseName: str
    fees: int
    createdAt: str
    updatedAt: Optional[str] = None
