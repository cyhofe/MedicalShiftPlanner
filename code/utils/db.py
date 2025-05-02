import sqlite3
from pathlib import Path
import bcrypt

# Define the path to the SQLite database file.
# It will be located in the root of your project directory.
DB_FILE = Path(__file__).parent.parent / "medical_shift_planner.db"

# Establish and return a connection to the database.
# Used internally by all database operations.
def get_connection():
    return sqlite3.connect(DB_FILE)

# --------------------------------------
# Password Hashing and Verification
# --------------------------------------

# Hash a plaintext password using bcrypt and return the hashed string.
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Compare a plaintext password with a previously hashed one.
# Returns True if the password is correct, otherwise False.
def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# --------------------------------------
# Database Initialization
# --------------------------------------

# Create all necessary database tables if they do not already exist.
# This function should be run once at application startup.
def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    -- Accounts table stores login-enabled users: admins, coordinators, and local managers
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('admin', 'coordinator', 'local_manager')) NOT NULL
    );

    -- Workers table stores individuals who can be assigned to shifts, but do not log in
    CREATE TABLE IF NOT EXISTS workers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        added_by INTEGER,
        FOREIGN KEY (added_by) REFERENCES accounts(id)
    );

    -- Locations where work shifts take place
    CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT
    );

    -- Time slots during which work occurs, assigned to specific locations
    CREATE TABLE IF NOT EXISTS shifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_id INTEGER NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        FOREIGN KEY(location_id) REFERENCES locations(id)
    );

    -- Optional: associate system users with shifts (if needed for permissions/visibility)
    CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        shift_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES accounts(id),
        FOREIGN KEY(shift_id) REFERENCES shifts(id),
        UNIQUE(user_id, shift_id)
    );

    -- Booking requests made by local managers to assign workers to shifts.
    -- Approved by coordinators. Can be canceled or rejected.
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        worker_id INTEGER NOT NULL,
        shift_id INTEGER NOT NULL,
        requested_by INTEGER NOT NULL,
        approved_by INTEGER,
        status TEXT CHECK(status IN ('pending', 'approved', 'rejected', 'cancelled')) NOT NULL DEFAULT 'pending',
        request_time TEXT DEFAULT CURRENT_TIMESTAMP,
        decision_time TEXT,
        FOREIGN KEY(worker_id) REFERENCES workers(id),
        FOREIGN KEY(shift_id) REFERENCES shifts(id),
        FOREIGN KEY(requested_by) REFERENCES accounts(id),
        FOREIGN KEY(approved_by) REFERENCES accounts(id),
        UNIQUE(worker_id, shift_id)
    );
    """)
    conn.commit()
    conn.close()

# --------------------------------------
# Account Management
# --------------------------------------

# Insert a new account (admin, coordinator, or local manager) into the database.
# Passwords are securely hashed before storage.
def add_account(name, username, email, password, role):
    conn = get_connection()
    cursor = conn.cursor()
    hashed = hash_password(password)
    cursor.execute("""
        INSERT INTO accounts (name, username, email, password, role)
        VALUES (?, ?, ?, ?, ?)
    """, (name, username, email, hashed, role))
    conn.commit()
    conn.close()

# Authenticate a user by checking their username and password.
# If successful, returns a dictionary with user ID, name, and role.
# Returns None if authentication fails.
def authenticate_account(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, password, role FROM accounts WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and check_password(password, user[2]):
        return {
            "id": user[0],
            "name": user[1],
            "role": user[3]
        }
    return None

# Ensure that at least one admin user exists in the system.
# If no admin is found, a default one is created with hardcoded credentials.
def ensure_admin_exists():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM accounts WHERE role = 'admin'")
    if cursor.fetchone()[0] == 0:
        hashed = hash_password("admin123")
        cursor.execute("""
            INSERT INTO accounts (name, username, email, password, role)
            VALUES ('Admin', 'admin', 'admin@example.com', ?, 'admin')
        """, (hashed,))
    conn.commit()
    conn.close()

# --------------------------------------
# Booking Management
# --------------------------------------

# Create a new booking request from a local manager for a specific worker and shift.
# The request will have 'pending' status until reviewed by a coordinator.
def create_booking(worker_id, shift_id, requested_by):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO bookings (worker_id, shift_id, requested_by)
        VALUES (?, ?, ?)
    """, (worker_id, shift_id, requested_by))
    conn.commit()
    conn.close()

# Update the status of a booking.
# The new status can be 'approved', 'rejected', or 'cancelled'.
# Optionally includes the ID of the coordinator approving or cancelling the booking.
def update_booking_status(booking_id, new_status, approver_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE bookings
        SET status = ?, approved_by = ?, decision_time = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (new_status, approver_id, booking_id))
    conn.commit()
    conn.close()
