from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from file_handler import FileHandler

router = APIRouter(prefix="/api", tags=["files"])


@router.get("/file/{filename}")
def get_file(filename: str) -> FileResponse:
    """Serve uploaded files"""
    if FileHandler.file_exists(filename):
        file_path = FileHandler.get_file_path(filename)
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")
