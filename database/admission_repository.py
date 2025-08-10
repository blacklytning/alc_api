from typing import Any, Dict, List, Optional

from .connection import get_db_connection


class AdmissionRepository:

    @staticmethod
    def update_exam_result(
        admission_id: int, exam_date: str, era_score: int, final_score: int, result: str
    ) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM student_admissions WHERE id = ?", (admission_id,)
        )
        if not cursor.fetchone():
            conn.close()
            return False
        cursor.execute(
            """
            UPDATE student_admissions
            SET exam_date = ?, era_score = ?, final_score = ?, result = ?
            WHERE id = ?
            """,
            (exam_date, era_score, final_score, result, admission_id),
        )
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def update_credentials(
        admission_id: int, learner_code: str, era_id: str, era_password: str
    ) -> bool:
        """Update learner credentials for a student admission"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM student_admissions WHERE id = ?", (admission_id,)
        )
        if not cursor.fetchone():
            conn.close()
            return False
        cursor.execute(
            """
            UPDATE student_admissions
            SET learner_code = ?, era_id = ?, era_password = ?
            WHERE id = ?
            """,
            (learner_code, era_id, era_password, admission_id),
        )
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def create(admission_data: Dict[str, Any]) -> int:
        """Create a new admission and return its ID"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO student_admissions (
                first_name, middle_name, last_name, date_of_birth, gender,
                marital_status, mother_tongue, aadhar_number,
                correspondence_address, city, state, district,
                mobile_number, alternate_mobile_number, category,
                educational_qualification, course_name, timing,
                certificate_name, referred_by,
                photo_filename, signature_filename
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                admission_data["firstName"],
                admission_data["middleName"],
                admission_data["lastName"],
                admission_data["dateOfBirth"],
                admission_data["gender"],
                admission_data["maritalStatus"],
                admission_data["motherTongue"],
                admission_data["aadharNumber"],
                admission_data["correspondenceAddress"],
                admission_data["city"],
                admission_data["state"],
                admission_data["district"],
                admission_data["mobileNumber"],
                admission_data["alternateMobileNumber"],
                admission_data["category"],
                admission_data["educationalQualification"],
                admission_data["courseName"],
                admission_data["timing"],
                admission_data["certificateName"],
                admission_data["referredBy"],
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
            SELECT id, first_name, middle_name, last_name, date_of_birth,
                   gender, marital_status, mother_tongue, aadhar_number,
                   correspondence_address, city, state, district,
                   mobile_number, alternate_mobile_number, category,
                   educational_qualification, course_name, timing,
                   certificate_name, referred_by,
                   photo_filename, signature_filename, created_at
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
                    "certificateName": row[19],
                    "referredBy": row[20],
                    "photoFilename": row[21],
                    "signatureFilename": row[22],
                    "createdAt": row[23],
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
            SELECT id, first_name, middle_name, last_name, date_of_birth,
                   gender, marital_status, mother_tongue, aadhar_number,
                   correspondence_address, city, state, district,
                   mobile_number, alternate_mobile_number, category,
                   educational_qualification, course_name, timing,
                   certificate_name, referred_by,
                   photo_filename, signature_filename, created_at,
                   learner_code, era_id, era_password,
                   exam_date, era_score, final_score, result
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
            "certificateName": row[19],
            "referredBy": row[20],
            "photoFilename": row[21],
            "signatureFilename": row[22],
            "createdAt": row[23],
            "learner_code": row[24],
            "era_id": row[25],
            "era_password": row[26],
            "exam_date": row[27],
            "era_score": row[28],
            "final_score": row[29],
            "result": row[30],
        }

    @staticmethod
    def update(admission_id: int, admission_data: Dict[str, Any]) -> bool:
        """Update an existing admission"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if admission exists
        cursor.execute(
            "SELECT id FROM student_admissions WHERE id = ?", (admission_id,)
        )
        if not cursor.fetchone():
            conn.close()
            return False

        # Update admission data
        cursor.execute(
            """
            UPDATE student_admissions SET
                first_name = ?, middle_name = ?, last_name = ?, date_of_birth = ?,
                gender = ?, marital_status = ?, mother_tongue = ?, aadhar_number = ?,
                correspondence_address = ?, city = ?, state = ?, district = ?,
                mobile_number = ?, alternate_mobile_number = ?, category = ?,
                educational_qualification = ?, course_name = ?, timing = ?,
                certificate_name = ?, referred_by = ?
            WHERE id = ?
            """,
            (
                admission_data["firstName"],
                admission_data["middleName"],
                admission_data["lastName"],
                admission_data["dateOfBirth"],
                admission_data["gender"],
                admission_data["maritalStatus"],
                admission_data["motherTongue"],
                admission_data["aadharNumber"],
                admission_data["correspondenceAddress"],
                admission_data["city"],
                admission_data["state"],
                admission_data["district"],
                admission_data["mobileNumber"],
                admission_data["alternateMobileNumber"],
                admission_data["category"],
                admission_data["educationalQualification"],
                admission_data["courseName"],
                admission_data["timing"],
                admission_data["certificateName"],
                admission_data["referredBy"],
                admission_id,
            ),
        )

        # Update photo filename if provided
        if "photoFilename" in admission_data and admission_data["photoFilename"]:
            cursor.execute(
                "UPDATE student_admissions SET photo_filename = ? WHERE id = ?",
                (admission_data["photoFilename"], admission_id),
            )

        # Update signature filename if provided
        if (
            "signatureFilename" in admission_data
            and admission_data["signatureFilename"]
        ):
            cursor.execute(
                "UPDATE student_admissions SET signature_filename = ? WHERE id = ?",
                (admission_data["signatureFilename"], admission_id),
            )

        conn.commit()
        conn.close()
        return True
