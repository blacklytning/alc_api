from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from database.attendance_repository import AttendanceRepository
from database.admission_repository import AdmissionRepository
from datetime import date

router = APIRouter(prefix="/api", tags=["attendance"])

@router.get("/attendance/students")
def get_students_by_batch(batch_timing: str) -> Dict[str, Any]:
    """Get all students in a batch (with photo)"""
    try:
        students = AttendanceRepository.get_students_by_batch(batch_timing)
        return {"students": students, "total": len(students), "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching students: {str(e)}")

@router.post("/attendance/mark")
def mark_attendance(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Bulk mark attendance for a list of students for a given date and batch."""
    try:
        AttendanceRepository.mark_attendance(records)
        return {"message": "Attendance marked successfully", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking attendance: {str(e)}")

@router.get("/attendance/by-date")
def get_attendance_by_date_batch(date_str: str, batch_timing: str) -> Dict[str, Any]:
    """Get attendance for all students for a given date and batch."""
    try:
        records = AttendanceRepository.get_attendance_by_date_batch(date_str, batch_timing)
        return {"attendance": records, "total": len(records), "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching attendance: {str(e)}")

@router.get("/attendance/student/{student_id}")
def get_attendance_for_student(student_id: int) -> Dict[str, Any]:
    """Get all attendance records for a student."""
    try:
        records = AttendanceRepository.get_attendance_for_student(student_id)
        return {"attendance": records, "total": len(records), "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching student attendance: {str(e)}") 