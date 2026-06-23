"""
visualize_data.py
-------------------
Reads the current contents of employees.db and draws two graphs:
  1. A bar chart of average salary per department
  2. A pie chart showing how many employees are in each department

Run this any time AFTER file_watcher.py has synced your latest changes,
to see an updated snapshot of the data as a graph.
"""

import sqlite3
import matplotlib.pyplot as plt

DB_FILE = "employees.db"


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


def draw_graphs():
    departments, avg_salaries, headcounts = get_department_stats()

    # Create one figure with two charts side by side
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # --- Bar chart: average salary per department ---
    ax1.bar(departments, avg_salaries, color="#4C72B0")
    ax1.set_title("Average Salary by Department")
    ax1.set_xlabel("Department")
    ax1.set_ylabel("Average Salary")
    ax1.tick_params(axis="x", rotation=30)

    # --- Pie chart: headcount distribution ---
    ax2.pie(headcounts, labels=departments, autopct="%1.0f%%", startangle=90)
    ax2.set_title("Headcount by Department")

    fig.suptitle("Employee Data Snapshot", fontsize=14)
    fig.tight_layout()

    # Save a copy to disk AND show it in a window
    fig.savefig("employee_graph.png", dpi=150)
    print("Saved chart as employee_graph.png")

    plt.show()


if __name__ == "__main__":
    draw_graphs()
