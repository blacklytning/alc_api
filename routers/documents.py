import os
import shutil
import time
from typing import Any, Dict, List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from database.documents_repository import DocumentsRepository
from database.admission_repository import AdmissionRepository

router = APIRouter(prefix="/api", tags=["documents"])

DOCUMENTS_FOLDER = "uploads/documents"
os.makedirs(DOCUMENTS_FOLDER, exist_ok=True)

# Allowed file types and size limit
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    if hasattr(file, 'size') and file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
        )


def save_document_file(student_id: int, document_type: str, file: UploadFile) -> tuple[str, str]:
    """Save uploaded document file and return (filename, original_filename)"""
    timestamp = str(int(time.time()))
    file_extension = file.filename.split(".")[-1].lower()
    
    # Generate unique filename
    filename = f"student_{student_id}_{document_type}_{timestamp}.{file_extension}"
    file_path = os.path.join(DOCUMENTS_FOLDER, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return filename, file.filename


@router.post("/documents/upload")
async def upload_document(
    student_id: int = Form(...),
    document_type: str = Form(...),
    notes: str = Form(""),
    file: UploadFile = File(...),
) -> Dict[str, Any]:
    """Upload a document for a student"""
    try:
        # Validate student exists
        student = AdmissionRepository.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Validate file
        validate_file(file)
        
        # Validate document type
        valid_types = ["SIGNED_ADMISSION_FORM", "IDENTITY_PROOF", "ADDRESS_PROOF", "EDUCATIONAL_CERTIFICATE", "OTHER"]
        if document_type not in valid_types:
            raise HTTPException(status_code=400, detail="Invalid document type")
        
        # Save file
        filename, original_filename = save_document_file(student_id, document_type, file)
        
        # Get file size
        file_path = os.path.join(DOCUMENTS_FOLDER, filename)
        file_size = os.path.getsize(file_path)
        
        # Save document record
        document_data = {
            "student_id": student_id,
            "document_type": document_type,
            "filename": filename,
            "original_filename": original_filename,
            "file_size": file_size,
            "mime_type": file.content_type or "application/octet-stream",
            "status": "UPLOADED",
            "notes": notes,
        }
        
        document_id = DocumentsRepository.create_document(document_data)
        
        return {
            "message": "Document uploaded successfully",
            "document_id": document_id,
            "filename": filename,
            "status": "success",
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@router.get("/documents/uploaded")
def get_uploaded_documents() -> Dict[str, Any]:
    """Get all uploaded documents"""
    try:
        documents = DocumentsRepository.get_all_documents()
        return {
            "documents": documents,
            "total": len(documents),
            "status": "success",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching documents: {str(e)}")


@router.get("/documents/student/{student_id}")
def get_student_documents(student_id: int) -> Dict[str, Any]:
    """Get all documents for a specific student"""
    try:
        # Validate student exists
        student = AdmissionRepository.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        documents = DocumentsRepository.get_documents_by_student(student_id)
        return {
            "documents": documents,
            "total": len(documents),
            "student_name": f"{student['first_name']} {student['last_name']}",
            "status": "success",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching student documents: {str(e)}")


@router.get("/documents/{document_id}")
def get_document_details(document_id: int) -> Dict[str, Any]:
    """Get document details by ID"""
    try:
        document = DocumentsRepository.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "document": document,
            "status": "success",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching document: {str(e)}")


@router.put("/documents/{document_id}/status")
def update_document_status(
    document_id: int,
    status: str = Form(...),
    notes: str = Form(""),
) -> Dict[str, Any]:
    """Update document status"""
    try:
        # Validate status
        valid_statuses = ["UPLOADED", "PENDING", "REJECTED"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        # Check if document exists
        document = DocumentsRepository.get_document_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Update status
        success = DocumentsRepository.update_document_status(document_id, status, notes)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update document status")
        
        return {
            "message": "Document status updated successfully",
            "status": "success",
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating document status: {str(e)}")


@router.delete("/documents/{document_id}")
def delete_document(document_id: int) -> Dict[str, Any]:
    """Delete a document"""
    try:
        # Delete from database and get filename
        filename = DocumentsRepository.delete_document(document_id)
        if not filename:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete physical file
        file_path = os.path.join(DOCUMENTS_FOLDER, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return {
            "message": "Document deleted successfully",
            "status": "success",
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


@router.get("/documents/stats")
def get_document_stats() -> Dict[str, Any]:
    """Get document statistics"""
    try:
        stats = DocumentsRepository.get_document_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching document stats: {str(e)}")


# Serve document files
@router.get("/file/document/{filename}")
def serve_document_file(filename: str) -> FileResponse:
    """Serve document files"""
    file_path = os.path.join(DOCUMENTS_FOLDER, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )

