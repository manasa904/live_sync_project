"""
file_watcher.py
----------------
Watches employees.txt for changes and syncs ONLY the changed rows
to employees.db using a diff-based approach.

How the diff works:
  1. Read the current file into a dict  { id -> (name, dept, salary, date) }
  2. Read the current database into a dict with the same shape
  3. Compare them:
       - id in file but NOT in db  → INSERT
       - id in both but values differ → UPDATE
       - id in db but NOT in file   → DELETE
  4. Run only those targeted SQL statements

This means editing one row out of 20 triggers exactly 1 UPDATE,
not a DELETE-all + 20 INSERTs like the old full-refresh approach.
"""

import sqlite3
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

TEXT_FILE = "employees.txt"
DB_FILE = "employees.db"


# ── Helpers ────────────────────────────────────────────────────────────────

def parse_file():
    """Read employees.txt and return {id: (name, dept, salary, date)}."""
    records = {}
    with open(TEXT_FILE, "r") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) != 5:
                print(f"  [SKIP] Line {line_number} has wrong number of columns: {line}")
                continue
            emp_id, name, department, salary, date_joined = parts
            try:
                records[int(emp_id)] = (
                    name.strip(),
                    department.strip(),
                    int(salary.strip()),
                    date_joined.strip()
                )
            except ValueError:
                print(f"  [SKIP] Line {line_number} has non-numeric id or salary: {line}")
    return records


def read_database():
    """Read employees table and return {id: (name, dept, salary, date)}."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, department, salary, date_joined FROM employees")
    rows = {row[0]: (row[1], row[2], row[3], row[4]) for row in cursor.fetchall()}
    conn.close()
    return rows


def sync_diff():
    """Diff file vs database and apply only the changes needed."""
    file_records = parse_file()
    db_records = read_database()

    file_ids = set(file_records.keys())
    db_ids = set(db_records.keys())

    to_insert = file_ids - db_ids                          # new rows
    to_delete = db_ids - file_ids                          # removed rows
    to_check  = file_ids & db_ids                          # might be updated
    to_update = {i for i in to_check if file_records[i] != db_records[i]}

    if not to_insert and not to_delete and not to_update:
        print("  No changes detected — database already up to date.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for emp_id in to_insert:
        name, dept, salary, date = file_records[emp_id]
        cursor.execute(
            "INSERT INTO employees (id, name, department, salary, date_joined) "
            "VALUES (?, ?, ?, ?, ?)",
            (emp_id, name, dept, salary, date)
        )
        print(f"  [INSERT] id={emp_id}  {name}")

    for emp_id in to_update:
        name, dept, salary, date = file_records[emp_id]
        cursor.execute(
            "UPDATE employees SET name=?, department=?, salary=?, date_joined=? "
            "WHERE id=?",
            (name, dept, salary, date, emp_id)
        )
        print(f"  [UPDATE] id={emp_id}  {name}")

    for emp_id in to_delete:
        cursor.execute("DELETE FROM employees WHERE id=?", (emp_id,))
        print(f"  [DELETE] id={emp_id}")

    conn.commit()
    conn.close()
    print(f"  Done — {len(to_insert)} inserted, {len(to_update)} updated, {len(to_delete)} deleted.")


# ── Watcher ────────────────────────────────────────────────────────────────

class TextFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(TEXT_FILE):
            print("\nChange detected in employees.txt → diffing...")
            sync_diff()


if __name__ == "__main__":
    print("Running initial sync...")
    sync_diff()

    print(f"\nWatching '{TEXT_FILE}' for live changes. Press Ctrl+C to stop.\n")
    handler = TextFileHandler()
    observer = Observer()
    observer.schedule(handler, path=".", recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopped watching.")
    observer.join()
