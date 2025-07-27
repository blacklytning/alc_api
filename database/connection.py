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

    set_admission_id_start()
    init_users_table()


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


def init_fee_payments_table():
    """Initialize the fee_payments table"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS fee_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            amount REAL NOT NULL CHECK(amount > 0),
            payment_date TEXT NOT NULL,
            payment_method TEXT NOT NULL CHECK(payment_method IN ('CASH', 'CARD', 'UPI', 'BANK_TRANSFER', 'CHEQUE')),
            transaction_id TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            late_fee REAL DEFAULT 0,
            discount REAL DEFAULT 0,
            handled_by TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES student_admissions (id) ON DELETE CASCADE
        )
        """
    )

    # Add discount column if it does not exist (migration for existing DBs)
    try:
        cursor.execute("ALTER TABLE fee_payments ADD COLUMN discount REAL DEFAULT 0")
    except Exception:
        pass  # Ignore if already exists

    # Create index for better query performance
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_fee_payments_student_id ON fee_payments(student_id);
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_fee_payments_date ON fee_payments(payment_date);
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
            INSERT INTO institute_settings (name, address, phone, email, website)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("EduManage", "", "", "", ""),
        )

    conn.commit()
    conn.close()


def set_admission_id_start(start=10001):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Only set if table exists and uses AUTOINCREMENT
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='student_admissions'")
    if cursor.fetchone():
        cursor.execute("SELECT seq FROM sqlite_sequence WHERE name='student_admissions'")
        row = cursor.fetchone()
        if not row or row[0] < start - 1:
            cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = 'student_admissions'", (start - 1,))
            conn.commit()
    conn.close()


def init_attendance_table():
    """Initialize the attendance table"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            batch_timing TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('PRESENT', 'ABSENT')),
            marked_by TEXT DEFAULT 'System User',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, date),
            FOREIGN KEY (student_id) REFERENCES student_admissions (id) ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_attendance_date_batch ON attendance(date, batch_timing)
        """
    )

    conn.commit()
    conn.close()


def init_documents_table():
    """Initialize the student_documents table"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS student_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            document_type TEXT NOT NULL CHECK(document_type IN (
                'SIGNED_ADMISSION_FORM', 'IDENTITY_PROOF', 'ADDRESS_PROOF', 
                'EDUCATIONAL_CERTIFICATE', 'OTHER'
            )),
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            mime_type TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'UPLOADED' CHECK(status IN ('UPLOADED', 'PENDING', 'REJECTED')),
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES student_admissions (id) ON DELETE CASCADE
        )
        """
    )

    # Create trigger to update updated_at timestamp
    cursor.execute(
        """
        CREATE TRIGGER IF NOT EXISTS update_documents_timestamp
        AFTER UPDATE ON student_documents
        BEGIN
            UPDATE student_documents SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        """
    )

    # Create indexes for better query performance
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_documents_student_id ON student_documents(student_id);
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_documents_type ON student_documents(document_type);
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_documents_status ON student_documents(status);
        """
    )

    conn.commit()
    conn.close()


def init_users_table():
    """Initialize the users table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            hashed_password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('staff', 'admin'))
        )
        """
    )
    conn.commit()
    conn.close()
