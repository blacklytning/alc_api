import os

# Database configuration
DATABASE_FILE = "student_data.db"

# File upload configuration
UPLOAD_FOLDER = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

# CORS configuration
CORS_ORIGINS = ["*"]  # Change this for production

# API configuration
API_VERSION = "1.0.0"
API_TITLE = "Student Management System API"

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
