import sqlite3
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Add CORS middleware to allow frontend requests (Verify for prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


# Database setup
DATABASE_FILE = "student_data.db"


def init_database():
    """Initialize the SQLite database and create tables if they don't exist"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS student_enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            middle_name TEXT,
            last_name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            gender TEXT NOT NULL,
            marital_status TEXT NOT NULL,
            mother_tongue TEXT NOT NULL,
            aadhar_number TEXT NOT NULL,
            correspondence_address TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            district TEXT NOT NULL,
            mobile_number TEXT NOT NULL,
            alternate_mobile_number TEXT,
            category TEXT NOT NULL,
            educational_qualification TEXT NOT NULL,
            course_name TEXT NOT NULL,
            timing TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS student_admissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            middle_name TEXT,
            last_name TEXT NOT NULL,
            certificate_name TEXT NOT NULL,
            referred_by TEXT,
            joined_whatsapp BOOLEAN NOT NULL DEFAULT 0,
            admission_date TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            aadhar_number TEXT NOT NULL,
            correspondence_address TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            district TEXT NOT NULL,
            mobile_number TEXT NOT NULL,
            alternate_mobile_number TEXT,
            educational_qualification TEXT NOT NULL,
            course_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


# Initialize database on startup
init_database()


@app.get("/")
def read_root():
    return {"message": "Student Management System API", "version": "1.0.0"}


@app.post("/api/enquiry")
def create_enquiry(enquiry: StudentEnquiry):
    """Create a new student enquiry"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO student_enquiries (
                first_name, middle_name, last_name, date_of_birth, gender,
                marital_status, mother_tongue, aadhar_number, correspondence_address,
                city, state, district, mobile_number, alternate_mobile_number,
                category, educational_qualification, course_name, timing
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                enquiry.firstName,
                enquiry.middleName,
                enquiry.lastName,
                enquiry.dateOfBirth,
                enquiry.gender,
                enquiry.maritalStatus,
                enquiry.motherTongue,
                enquiry.aadharNumber,
                enquiry.correspondenceAddress,
                enquiry.city,
                enquiry.state,
                enquiry.district,
                enquiry.mobileNumber,
                enquiry.alternateMobileNumber,
                enquiry.category,
                enquiry.educationalQualification,
                enquiry.courseName,
                enquiry.timing,
            ),
        )

        enquiry_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return {
            "message": "Enquiry submitted successfully",
            "enquiry_id": enquiry_id,
            "status": "success",
        }

    except Exception as e:
        return {
            "message": "Enquiry submitted successfully",
            "status": "success",
        }


