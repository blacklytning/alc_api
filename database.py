import sqlite3
from typing import Any, Dict, List, Optional

from models import Course, CourseUpdate, StudentEnquiry

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
            handled_by TEXT NOT NULL,
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


def init_courses_table():
    """Initialize the courses table"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL UNIQUE,
            fees INTEGER NOT NULL CHECK(fees > 0),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Create trigger to update updated_at timestamp
    cursor.execute(
        """
        CREATE TRIGGER IF NOT EXISTS update_courses_timestamp 
        AFTER UPDATE ON courses
        BEGIN
            UPDATE courses SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        """
    )

    # Insert default courses if table is empty
    cursor.execute("SELECT COUNT(*) FROM courses")
    count = cursor.fetchone()[0]

    if count == 0:
        default_courses = [
            ("MS-CIT", 2500),
            ("ADVANCE TALLY - CIT", 3500),
            ("ADVANCE TALLY - KLIC", 3000),
            ("ADVANCE EXCEL - CIT", 2000),
            ("ENGLISH TYPING - MKCL", 1500),
            ("ENGLISH TYPING - CIT", 1800),
            ("MARATHI TYPING - MKCL", 1500),
            ("DTP - CIT", 2200),
            ("IT - KLIC", 4000),
            ("KLIC DIPLOMA", 5000),
        ]

        cursor.executemany(
            "INSERT INTO courses (course_name, fees) VALUES (?, ?)", default_courses
        )

    conn.commit()
    conn.close()


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
                category, educational_qualification, course_name, timing, handled_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                enquiry.handledBy,
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
                   category, educational_qualification, course_name, timing, handled_by, created_at
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
                    "handledBy": row[19],
                    "createdAt": row[20],
                }
            )

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
                   category, educational_qualification, course_name, timing, handled_by, created_at
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
            "handledBy": row[19],
            "createdAt": row[20],
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
                    "photoFilename": row[18],
                    "signatureFilename": row[19],
                    "createdAt": row[20],
                }
            )

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


class CourseRepository:
    @staticmethod
    def create(course: Course) -> int:
        """Create a new course and return its ID"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO courses (course_name, fees) VALUES (?, ?)",
                (course.courseName, course.fees),
            )
            course_id = cursor.lastrowid
            conn.commit()
            return course_id
        except sqlite3.IntegrityError:
            raise ValueError(f"Course '{course.courseName}' already exists")
        finally:
            conn.close()

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all courses"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, course_name, fees, created_at, updated_at
            FROM courses
            ORDER BY course_name ASC
            """
        )

        rows = cursor.fetchall()
        conn.close()

        courses = []
        for row in rows:
            courses.append(
                {
                    "id": row[0],
                    "courseName": row[1],
                    "fees": row[2],
                    "createdAt": row[3],
                    "updatedAt": row[4],
                }
            )

        return courses

    @staticmethod
    def get_by_id(course_id: int) -> Optional[Dict[str, Any]]:
        """Get course by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, course_name, fees, created_at, updated_at
            FROM courses
            WHERE id = ?
            """,
            (course_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            "id": row[0],
            "courseName": row[1],
            "fees": row[2],
            "createdAt": row[3],
            "updatedAt": row[4],
        }

    @staticmethod
    def update(course_id: int, course_update: CourseUpdate) -> bool:
        """Update a course"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Build dynamic query based on provided fields
        update_fields = []
        update_values = []

        if course_update.courseName is not None:
            update_fields.append("course_name = ?")
            update_values.append(course_update.courseName)

        if course_update.fees is not None:
            update_fields.append("fees = ?")
            update_values.append(course_update.fees)

        if not update_fields:
            conn.close()
            return False

        update_values.append(course_id)
        query = f"UPDATE courses SET {', '.join(update_fields)} WHERE id = ?"

        try:
            cursor.execute(query, update_values)
            rows_affected = cursor.rowcount
            conn.commit()
            return rows_affected > 0
        except sqlite3.IntegrityError:
            raise ValueError(f"Course name already exists")
        finally:
            conn.close()

    @staticmethod
    def delete(course_id: int) -> bool:
        """Delete a course"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()

        return rows_affected > 0

    @staticmethod
    def search(search_term: str) -> List[Dict[str, Any]]:
        """Search courses by name"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, course_name, fees, created_at, updated_at
            FROM courses
            WHERE course_name LIKE ?
            ORDER BY course_name ASC
            """,
            (f"%{search_term}%",),
        )

        rows = cursor.fetchall()
        conn.close()

        courses = []
        for row in rows:
            courses.append(
                {
                    "id": row[0],
                    "courseName": row[1],
                    "fees": row[2],
                    "createdAt": row[3],
                    "updatedAt": row[4],
                }
            )

        return courses

    @staticmethod
    def get_course_stats() -> Dict[str, Any]:
        """Get course statistics"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Total courses
        cursor.execute("SELECT COUNT(*) FROM courses")
        total_courses = cursor.fetchone()[0]

        # Average fees
        cursor.execute("SELECT AVG(fees) FROM courses")
        avg_fees = cursor.fetchone()[0] or 0

        # Min and max fees
        cursor.execute("SELECT MIN(fees), MAX(fees) FROM courses")
        min_fees, max_fees = cursor.fetchone()

        # Most expensive course
        cursor.execute(
            "SELECT course_name, fees FROM courses WHERE fees = (SELECT MAX(fees) FROM courses) LIMIT 1"
        )
        most_expensive = cursor.fetchone()

        # Least expensive course
        cursor.execute(
            "SELECT course_name, fees FROM courses WHERE fees = (SELECT MIN(fees) FROM courses) LIMIT 1"
        )
        least_expensive = cursor.fetchone()

        conn.close()

        return {
            "total_courses": total_courses,
            "average_fees": round(avg_fees, 2),
            "min_fees": min_fees or 0,
            "max_fees": max_fees or 0,
            "most_expensive": {
                "course_name": most_expensive[0] if most_expensive else None,
                "fees": most_expensive[1] if most_expensive else None,
            },
            "least_expensive": {
                "course_name": least_expensive[0] if least_expensive else None,
                "fees": least_expensive[1] if least_expensive else None,
            },
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


def init_followups_table():
    """Initialize the followups table"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS followups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enquiry_id INTEGER NOT NULL,
            followup_date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('PENDING', 'INTERESTED', 'NOT_INTERESTED', 'ADMITTED')),
            notes TEXT DEFAULT '',
            next_followup_date TEXT,
            handled_by TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (enquiry_id) REFERENCES student_enquiries (id) ON DELETE CASCADE
        )
        """
    )

    # Create trigger to update updated_at timestamp
    cursor.execute(
        """
        CREATE TRIGGER IF NOT EXISTS update_followups_timestamp 
        AFTER UPDATE ON followups
        BEGIN
            UPDATE followups SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        """
    )

    # Create index for better query performance
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_followups_enquiry_id ON followups(enquiry_id);
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_followups_next_date ON followups(next_followup_date);
        """
    )

    conn.commit()
    conn.close()


class FollowupRepository:
    @staticmethod
    def create(followup_data: Dict[str, Any]) -> int:
        """Create a new follow-up record"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO followups (
                enquiry_id, followup_date, status, notes, 
                next_followup_date, handled_by
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                followup_data["enquiry_id"],
                followup_data["followup_date"],
                followup_data["status"],
                followup_data.get("notes", ""),
                followup_data.get("next_followup_date"),
                followup_data["handled_by"],
            ),
        )

        followup_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return followup_id

    @staticmethod
    def get_by_enquiry_id(enquiry_id: int) -> List[Dict[str, Any]]:
        """Get all follow-ups for a specific enquiry"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, enquiry_id, followup_date, status, notes, 
                   next_followup_date, handled_by, created_at, updated_at
            FROM followups
            WHERE enquiry_id = ?
            ORDER BY followup_date DESC
            """,
            (enquiry_id,),
        )

        rows = cursor.fetchall()
        conn.close()

        followups = []
        for row in rows:
            followups.append(
                {
                    "id": row[0],
                    "enquiry_id": row[1],
                    "followup_date": row[2],
                    "status": row[3],
                    "notes": row[4],
                    "next_followup_date": row[5],
                    "handled_by": row[6],
                    "created_at": row[7],
                    "updated_at": row[8],
                }
            )

        return followups

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all follow-ups"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT f.id, f.enquiry_id, f.followup_date, f.status, f.notes, 
                   f.next_followup_date, f.handled_by, f.created_at, f.updated_at,
                   e.first_name, e.last_name, e.mobile_number, e.course_name
            FROM followups f
            JOIN student_enquiries e ON f.enquiry_id = e.id
            ORDER BY f.followup_date DESC
            """
        )

        rows = cursor.fetchall()
        conn.close()

        followups = []
        for row in rows:
            followups.append(
                {
                    "id": row[0],
                    "enquiry_id": row[1],
                    "followup_date": row[2],
                    "status": row[3],
                    "notes": row[4],
                    "next_followup_date": row[5],
                    "handled_by": row[6],
                    "created_at": row[7],
                    "updated_at": row[8],
                    "student_name": f"{row[9]} {row[10]}",
                    "mobile_number": row[11],
                    "course_name": row[12],
                }
            )

        return followups

    @staticmethod
    def get_enquiries_with_followup_summary() -> List[Dict[str, Any]]:
        """Get all enquiries with their follow-up summary"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                e.id,
                e.first_name,
                e.middle_name,
                e.last_name,
                e.mobile_number,
                e.course_name,
                DATE(e.created_at) as enquiry_date,
                COALESCE(latest_followup.status, 'PENDING') as current_status,
                latest_followup.followup_date as last_followup,
                latest_followup.next_followup_date as next_followup,
                COALESCE(followup_counts.total_followups, 0) as followup_count,
                latest_followup.notes as latest_notes
            FROM student_enquiries e
            LEFT JOIN (
                SELECT 
                    enquiry_id,
                    followup_date,
                    next_followup_date,
                    status,
                    notes,
                    ROW_NUMBER() OVER (PARTITION BY enquiry_id ORDER BY followup_date DESC) as rn
                FROM followups
            ) latest_followup ON e.id = latest_followup.enquiry_id AND latest_followup.rn = 1
            LEFT JOIN (
                SELECT enquiry_id, COUNT(*) as total_followups
                FROM followups
                GROUP BY enquiry_id
            ) followup_counts ON e.id = followup_counts.enquiry_id
            ORDER BY 
                CASE 
                    WHEN latest_followup.next_followup_date IS NULL THEN 1
                    WHEN latest_followup.next_followup_date < DATE('now') THEN 0
                    ELSE 2
                END,
                latest_followup.next_followup_date ASC,
                e.created_at DESC
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
                    "middleName": row[2] or "",
                    "lastName": row[3],
                    "mobileNumber": row[4],
                    "courseName": row[5],
                    "enquiryDate": row[6],
                    "currentStatus": row[7],
                    "lastFollowup": row[8],
                    "nextFollowup": row[9],
                    "followupCount": row[10],
                    "latestNotes": row[11],
                }
            )

        return enquiries

    @staticmethod
    def get_overdue_followups() -> List[Dict[str, Any]]:
        """Get enquiries with overdue follow-ups"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                e.id,
                e.first_name,
                e.last_name,
                e.mobile_number,
                e.course_name,
                latest_followup.next_followup_date,
                JULIANDAY('now') - JULIANDAY(latest_followup.next_followup_date) as days_overdue
            FROM student_enquiries e
            JOIN (
                SELECT 
                    enquiry_id,
                    next_followup_date,
                    ROW_NUMBER() OVER (PARTITION BY enquiry_id ORDER BY followup_date DESC) as rn
                FROM followups
                WHERE next_followup_date IS NOT NULL
            ) latest_followup ON e.id = latest_followup.enquiry_id AND latest_followup.rn = 1
            WHERE latest_followup.next_followup_date < DATE('now')
            ORDER BY days_overdue DESC
            """
        )

        rows = cursor.fetchall()
        conn.close()

        overdue = []
        for row in rows:
            overdue.append(
                {
                    "enquiry_id": row[0],
                    "student_name": f"{row[1]} {row[2]}",
                    "mobile_number": row[3],
                    "course_name": row[4],
                    "next_followup_date": row[5],
                    "days_overdue": int(row[6]),
                }
            )

        return overdue

    @staticmethod
    def update(followup_id: int, update_data: Dict[str, Any]) -> bool:
        """Update a follow-up record"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Build dynamic query based on provided fields
        update_fields = []
        update_values = []

        for field, value in update_data.items():
            if value is not None:
                update_fields.append(f"{field} = ?")
                update_values.append(value)

        if not update_fields:
            conn.close()
            return False

        update_values.append(followup_id)
        query = f"UPDATE followups SET {', '.join(update_fields)} WHERE id = ?"

        cursor.execute(query, update_values)
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()

        return rows_affected > 0

    @staticmethod
    def delete(followup_id: int) -> bool:
        """Delete a follow-up record"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM followups WHERE id = ?", (followup_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()

        return rows_affected > 0

    @staticmethod
    def get_followup_stats() -> Dict[str, Any]:
        """Get follow-up statistics"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Total follow-ups
        cursor.execute("SELECT COUNT(*) FROM followups")
        total_followups = cursor.fetchone()[0]

        # Follow-ups by status
        cursor.execute(
            """
            SELECT status, COUNT(*) as count
            FROM followups
            GROUP BY status
            """
        )
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}

        # Overdue count
        cursor.execute(
            """
            SELECT COUNT(DISTINCT enquiry_id)
            FROM followups f1
            WHERE next_followup_date < DATE('now')
            AND NOT EXISTS (
                SELECT 1 FROM followups f2 
                WHERE f2.enquiry_id = f1.enquiry_id 
                AND f2.followup_date > f1.followup_date
            )
            """
        )
        overdue_count = cursor.fetchone()[0]

        # Average follow-ups per enquiry
        cursor.execute(
            """
            SELECT AVG(followup_count) FROM (
                SELECT COUNT(*) as followup_count
                FROM followups
                GROUP BY enquiry_id
            )
            """
        )
        avg_followups = cursor.fetchone()[0] or 0

        conn.close()

        return {
            "total_followups": total_followups,
            "status_distribution": status_counts,
            "overdue_count": overdue_count,
            "average_followups_per_enquiry": round(avg_followups, 2),
        }
