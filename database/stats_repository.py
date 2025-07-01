from typing import Any, Dict

from .connection import get_db_connection


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