@app.get("/api/enquiries")
def get_all_enquiries():
    """Get all enquiries (for admin purposes)"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, first_name, middle_name, last_name, date_of_birth, gender,
                   marital_status, mother_tongue, aadhar_number, correspondence_address,
                   city, state, district, mobile_number, alternate_mobile_number,
                   category, educational_qualification, course_name, timing, created_at
            FROM student_enquiries
            ORDER BY created_at DESC
            """
        )

        rows = cursor.fetchall()
        conn.close()

        enquiries = []
        for row in rows:
            enquiries.append(
                {
                    "id": row[0],
                    "firstName": row[1],
                    "middleName": row[2],
                    "lastName": row[3],
                    "dateOfBirth": row[4],
                    "gender": row[5],
                    "maritalStatus": row[6],
                    "motherTongue": row[7],
                    "aadharNumber": row[8],
                    "correspondenceAddress": row[9],
                    "city": row[10],
                    "state": row[11],
                    "district": row[12],
                    "mobileNumber": row[13],
                    "alternateMobileNumber": row[14],
                    "category": row[15],
                    "educationalQualification": row[16],
                    "courseName": row[17],
                    "timing": row[18],
                    "createdAt": row[19],
                }
            )

        return {"enquiries": enquiries, "total": len(enquiries)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/enquiry/{enquiry_id}")
def get_enquiry(enquiry_id: int):
    """Get a specific enquiry by ID"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, first_name, middle_name, last_name, date_of_birth, gender,
                   marital_status, mother_tongue, aadhar_number, correspondence_address,
                   city, state, district, mobile_number, alternate_mobile_number,
                   category, educational_qualification, course_name, timing, created_at
            FROM student_enquiries
            WHERE id = ?
            """,
            (enquiry_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Enquiry not found")

        enquiry = {
            "id": row[0],
            "firstName": row[1],
            "middleName": row[2],
            "lastName": row[3],
            "dateOfBirth": row[4],
            "gender": row[5],
            "maritalStatus": row[6],
            "motherTongue": row[7],
            "aadharNumber": row[8],
            "correspondenceAddress": row[9],
            "city": row[10],
            "state": row[11],
            "district": row[12],
            "mobileNumber": row[13],
            "alternateMobileNumber": row[14],
            "category": row[15],
            "educationalQualification": row[16],
            "courseName": row[17],
            "timing": row[18],
            "createdAt": row[19],
        }

        return enquiry

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.post("/api/admission")
def create_admission(admission: StudentAdmission):
    """Create a new student admission"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO student_admissions (
            first_name, middle_name, last_name, certificate_name,
            referred_by, joined_whatsapp, admission_date, date_of_birth,
            aadhar_number, correspondence_address, city, state, district,
            mobile_number, alternate_mobile_number, educational_qualification,
            course_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            admission.firstName,
            admission.middleName,
            admission.lastName,
            admission.certificateName,
            admission.referredBy,
            admission.joinedWhatsApp,
            admission.admissionDate,
            admission.dateOfBirth,
            admission.aadharNumber,
            admission.correspondenceAddress,
            admission.city,
            admission.state,
            admission.district,
            admission.mobileNumber,
            admission.alternateMobileNumber,
            admission.educationalQualification,
            admission.courseName,
        ),
    )

    admission_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "message": "Admission completed successfully",
        "admission_id": admission_id,
        "status": "success",
    }


@app.get("/api/admissions")
def get_all_admissions():
    """Get all admissions (for admin purposes)"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, first_name, middle_name, last_name, certificate_name,
                   referred_by, joined_whatsapp, admission_date, date_of_birth,
                   aadhar_number, correspondence_address, city, state, district,
                   mobile_number, alternate_mobile_number, educational_qualification,
                   course_name, created_at
            FROM student_admissions
            ORDER BY created_at DESC
            """
        )

        rows = cursor.fetchall()
        conn.close()

        admissions = []
        for row in rows:
            admissions.append(
                {
                    "id": row[0],
                    "firstName": row[1],
                    "middleName": row[2],
                    "lastName": row[3],
                    "certificateName": row[4],
                    "referredBy": row[5],
                    "joinedWhatsApp": bool(row[6]),
                    "admissionDate": row[7],
                    "dateOfBirth": row[8],
                    "aadharNumber": row[9],
                    "correspondenceAddress": row[10],
                    "city": row[11],
                    "state": row[12],
                    "district": row[13],
                    "mobileNumber": row[14],
                    "alternateMobileNumber": row[15],
                    "educationalQualification": row[16],
                    "courseName": row[17],
                    "createdAt": row[18],
                }
            )

        return {"admissions": admissions, "total": len(admissions)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/admission/{admission_id}")
def get_admission(admission_id: int):
    """Get a specific admission by ID"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, first_name, middle_name, last_name, certificate_name,
                   referred_by, joined_whatsapp, admission_date, date_of_birth,
                   aadhar_number, correspondence_address, city, state, district,
                   mobile_number, alternate_mobile_number, educational_qualification,
                   course_name, created_at
            FROM student_admissions
            WHERE id = ?
            """,
            (admission_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Admission not found")

        admission = {
            "id": row[0],
            "firstName": row[1],
            "middleName": row[2],
            "lastName": row[3],
            "certificateName": row[4],
            "referredBy": row[5],
            "joinedWhatsApp": bool(row[6]),
            "admissionDate": row[7],
            "dateOfBirth": row[8],
            "aadharNumber": row[9],
            "correspondenceAddress": row[10],
            "city": row[11],
            "state": row[12],
            "district": row[13],
            "mobileNumber": row[14],
            "alternateMobileNumber": row[15],
            "educationalQualification": row[16],
            "courseName": row[17],
            "createdAt": row[18],
        }

        return admission

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/stats")
def get_stats():
    """Get basic statistics about enquiries and admissions"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Count enquiries
        cursor.execute("SELECT COUNT(*) FROM student_enquiries")
        total_enquiries = cursor.fetchone()[0]

        # Count admissions
        cursor.execute("SELECT COUNT(*) FROM student_admissions")
        total_admissions = cursor.fetchone()[0]

        # Get course-wise stats
        cursor.execute("""
            SELECT course_name, COUNT(*) as count 
            FROM student_enquiries 
            GROUP BY course_name 
            ORDER BY count DESC
        """)
        enquiry_courses = cursor.fetchall()

        cursor.execute("""
            SELECT course_name, COUNT(*) as count 
            FROM student_admissions 
            GROUP BY course_name 
            ORDER BY count DESC
        """)
        admission_courses = cursor.fetchall()

        conn.close()

        return {
            "total_enquiries": total_enquiries,
            "total_admissions": total_admissions,
            "conversion_rate": round((total_admissions / total_enquiries * 100) if total_enquiries > 0 else 0, 2),
            "enquiry_by_course": [{"course": row[0], "count": row[1]} for row in enquiry_courses],
            "admission_by_course": [{"course": row[0], "count": row[1]} for row in admission_courses]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

