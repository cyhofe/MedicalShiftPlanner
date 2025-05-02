import sqlite3
from pathlib import Path

import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).parent.parent / "medical_shift_planner.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        role TEXT CHECK(role IN ('coordinator', 'local_manager', 'worker')) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT
    );

    CREATE TABLE IF NOT EXISTS shifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_id INTEGER NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        FOREIGN KEY(location_id) REFERENCES locations(id)
    );

    CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        shift_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(shift_id) REFERENCES shifts(id),
        UNIQUE(user_id, shift_id)
    );
    """)
    conn.commit()
    conn.close()
