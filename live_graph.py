"""
live_graph.py
--------------
A live-updating dashboard. Every few seconds, it re-reads employees.db
and redraws the bar chart + pie chart automatically - no need to close
and rerun the script every time you want to see the latest data.

Run this ALONGSIDE file_watcher.py, in its own terminal:
  Terminal 1: python file_watcher.py   (keeps the database synced with the text file)
  Terminal 2: python live_graph.py     (keeps this graph synced with the database)
"""

import sqlite3
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

DB_FILE = "employees.db"
REFRESH_SECONDS = 3   # how often the graph redraws itself


def get_department_stats():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT department, AVG(salary), COUNT(*)
        FROM employees
        GROUP BY department
        ORDER BY department
    ''')
    rows = cursor.fetchall()
    conn.close()

    departments = [row[0] for row in rows]
    avg_salaries = [row[1] for row in rows]
    headcounts = [row[2] for row in rows]
    return departments, avg_salaries, headcounts


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))


def update(frame):
    departments, avg_salaries, headcounts = get_department_stats()

    ax1.clear()
    ax1.bar(departments, avg_salaries, color="#4C72B0")
    ax1.set_title("Average Salary by Department")
    ax1.set_xlabel("Department")
    ax1.set_ylabel("Average Salary")
    ax1.tick_params(axis="x", rotation=30)

    ax2.clear()
    ax2.pie(headcounts, labels=departments, autopct="%1.0f%%", startangle=90)
    ax2.set_title("Headcount by Department")

    fig.suptitle("Employee Data (Live)", fontsize=14)
    fig.tight_layout()


if __name__ == "__main__":
    ani = FuncAnimation(fig, update, interval=REFRESH_SECONDS * 1000, cache_frame_data=False)
    plt.show()
