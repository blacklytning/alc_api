from typing import Any, Dict, List
from .connection import get_db_connection
from datetime import date

class AttendanceRepository:
    @staticmethod
    def mark_attendance(records: List[Dict[str, Any]]) -> None:
        """Bulk mark attendance for a list of students for a given date and batch."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            for rec in records:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO attendance (student_id, date, batch_timing, status, marked_by)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        rec["student_id"],
                        rec["date"],
                        rec["batch_timing"],
                        rec["status"],
                        rec.get("marked_by", "System User"),
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def get_attendance_by_date_batch(date_str: str, batch_timing: str) -> List[Dict[str, Any]]:
        """Get attendance for all students for a given date and batch."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT a.id, a.student_id, a.date, a.batch_timing, a.status, a.marked_by, a.created_at,
                   sa.first_name, sa.middle_name, sa.last_name, sa.photo_filename
            FROM attendance a
            JOIN student_admissions sa ON a.student_id = sa.id
            WHERE a.date = ? AND a.batch_timing = ?
            ORDER BY sa.first_name, sa.last_name
            """,
            (date_str, batch_timing),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": row[0],
                "student_id": row[1],
                "date": row[2],
                "batch_timing": row[3],
                "status": row[4],
                "marked_by": row[5],
                "created_at": row[6],
                "firstName": row[7],
                "middleName": row[8],
                "lastName": row[9],
                "photoFilename": row[10],
            }
            for row in rows
        ]

    @staticmethod
    def get_attendance_for_student(student_id: int) -> List[Dict[str, Any]]:
        """Get all attendance records for a student."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, date, batch_timing, status, marked_by, created_at
            FROM attendance
            WHERE student_id = ?
            ORDER BY date DESC
            """,
            (student_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": row[0],
                "date": row[1],
                "batch_timing": row[2],
                "status": row[3],
                "marked_by": row[4],
                "created_at": row[5],
            }
            for row in rows
        ]

    @staticmethod
    def get_students_by_batch(batch_timing: str) -> List[Dict[str, Any]]:
        """Get all students in a batch (with photo)."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, first_name, middle_name, last_name, photo_filename
            FROM student_admissions
            WHERE timing = ?
            ORDER BY first_name, last_name
            """,
            (batch_timing,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": row[0],
                "firstName": row[1],
                "middleName": row[2],
                "lastName": row[3],
                "photoFilename": row[4],
            }
            for row in rows
        ] 