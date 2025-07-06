from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from models import Course, CourseUpdate
from database.courses_repository import CourseRepository

router = APIRouter(prefix="/api", tags=["courses"])


@router.post("/courses", response_model=Dict[str, Any])
def create_course(course: Course) -> Dict[str, Any]:
    """Create a new course"""
    try:
        course_id = CourseRepository.create(course)
        created_course = CourseRepository.get_by_id(course_id)
        
        return {
            "message": "Course created successfully",
            "course_id": course_id,
            "status": "success",
            "data": created_course
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating course: {str(e)}")


@router.get("/courses", response_model=Dict[str, Any])
def get_all_courses(
    search: Optional[str] = Query(None, description="Search courses by name")
) -> Dict[str, Any]:
    """Get all courses with optional search"""
    try:
        if search:
            courses = CourseRepository.search(search)
        else:
            courses = CourseRepository.get_all()
            
        return {
            "courses": courses,
            "total": len(courses),
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching courses: {str(e)}")


@router.get("/courses/{course_id}", response_model=Dict[str, Any])
def get_course(course_id: int) -> Dict[str, Any]:
    """Get a specific course by ID"""
    try:
        course = CourseRepository.get_by_id(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return {
            "data": course,
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching course: {str(e)}")


@router.put("/courses/{course_id}", response_model=Dict[str, Any])
def update_course(course_id: int, course_update: CourseUpdate) -> Dict[str, Any]:
    """Update a course"""
    try:
        # Check if course exists
        existing_course = CourseRepository.get_by_id(course_id)
        if not existing_course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Update course
        success = CourseRepository.update(course_id, course_update)
        if not success:
            raise HTTPException(status_code=400, detail="No fields to update or update failed")
        
        # Return updated course
        updated_course = CourseRepository.get_by_id(course_id)
        
        return {
            "message": "Course updated successfully",
            "status": "success",
            "data": updated_course
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating course: {str(e)}")


@router.delete("/courses/{course_id}", response_model=Dict[str, Any])
def delete_course(course_id: int) -> Dict[str, Any]:
    """Delete a course"""
    try:
        # Check if course exists
        existing_course = CourseRepository.get_by_id(course_id)
        if not existing_course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Delete course
        success = CourseRepository.delete(course_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to delete course")
        
        return {
            "message": "Course deleted successfully",
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting course: {str(e)}")




