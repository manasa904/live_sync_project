"""
setup_database.py
------------------
Run this ONCE to create the database file and the table inside it.
SQLite is used here because it needs no server, no install, no password -
it's just a single file on your disk. Perfect for learning.
"""

import sqlite3

DB_FILE = "employees.db"


def create_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT,
            salary INTEGER,
            date_joined TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database '{DB_FILE}' is ready with table 'employees'.")


if __name__ == "__main__":
    create_database()
