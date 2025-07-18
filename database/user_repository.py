import sqlite3
from typing import Optional
from database.connection import DATABASE_FILE, get_db_connection
from models import User

# Get user by username
def get_user_by_username(username: str) -> Optional[User]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, hashed_password, role FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(id=row[0], username=row[1], role=row[3]), row[2]  # Return User (no password), and hashed_password
    return None, None

# Create new user
def create_user(username: str, hashed_password: str, role: str) -> User:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, hashed_password, role) VALUES (?, ?, ?)",
        (username, hashed_password, role)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return User(id=user_id, username=username, role=role)

def user_count() -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count 