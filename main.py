import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import database initialization
from database.connection import (init_courses_table, init_database,
                                 init_followups_table, init_settings_table)
from routers.admission import router as admission_router
from routers.courses import router as course_router
# Import routers
from routers.enquiry import router as enquiry_router
from routers.files import router as files_router
from routers.followups import router as followups_router
from routers.settings import router as settings_router
from routers.stats import router as stats_router

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
app.include_router(files_router)
app.include_router(stats_router)
app.include_router(followups_router)
app.include_router(settings_router)


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    init_database()
    init_courses_table()
    init_followups_table()
    init_settings_table()


@app.get("/")
def read_root():
    return {
        "message": "Student Management System API",
        "version": "1.0.0",
        "endpoints": {
            "enquiries": "/api/enquiries",
            "admissions": "/api/admissions",
            "courses": "/api/courses",
            "followups": "/api/followups",
            "settings": "/api/settings",
            "stats": "/api/stats",
            "files": "/api/file/{filename}",
            "docs": "/docs",
            "redoc": "/redoc",
        },
    }
