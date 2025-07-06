import sqlite3
from typing import Any, Dict, List, Optional
from datetime import datetime
from .connection import get_db_connection


class FeesRepository:
    @staticmethod
    def create_payment(payment_data: Dict[str, Any]) -> int:
        """Create a new payment record"""
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO fee_payments (
                    student_id, amount, payment_date, payment_method,
                    transaction_id, notes, late_fee, handled_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payment_data["student_id"],
                    payment_data["amount"],
                    payment_data["payment_date"],
                    payment_data["payment_method"],
                    payment_data.get("transaction_id", ""),
                    payment_data.get("notes", ""),
                    payment_data.get("late_fee", 0),
                    payment_data.get("handled_by", "System User"),
                ),
            )

            payment_id = cursor.lastrowid
            conn.commit()
            return payment_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_all_payments() -> List[Dict[str, Any]]:
        """Get all payment records with student details"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                fp.id, fp.student_id, fp.amount, fp.payment_date,
                fp.payment_method, fp.transaction_id, fp.notes,
                fp.late_fee, fp.handled_by, fp.created_at,
                sa.first_name, sa.middle_name, sa.last_name,
                sa.mobile_number, sa.course_name
            FROM fee_payments fp
            JOIN student_admissions sa ON fp.student_id = sa.id
            ORDER BY fp.payment_date DESC
            """
        )

        rows = cursor.fetchall()
        conn.close()

        payments = []
        for row in rows:
            payments.append({
                "id": row[0],
                "student_id": row[1],
                "amount": row[2],
                "payment_date": row[3],
                "payment_method": row[4],
                "transaction_id": row[5],
                "notes": row[6],
                "late_fee": row[7],
                "handled_by": row[8],
                "created_at": row[9],
                "student_name": f"{row[10]} {row[11] or ''} {row[12]}".strip(),
                "mobile_number": row[13],
                "course_name": row[14],
            })

        return payments

    @staticmethod
    def get_payments_by_student(student_id: int) -> List[Dict[str, Any]]:
        """Get all payments for a specific student"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                id, student_id, amount, payment_date, payment_method,
                transaction_id, notes, late_fee, handled_by, created_at
            FROM fee_payments
            WHERE student_id = ?
            ORDER BY payment_date DESC
            """,
            (student_id,),
        )

        rows = cursor.fetchall()
        conn.close()

        payments = []
        for row in rows:
            payments.append({
                "id": row[0],
                "student_id": row[1],
                "amount": row[2],
                "payment_date": row[3],
                "payment_method": row[4],
                "transaction_id": row[5],
                "notes": row[6],
                "late_fee": row[7],
                "handled_by": row[8],
                "created_at": row[9],
            })

        return payments

    @staticmethod
    def get_fee_summary() -> List[Dict[str, Any]]:
        """Get fee summary for all students with payment status"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get all students with their course fees
        cursor.execute(
            """
            SELECT 
                sa.id, sa.first_name, sa.middle_name, sa.last_name,
                sa.mobile_number, sa.course_name, sa.created_at,
                c.fees as course_fee
            FROM student_admissions sa
            LEFT JOIN courses c ON sa.course_name = c.course_name
            ORDER BY sa.created_at DESC
            """
        )

        students = cursor.fetchall()
        fee_summary = []

        for student in students:
            student_id = student[0]
            
            # Calculate total due (course fee)
            course_fee = student[7] or 2000  # Default fee if not found
            
            # Get total paid
            cursor.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM fee_payments WHERE student_id = ?",
                (student_id,)
            )
            total_paid = cursor.fetchone()[0] or 0
            
            # Calculate balance
            balance = course_fee - total_paid
            
            # Determine status
            if balance <= 0:
                status = "PAID"
            elif total_paid > 0:
                status = "PARTIAL"
            else:
                status = "PENDING"
            
            # Check if overdue (more than 1 month since admission)
            admission_date = datetime.strptime(student[6], "%Y-%m-%d %H:%M:%S")
            today = datetime.now()
            months_diff = (today.year - admission_date.year) * 12 + (today.month - admission_date.month)
            
            if balance > 0 and months_diff > 0:
                status = "OVERDUE"
            
            fee_summary.append({
                "student_id": student_id,
                "student_name": f"{student[1]} {student[2] or ''} {student[3]}".strip(),
                "mobile_number": student[4],
                "course_name": student[5],
                "admission_date": student[6],
                "course_fee": course_fee,
                "total_paid": total_paid,
                "balance": balance,
                "status": status,
                "is_overdue": status == "OVERDUE",
                "months_overdue": months_diff if status == "OVERDUE" else 0,
            })

        conn.close()
        return fee_summary

    @staticmethod
    def get_student_fee_details(student_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed fee information for a specific student"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get student info
        cursor.execute(
            """
            SELECT 
                sa.id, sa.first_name, sa.middle_name, sa.last_name,
                sa.mobile_number, sa.course_name, sa.created_at,
                c.fees as course_fee
            FROM student_admissions sa
            LEFT JOIN courses c ON sa.course_name = c.course_name
            WHERE sa.id = ?
            """,
            (student_id,),
        )

        student = cursor.fetchone()
        if not student:
            conn.close()
            return None

        # Get total paid
        cursor.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM fee_payments WHERE student_id = ?",
            (student_id,)
        )
        total_paid = cursor.fetchone()[0] or 0

        # Get payment history
        cursor.execute(
            """
            SELECT 
                id, amount, payment_date, payment_method, transaction_id,
                notes, late_fee, handled_by, created_at
            FROM fee_payments
            WHERE student_id = ?
            ORDER BY payment_date DESC
            """,
            (student_id,),
        )

        payments = []
        for row in cursor.fetchall():
            payments.append({
                "id": row[0],
                "amount": row[1],
                "payment_date": row[2],
                "payment_method": row[3],
                "transaction_id": row[4],
                "notes": row[5],
                "late_fee": row[6],
                "handled_by": row[7],
                "created_at": row[8],
            })

        course_fee = student[7] or 2000
        balance = course_fee - total_paid

        conn.close()

        return {
            "student_id": student[0],
            "student_name": f"{student[1]} {student[2] or ''} {student[3]}".strip(),
            "mobile_number": student[4],
            "course_name": student[5],
            "admission_date": student[6],
            "course_fee": course_fee,
            "total_paid": total_paid,
            "balance": balance,
            "payments": payments,
        } 