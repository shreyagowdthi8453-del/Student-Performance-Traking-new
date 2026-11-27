import sqlite3

def create_table():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            usn TEXT,
            email TEXT,
            department TEXT,
            semester INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usn TEXT,
            subject TEXT,
            marks INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usn TEXT,
            total_classes INTEGER,
            attended_classes INTEGER
        )
    """)

    conn.commit()
    conn.close()

create_table()