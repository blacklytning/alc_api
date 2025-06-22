import sqlite3
from typing import List, Dict, Any, Optional
from models import StudentEnquiry, StudentAdmission

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
            photo_filename TEXT,
            signature_filename TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DATABASE_FILE)


class EnquiryRepository:
    @staticmethod
    def create(enquiry: StudentEnquiry) -> int:
        """Create a new enquiry and return its ID"""
        conn = get_db_connection()
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
        return enquiry_id

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all enquiries"""
        conn = get_db_connection()
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
            enquiries.append({
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
            })

        return enquiries

    @staticmethod
    def get_by_id(enquiry_id: int) -> Optional[Dict[str, Any]]:
        """Get enquiry by ID"""
        conn = get_db_connection()
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
            return None

        return {
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


class AdmissionRepository:
    @staticmethod
    def create(admission_data: Dict[str, Any]) -> int:
        """Create a new admission and return its ID"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO student_admissions (
                first_name, middle_name, last_name, certificate_name,
                referred_by, joined_whatsapp, admission_date, date_of_birth,
                aadhar_number, correspondence_address, city, state, district,
                mobile_number, alternate_mobile_number, educational_qualification,
                course_name, photo_filename, signature_filename
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                admission_data["firstName"],
                admission_data["middleName"],
                admission_data["lastName"],
                admission_data["certificateName"],
                admission_data["referredBy"],
                admission_data["joinedWhatsApp"],
                admission_data["admissionDate"],
                admission_data["dateOfBirth"],
                admission_data["aadharNumber"],
                admission_data["correspondenceAddress"],
                admission_data["city"],
                admission_data["state"],
                admission_data["district"],
                admission_data["mobileNumber"],
                admission_data["alternateMobileNumber"],
                admission_data["educationalQualification"],
                admission_data["courseName"],
                admission_data["photoFilename"],
                admission_data["signatureFilename"],
            ),
        )

        admission_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return admission_id

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all admissions"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, first_name, middle_name, last_name, certificate_name,
                   referred_by, joined_whatsapp, admission_date, date_of_birth,
                   aadhar_number, correspondence_address, city, state, district,
                   mobile_number, alternate_mobile_number, educational_qualification,
                   course_name, photo_filename, signature_filename, created_at
            FROM student_admissions
            ORDER BY created_at DESC
            """
        )

        rows = cursor.fetchall()
        conn.close()

        admissions = []
        for row in rows:
            admissions.append({
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
                "photoFilename": row[18],
                "signatureFilename": row[19],
                "createdAt": row[20],
            })

        return admissions

    @staticmethod
    def get_by_id(admission_id: int) -> Optional[Dict[str, Any]]:
        """Get admission by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, first_name, middle_name, last_name, certificate_name,
                   referred_by, joined_whatsapp, admission_date, date_of_birth,
                   aadhar_number, correspondence_address, city, state, district,
                   mobile_number, alternate_mobile_number, educational_qualification,
                   course_name, photo_filename, signature_filename, created_at
            FROM student_admissions
            WHERE id = ?
            """,
            (admission_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
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
            "photoFilename": row[18],
            "signatureFilename": row[19],
            "createdAt": row[20],
        }


class StatsRepository:
    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """Get basic statistics"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Count enquiries
        cursor.execute("SELECT COUNT(*) FROM student_enquiries")
        total_enquiries = cursor.fetchone()[0]

        # Count admissions
        cursor.execute("SELECT COUNT(*) FROM student_admissions")
        total_admissions = cursor.fetchone()[0]

        # Get course-wise stats
        cursor.execute(
            """
            SELECT course_name, COUNT(*) as count 
            FROM student_enquiries 
            GROUP BY course_name 
            ORDER BY count DESC
        """
        )
        enquiry_courses = cursor.fetchall()

        cursor.execute(
            """
            SELECT course_name, COUNT(*) as count 
            FROM student_admissions 
            GROUP BY course_name 
            ORDER BY count DESC
        """
        )
        admission_courses = cursor.fetchall()

        conn.close()

        return {
            "total_enquiries": total_enquiries,
            "total_admissions": total_admissions,
            "conversion_rate": round(
                (
                    (total_admissions / total_enquiries * 100)
                    if total_enquiries > 0
                    else 0
                ),
                2,
            ),
            "enquiry_by_course": [
                {"course": row[0], "count": row[1]} for row in enquiry_courses
            ],
            "admission_by_course": [
                {"course": row[0], "count": row[1]} for row in admission_courses
            ],
        }
