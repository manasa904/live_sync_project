"""
view_database.py
------------------
A quick helper to print out what's currently inside employees.db,
so you can confirm the sync worked without installing extra tools.
"""

import sqlite3

DB_FILE = "employees.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("SELECT * FROM employees ORDER BY id")
rows = cursor.fetchall()

print(f"{'ID':<5}{'Name':<20}{'Department':<15}{'Salary':<10}{'Date Joined':<12}")
print("-" * 62)
for row in rows:
    print(f"{row[0]:<5}{row[1]:<20}{row[2]:<15}{row[3]:<10}{row[4]:<12}")

print(f"\nTotal records: {len(rows)}")
conn.close()
