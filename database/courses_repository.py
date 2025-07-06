import sqlite3
from typing import Any, Dict, List, Optional

from models import Course, CourseUpdate

from .connection import get_db_connection


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
            raise ValueError("Course name already exists")
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
