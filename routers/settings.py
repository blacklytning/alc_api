import os
import shutil
import tempfile
from typing import Any, Dict

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from database.settings_repository import SettingsRepository

router = APIRouter(prefix="/api", tags=["settings"])

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.get("/settings/institute")
def get_institute_settings() -> Dict[str, Any]:
    """Get institute settings"""
    try:
        settings = SettingsRepository.get_institute_settings()
        if not settings:
            # Return default settings if none exist
            return {
                "id": 0,
                "name": "Your Institute Name",
                "centerCode": "",
                "address": "",
                "phone": "",
                "email": "",
                "website": "",
                "logo": None,
                "created_at": "",
                "updated_at": None,
            }
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/settings/institute")
def update_institute_settings(
    name: str = Form(...),
    centerCode: str = Form(""),
    address: str = Form(""),
    phone: str = Form(""),
    email: str = Form(""),
    website: str = Form(""),
    logo: UploadFile = File(None),
) -> Dict[str, Any]:
    """Update institute settings"""
    try:
        # Validate required fields
        if not name.strip():
            raise HTTPException(status_code=400, detail="Institute name is required")

        settings_data = {
            "name": name.strip(),
            "centerCode": centerCode.strip(),
            "address": address.strip(),
            "phone": phone.strip(),
            "email": email.strip(),
            "website": website.strip(),
        }

        # Handle logo upload
        if logo and logo.filename:
            # Validate file type
            allowed_extensions = {"png", "jpg", "jpeg", "gif"}
            file_extension = logo.filename.split(".")[-1].lower()

            if file_extension not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file type. Only PNG, JPG, JPEG, GIF allowed",
                )

            # Validate file size (5MB limit)
            if logo.size and logo.size > 5 * 1024 * 1024:
                raise HTTPException(
                    status_code=400, detail="File size too large. Maximum 5MB allowed"
                )

            # Generate unique filename
            logo_filename = f"institute_logo.{file_extension}"
            logo_path = os.path.join(UPLOAD_FOLDER, logo_filename)

            # Save the file
            with open(logo_path, "wb") as logo_file:
                shutil.copyfileobj(logo.file, logo_file)

            settings_data["logo"] = logo_filename
        else:
            # Keep existing logo if no new logo uploaded
            existing_settings = SettingsRepository.get_institute_settings()
            if existing_settings:
                settings_data["logo"] = existing_settings.get("logo")

        # Update settings in database
        success = SettingsRepository.update_institute_settings(settings_data)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to update settings")

        return {
            "message": "Institute settings updated successfully",
            "status": "success",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating settings: {str(e)}"
        )


@router.get("/settings/database/stats")
def get_database_stats() -> Dict[str, Any]:
    """Get database statistics"""
    try:
        stats = SettingsRepository.get_database_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting database stats: {str(e)}"
        )


@router.post("/settings/database/backup")
def create_database_backup():
    """Create database backup and return as downloadable file"""
    try:
        backup_path = SettingsRepository.create_backup()
        if not backup_path:
            raise HTTPException(status_code=500, detail="Failed to create backup")

        return FileResponse(
            path=backup_path,
            filename=os.path.basename(backup_path),
            media_type="application/octet-stream",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating backup: {str(e)}")


@router.post("/settings/database/restore")
def restore_database_backup(backup_file: UploadFile = File(...)) -> Dict[str, Any]:
    """Restore database from backup file"""
    try:
        # Validate file
        if not backup_file.filename:
            raise HTTPException(status_code=400, detail="No file provided")

        # Check file extension
        allowed_extensions = {".sql", ".db", ".backup"}
        file_extension = os.path.splitext(backup_file.filename)[1].lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Invalid backup file format")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=file_extension
        ) as tmp_file:
            shutil.copyfileobj(backup_file.file, tmp_file)
            tmp_file_path = tmp_file.name

        try:
            # Restore from backup
            success = SettingsRepository.restore_backup(tmp_file_path)

            if not success:
                raise HTTPException(status_code=500, detail="Failed to restore backup")

            return {"message": "Database restored successfully", "status": "success"}

        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error restoring backup: {str(e)}")
