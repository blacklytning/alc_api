import sqlite3

DATABASE_FILE = "student_data.db"


def init_database():
    """Initialize the SQLite database and create tables if they don't exist"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS student_enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            middle_name TEXT,
            last_name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            gender TEXT NOT NULL,
            marital_status TEXT NOT NULL,
            mother_tongue TEXT NOT NULL,
            aadhar_number TEXT NOT NULL,
            correspondence_address TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            district TEXT NOT NULL,
            mobile_number TEXT NOT NULL,
            alternate_mobile_number TEXT,
            category TEXT NOT NULL,
            educational_qualification TEXT NOT NULL,
            course_name TEXT NOT NULL,
            timing TEXT NOT NULL,
            handled_by TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS student_admissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            middle_name TEXT,
            last_name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            gender TEXT NOT NULL,
            marital_status TEXT NOT NULL,
            mother_tongue TEXT NOT NULL,
            aadhar_number TEXT NOT NULL,
            correspondence_address TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL,
            district TEXT NOT NULL,
            mobile_number TEXT NOT NULL,
            alternate_mobile_number TEXT,
            category TEXT NOT NULL,
            educational_qualification TEXT NOT NULL,
            course_name TEXT NOT NULL,
            timing TEXT NOT NULL,
            certificate_name TEXT NOT NULL,
            referred_by TEXT,
            photo_filename TEXT,
            signature_filename TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DATABASE_FILE)


def init_courses_table():
    """Initialize the courses table"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL UNIQUE,
            fees INTEGER NOT NULL CHECK(fees > 0),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Create trigger to update updated_at timestamp
    cursor.execute(
        """
        CREATE TRIGGER IF NOT EXISTS update_courses_timestamp
        AFTER UPDATE ON courses
        BEGIN
            UPDATE courses SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        """
    )

    # Insert default courses if table is empty
    cursor.execute("SELECT COUNT(*) FROM courses")
    count = cursor.fetchone()[0]

    if count == 0:
        default_courses = [
            ("MS-CIT", 2500),
            ("ADVANCE TALLY - CIT", 3500),
            ("ADVANCE TALLY - KLIC", 3000),
            ("ADVANCE EXCEL - CIT", 2000),
            ("ENGLISH TYPING - MKCL", 1500),
            ("ENGLISH TYPING - CIT", 1800),
            ("MARATHI TYPING - MKCL", 1500),
            ("DTP - CIT", 2200),
            ("IT - KLIC", 4000),
            ("KLIC DIPLOMA", 5000),
        ]

        cursor.executemany(
            "INSERT INTO courses (course_name, fees) VALUES (?, ?)", default_courses
        )

    conn.commit()
    conn.close()


def init_followups_table():
    """Initialize the followups table"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS followups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enquiry_id INTEGER NOT NULL,
            followup_date TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('PENDING', 'INTERESTED', 'NOT_INTERESTED', 'ADMITTED')),
            notes TEXT DEFAULT '',
            next_followup_date TEXT,
            handled_by TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (enquiry_id) REFERENCES student_enquiries (id) ON DELETE CASCADE
        )
        """
    )

    # Create trigger to update updated_at timestamp
    cursor.execute(
        """
        CREATE TRIGGER IF NOT EXISTS update_followups_timestamp
        AFTER UPDATE ON followups
        BEGIN
            UPDATE followups SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        """
    )

    # Create index for better query performance
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_followups_enquiry_id ON followups(enquiry_id);
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_followups_next_date ON followups(next_followup_date);
        """
    )

    conn.commit()
    conn.close()


def init_settings_table():
    """Initialize the institute settings table"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS institute_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
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
            INSERT INTO institute_settings (name, address, phone, email, website)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("Your Institute Name", "", "", "", ""),
        )

    conn.commit()
    conn.close()
