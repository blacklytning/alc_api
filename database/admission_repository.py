from typing import Any, Dict, List, Optional
from .connection import get_db_connection


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
