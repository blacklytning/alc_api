import os

from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from database.user_repository import get_user_by_username, create_user, user_count
from auth_utils import hash_password, verify_password, create_access_token, decode_access_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional

# Import database initialization
from database.connection import (init_courses_table, init_database,
                                 init_followups_table, init_fee_payments_table, init_settings_table, init_attendance_table, init_documents_table)
from routers.admission import router as admission_router
from routers.courses import router as course_router
# Import routers
from routers.enquiry import router as enquiry_router
from routers.fees import router as fees_router
from routers.files import router as files_router
from routers.followups import router as followups_router
from routers.settings import router as settings_router
from routers.stats import router as stats_router
from routers.attendance import router as attendance_router
from routers.documents import router as documents_router

UPLOAD_FOLDER = "uploads"
DOCUMENTS_FOLDER = "uploads/documents"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOCUMENTS_FOLDER, exist_ok=True)

app = FastAPI(
    title="Student Management System API",
    description="A comprehensive API for managing student enquiries, admissions, courses, follow-ups, and settings",
    version="1.0.0",
)

# Add CORS middleware to allow frontend requests (Verify for prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files to serve uploaded images
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

# Include routers
app.include_router(enquiry_router)
app.include_router(admission_router)
app.include_router(course_router)
app.include_router(fees_router)
app.include_router(files_router)
app.include_router(stats_router)
app.include_router(followups_router)
app.include_router(settings_router)
app.include_router(attendance_router)
app.include_router(documents_router)


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    init_database()
    init_courses_table()
    init_followups_table()
    init_fee_payments_table()
    init_settings_table()
    init_attendance_table()
    init_documents_table()


# Pydantic models for auth
class UserRegister(BaseModel):
    username: str
    password: str
    role: str  # 'admin' or 'staff'

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login",auto_error=False)

# Dependency to get current user from JWT
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user, _ = get_user_by_username(payload.get("sub"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Dependency to get current user from JWT
def get_current_user_optional(token: str = Depends(oauth2_scheme)):
    if user_count() == 0:
        return None
    return get_current_user(token)

@app.post("/register", response_model=Token)
def register(user: UserRegister, current_user=Depends(get_current_user_optional)):
    if user_count() == 0:
        # First user must be admin
        if user.role != "admin":
            raise HTTPException(status_code=400, detail="First user must be an admin")
    else:
        # Only allow admins to register new users
        if current_user is None:
            raise HTTPException(status_code=401, detail="Authentication required")
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Only admins can create new users")
    existing_user, _ = get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    if user.role not in ("admin", "staff"):
        raise HTTPException(status_code=400, detail="Role must be 'admin' or 'staff'")
    hashed_pw = hash_password(user.password)
    new_user = create_user(user.username, hashed_pw, user.role)
    token = create_access_token({"sub": new_user.username, "role": new_user.role})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user, hashed_pw = get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, hashed_pw):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/change-password")
def change_password(
    old_password: str = Body(...),
    new_password: str = Body(...),
    current_user=Depends(get_current_user)
):
    # Fetch user and hashed password
    user, hashed_pw = get_user_by_username(current_user.username)
    if not user or not verify_password(old_password, hashed_pw):
        raise HTTPException(status_code=401, detail="Incorrect old password")
    # Hash new password and update in DB
    from database.connection import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET hashed_password = ? WHERE username = ?",
        (hash_password(new_password), current_user.username)
    )
    conn.commit()
    conn.close()
    return {"detail": "Password changed successfully"}


@app.get("/check-setup")
def check_setup():
    if user_count() == 0:
        raise HTTPException(status_code=307)
    return {"setup_complete": True}

# Example protected route
@app.get("/me")
def read_users_me(current_user=Depends(get_current_user)):
    return current_user

@app.get("/")
def read_root():
    return {
        "message": "Student Management System API",
        "version": "1.0.0",
        "endpoints": {
            "enquiries": "/api/enquiries",
            "admissions": "/api/admissions",
            "courses": "/api/courses",
            "fees": "/api/fees",
            "followups": "/api/followups",
            "settings": "/api/settings",
            "stats": "/api/stats",
            "attendance": "/api/attendance",
            "documents": "/api/documents",
            "files": "/api/file/{filename}",
            "docs": "/docs",
            "redoc": "/redoc",
        },
    }
