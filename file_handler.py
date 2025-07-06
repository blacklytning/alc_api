import os
import shutil
import time
from typing import Tuple

from fastapi import UploadFile

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class FileHandler:
    @staticmethod
    def save_admission_files(
        mobile_number: str, photo: UploadFile, signature: UploadFile
    ) -> Tuple[str, str]:
        """Save uploaded photo and signature files"""
        timestamp = str(int(time.time()))

        # Generate unique filenames
        photo_filename = f"{mobile_number}_{
            timestamp}_photo.{photo.filename.split('.')[-1]}"
        signature_filename = f"{mobile_number}_{
            timestamp}_signature.{signature.filename.split('.')[-1]}"

        photo_path = os.path.join(UPLOAD_FOLDER, photo_filename)
        signature_path = os.path.join(UPLOAD_FOLDER, signature_filename)

        # Save files
        with open(photo_path, "wb") as photo_file:
            shutil.copyfileobj(photo.file, photo_file)

        with open(signature_path, "wb") as signature_file:
            shutil.copyfileobj(signature.file, signature_file)

        return photo_filename, signature_filename

    @staticmethod
    def file_exists(filename: str) -> bool:
        """Check if file exists"""
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        return os.path.exists(file_path)

    @staticmethod
    def get_file_path(filename: str) -> str:
        """Get full file path"""
        return os.path.join(UPLOAD_FOLDER, filename)
