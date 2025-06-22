from typing import Optional
from pydantic import BaseModel


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
