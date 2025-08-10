from typing import Optional

from pydantic import BaseModel, Field, validator
from validation import validate_mobile_number, validate_aadhar_number, format_mobile_number, format_aadhar_number

class User(BaseModel):
    id: int
    username: str
    role: str  # 'staff' or 'admin'


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

    @validator('mobileNumber')
    def validate_mobile_number(cls, v):
        is_valid, error_message = validate_mobile_number(v)
        if not is_valid:
            raise ValueError(error_message)
        return format_mobile_number(v)

    @validator('alternateMobileNumber')
    def validate_alternate_mobile_number(cls, v):
        if not v:  # Allow empty string
            return v
        is_valid, error_message = validate_mobile_number(v)
        if not is_valid:
            raise ValueError(error_message)
        return format_mobile_number(v)

    @validator('aadharNumber')
    def validate_aadhar_number(cls, v):
        is_valid, error_message = validate_aadhar_number(v)
        if not is_valid:
            raise ValueError(error_message)
        return format_aadhar_number(v)


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

    @validator('mobileNumber')
    def validate_mobile_number(cls, v):
        is_valid, error_message = validate_mobile_number(v)
        if not is_valid:
            raise ValueError(error_message)
        return format_mobile_number(v)

    @validator('alternateMobileNumber')
    def validate_alternate_mobile_number(cls, v):
        if not v:  # Allow empty string
            return v
        is_valid, error_message = validate_mobile_number(v)
        if not is_valid:
            raise ValueError(error_message)
        return format_mobile_number(v)

    @validator('aadharNumber')
    def validate_aadhar_number(cls, v):
        is_valid, error_message = validate_aadhar_number(v)
        if not is_valid:
            raise ValueError(error_message)
        return format_aadhar_number(v)


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


class Denomination(BaseModel):
    value: int
    count: int
    serials: list[str] = []

class PaymentCreate(BaseModel):
    student_id: int = Field(..., description="ID of the student")
    amount: float = Field(..., description="Payment amount")
    payment_date: str = Field(..., description="Payment date (YYYY-MM-DD)")
    payment_method: str = Field(..., description="Payment method (CASH, CARD, UPI, BANK_TRANSFER, CHEQUE)")
    transaction_id: Optional[str] = Field(None, description="Transaction ID for non-cash payments")
    notes: Optional[str] = Field(None, description="Payment notes")
    late_fee: Optional[float] = Field(0, description="Late fee amount")
    discount: Optional[float] = Field(0, description="Discount amount")
    handled_by: Optional[str] = Field("System User", description="Staff member who handled the payment")
    denominations: list[Denomination] = Field(default_factory=list, description="List of denomination objects")
    cheque_number: Optional[str] = Field(None, description="Cheque number for cheque payments")
    bank_name: Optional[str] = Field(None, description="Bank name for cheque payments")


class DocumentUpload(BaseModel):
    student_id: int = Field(..., description="ID of the student")
    document_type: str = Field(..., description="Type of document (SIGNED_ADMISSION_FORM, IDENTITY_PROOF, ADDRESS_PROOF, EDUCATIONAL_CERTIFICATE, OTHER)")
    notes: Optional[str] = Field("", description="Document notes")


class DocumentResponse(BaseModel):
    id: int
    student_id: int
    document_type: str
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    status: str
    notes: str
    created_at: str
    updated_at: Optional[str]
    student_name: Optional[str] = None


class DocumentStatusUpdate(BaseModel):
    status: str = Field(..., description="Document status (UPLOADED, PENDING, REJECTED)")
    notes: Optional[str] = Field("", description="Status update notes")


class DocumentStats(BaseModel):
    total_documents: int
    documents_by_status: dict
    documents_by_type: list
    total_size: int
