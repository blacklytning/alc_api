from typing import Any, Dict, List

from .connection import get_db_connection


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
