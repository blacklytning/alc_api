import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, Optional
import zipfile
import shutil
import tempfile

from .connection import get_db_connection


class SettingsRepository:


    @staticmethod
    def get_institute_settings() -> Optional[Dict[str, Any]]:
        """Get institute settings"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, name, center_code, address, phone, email, website, logo, created_at, updated_at
            FROM institute_settings
            ORDER BY id DESC
            LIMIT 1
            """
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row[0],
                "name": row[1],
                "centerCode": row[2],
                "address": row[3],
                "phone": row[4],
                "email": row[5],
                "website": row[6],
                "logo": row[7],
                "created_at": row[8],
                "updated_at": row[9],
            }
        return None

    @staticmethod
    def update_institute_settings(settings_data: Dict[str, Any]) -> bool:
        """Update institute settings"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if settings exist
            cursor.execute("SELECT COUNT(*) FROM institute_settings")
            count = cursor.fetchone()[0]

            if count == 0:
                # Insert new settings
                cursor.execute(
                    """
                    INSERT INTO institute_settings (name, center_code, address, phone, email, website, logo)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        settings_data.get("name", ""),
                        settings_data.get("centerCode", ""),
                        settings_data.get("address", ""),
                        settings_data.get("phone", ""),
                        settings_data.get("email", ""),
                        settings_data.get("website", ""),
                        settings_data.get("logo", None),
                    ),
                )
            else:
                # Update existing settings
                cursor.execute(
                    """
                    UPDATE institute_settings
                    SET name = ?, center_code = ?, address = ?, phone = ?, email = ?, website = ?, logo = ?
                    WHERE id = (SELECT id FROM institute_settings ORDER BY id DESC LIMIT 1)
                    """,
                    (
                        settings_data.get("name", ""),
                        settings_data.get("centerCode", ""),
                        settings_data.get("address", ""),
                        settings_data.get("phone", ""),
                        settings_data.get("email", ""),
                        settings_data.get("website", ""),
                        settings_data.get("logo", None),
                    ),
                )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating settings: {e}")
            return False

    @staticmethod
    def get_database_stats() -> Dict[str, Any]:
        """Get database statistics"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Get database file size
            db_file = "student_data.db"
            db_size = os.path.getsize(
                db_file) if os.path.exists(db_file) else 0

            # Count total records
            total_records = 0
            tables = [
                "student_enquiries",
                "student_admissions",
                "courses",
                "followups",
                "institute_settings",
            ]

            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    total_records += count
                except:
                    pass

            # Get last backup info (simulated - you can implement actual backup tracking)
            last_backup = None
            backup_history = []

            # Check for backup files in a backups directory
            backup_dir = "backups"
            if os.path.exists(backup_dir):
                backup_files = [
                    f
                    for f in os.listdir(backup_dir)
                    if f.endswith(".sql") or f.endswith(".db")
                ]
                backup_files.sort(
                    key=lambda x: os.path.getmtime(
                        os.path.join(backup_dir, x)),
                    reverse=True,
                )

                if backup_files:
                    latest_backup = backup_files[0]
                    backup_path = os.path.join(backup_dir, latest_backup)
                    last_backup = datetime.fromtimestamp(
                        os.path.getmtime(backup_path)
                    ).isoformat()

                    # Get backup history (last 5 backups)
                    for backup_file in backup_files[:5]:
                        backup_path = os.path.join(backup_dir, backup_file)
                        backup_history.append(
                            {
                                "filename": backup_file,
                                "created": datetime.fromtimestamp(
                                    os.path.getmtime(backup_path)
                                ).isoformat(),
                                "size": os.path.getsize(backup_path),
                                "status": "completed",
                            }
                        )

            conn.close()

            return {
                "lastBackup": last_backup,
                "databaseSize": db_size,
                "totalRecords": total_records,
                "backupHistory": backup_history,
            }
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {
                "lastBackup": None,
                "databaseSize": 0,
                "totalRecords": 0,
                "backupHistory": [],
            }

    @staticmethod
    def create_backup() -> Optional[str]:
        """Create database and uploads backup as a zip file"""
        try:
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"edumanage_backup_{timestamp}.sql"
            backup_path = os.path.join(backup_dir, backup_filename)

            # Create SQL dump
            conn = get_db_connection()
            with open(backup_path, "w") as f:
                for line in conn.iterdump():
                    f.write("%s\n" % line)
            conn.close()

            # Create zip containing SQL and uploads
            zip_filename = f"edumanage_backup_{timestamp}.zip"
            zip_path = os.path.join(backup_dir, zip_filename)
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                # Add SQL dump
                zipf.write(backup_path, arcname=os.path.basename(backup_path))
                # Add uploads folder
                uploads_dir = "uploads"
                if os.path.exists(uploads_dir):
                    for root, dirs, files in os.walk(uploads_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, uploads_dir)
                            zipf.write(file_path, arcname=os.path.join("uploads", arcname))
            # Optionally remove the raw SQL file after zipping
            os.remove(backup_path)
            return zip_path
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None

    @staticmethod
    def restore_backup(backup_file_path: str) -> bool:
        """Restore from a backup file (zip containing SQL and uploads, or plain SQL)."""
        try:
            # 1. Backup current DB before replacing
            current_backup = SettingsRepository.create_backup()
            if not current_backup:
                print("Failed to create backup before restore")
                return False

            import shutil
            import tempfile
            import zipfile
            import os
            import sqlite3

            db_path = "student_data.db"
            uploads_dir = "uploads"

            # Helper: restore DB from SQL file
            def restore_db_from_sql(sql_path):
                if os.path.exists(db_path):
                    os.remove(db_path)
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                with open(sql_path, "r", encoding="utf-8") as f:
                    sql_script = f.read()
                cursor.executescript(sql_script)
                conn.commit()
                conn.close()

            # Helper: restore uploads folder
            def restore_uploads_from_dir(src_uploads):
                if os.path.exists(uploads_dir):
                    shutil.rmtree(uploads_dir)
                shutil.copytree(src_uploads, uploads_dir)

            # Check if file is a zip (by magic number, not just extension)
            is_zip = False
            with open(backup_file_path, 'rb') as f:
                sig = f.read(4)
                if sig == b'PK\x03\x04':
                    is_zip = True

            if is_zip:
                with tempfile.TemporaryDirectory() as tmpdir:
                    with zipfile.ZipFile(backup_file_path, 'r') as zipf:
                        zipf.extractall(tmpdir)
                    # Find SQL file (should be only .sql in root of tmpdir)
                    sql_file = None
                    for fname in os.listdir(tmpdir):
                        if fname.endswith('.sql'):
                            sql_file = os.path.join(tmpdir, fname)
                            break
                    if not sql_file:
                        print("No SQL file found in backup zip!")
                        return False
                    restore_db_from_sql(sql_file)
                    # Restore uploads if present
                    extracted_uploads = os.path.join(tmpdir, 'uploads')
                    if os.path.exists(extracted_uploads):
                        restore_uploads_from_dir(extracted_uploads)
            else:
                # Not a zip, treat as plain SQL
                restore_db_from_sql(backup_file_path)
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
