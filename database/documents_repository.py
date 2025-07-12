import os
from typing import Any, Dict, List, Optional
from .connection import get_db_connection


class DocumentsRepository:
    @staticmethod
    def create_document(document_data: Dict[str, Any]) -> int:
        """Create a new document record"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                INSERT INTO student_documents (
                    student_id, document_type, filename, original_filename,
                    file_size, mime_type, status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_data["student_id"],
                    document_data["document_type"],
                    document_data["filename"],
                    document_data["original_filename"],
                    document_data["file_size"],
                    document_data["mime_type"],
                    document_data.get("status", "UPLOADED"),
                    document_data.get("notes", ""),
                ),
            )
            
            document_id = cursor.lastrowid
            conn.commit()
            return document_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_all_documents() -> List[Dict[str, Any]]:
        """Get all documents with student details"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT 
                sd.id, sd.student_id, sd.document_type, sd.filename,
                sd.original_filename, sd.file_size, sd.mime_type,
                sd.status, sd.notes, sd.created_at, sd.updated_at,
                sa.first_name, sa.middle_name, sa.last_name,
                sa.mobile_number, sa.course_name
            FROM student_documents sd
            JOIN student_admissions sa ON sd.student_id = sa.id
            ORDER BY sd.created_at DESC
            """
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        documents = []
        for row in rows:
            documents.append({
                "id": row[0],
                "student_id": row[1],
                "document_type": row[2],
                "filename": row[3],
                "original_filename": row[4],
                "file_size": row[5],
                "mime_type": row[6],
                "status": row[7],
                "notes": row[8],
                "created_at": row[9],
                "updated_at": row[10],
                "student_name": f"{row[11]} {row[12] or ''} {row[13]}".strip(),
                "mobile_number": row[14],
                "course_name": row[15],
            })
        
        return documents

    @staticmethod
    def get_documents_by_student(student_id: int) -> List[Dict[str, Any]]:
        """Get all documents for a specific student"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT 
                id, student_id, document_type, filename, original_filename,
                file_size, mime_type, status, notes, created_at, updated_at
            FROM student_documents
            WHERE student_id = ?
            ORDER BY created_at DESC
            """,
            (student_id,),
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        documents = []
        for row in rows:
            documents.append({
                "id": row[0],
                "student_id": row[1],
                "document_type": row[2],
                "filename": row[3],
                "original_filename": row[4],
                "file_size": row[5],
                "mime_type": row[6],
                "status": row[7],
                "notes": row[8],
                "created_at": row[9],
                "updated_at": row[10],
            })
        
        return documents

    @staticmethod
    def get_document_by_id(document_id: int) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT 
                sd.id, sd.student_id, sd.document_type, sd.filename,
                sd.original_filename, sd.file_size, sd.mime_type,
                sd.status, sd.notes, sd.created_at, sd.updated_at,
                sa.first_name, sa.middle_name, sa.last_name
            FROM student_documents sd
            JOIN student_admissions sa ON sd.student_id = sa.id
            WHERE sd.id = ?
            """,
            (document_id,),
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "id": row[0],
            "student_id": row[1],
            "document_type": row[2],
            "filename": row[3],
            "original_filename": row[4],
            "file_size": row[5],
            "mime_type": row[6],
            "status": row[7],
            "notes": row[8],
            "created_at": row[9],
            "updated_at": row[10],
            "student_name": f"{row[11]} {row[12] or ''} {row[13]}".strip(),
        }

    @staticmethod
    def update_document_status(document_id: int, status: str, notes: Optional[str] = None) -> bool:
        """Update document status"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if notes is not None:
            cursor.execute(
                "UPDATE student_documents SET status = ?, notes = ? WHERE id = ?",
                (status, notes, document_id)
            )
        else:
            cursor.execute(
                "UPDATE student_documents SET status = ? WHERE id = ?",
                (status, document_id)
            )
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0

    @staticmethod
    def delete_document(document_id: int) -> Optional[str]:
        """Delete document and return filename for file cleanup"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get filename before deletion
        cursor.execute("SELECT filename FROM student_documents WHERE id = ?", (document_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        filename = row[0]
        
        # Delete the record
        cursor.execute("DELETE FROM student_documents WHERE id = ?", (document_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return filename if rows_affected > 0 else None

    @staticmethod
    def get_document_stats() -> Dict[str, Any]:
        """Get document statistics"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total documents
        cursor.execute("SELECT COUNT(*) FROM student_documents")
        total_documents = cursor.fetchone()[0]
        
        # Documents by status
        cursor.execute(
            """
            SELECT status, COUNT(*) as count
            FROM student_documents
            GROUP BY status
            """
        )
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Documents by type
        cursor.execute(
            """
            SELECT document_type, COUNT(*) as count
            FROM student_documents
            GROUP BY document_type
            ORDER BY count DESC
            """
        )
        type_counts = [{"type": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Total file size
        cursor.execute("SELECT COALESCE(SUM(file_size), 0) FROM student_documents")
        total_size = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_documents": total_documents,
            "status_distribution": status_counts,
            "type_distribution": type_counts,
            "total_file_size": total_size,
        }

