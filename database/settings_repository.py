import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, Optional

from .connection import get_db_connection


class SettingsRepository:
    @staticmethod
    def init_settings_table():
        """Initialize the settings table"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS institute_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                center_code TEXT DEFAULT '',
                address TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                email TEXT DEFAULT '',
                website TEXT DEFAULT '',
                logo TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Create trigger to update updated_at timestamp
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_institute_settings_timestamp
            AFTER UPDATE ON institute_settings
            BEGIN
                UPDATE institute_settings SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END;
            """
        )

        # Insert default settings if table is empty
        cursor.execute("SELECT COUNT(*) FROM institute_settings")
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.execute(
                """
                INSERT INTO institute_settings (name, center_code, address, phone, email, website)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("Your Institute Name", "", "", "", "", ""),
            )

        conn.commit()
        conn.close()

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
        """Create database backup"""
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
            return backup_path
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None

    @staticmethod
    def restore_backup(backup_file_path: str) -> bool:
        """Delete DB file and restore from SQL dump"""
        try:
            # 1. Backup current DB before replacing
            current_backup = SettingsRepository.create_backup()
            if not current_backup:
                print("Failed to create backup before restore")
                return False

            db_path = "student_data.db"
            if os.path.exists(db_path):
                os.remove(db_path)  # delete the old DB

            # 2. Create a fresh DB and restore
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            with open(backup_file_path, "r") as f:
                sql_script = f.read()

            cursor.executescript(sql_script)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
