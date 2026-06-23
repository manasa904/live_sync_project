# Live Text File → Database → Graph Sync

A real-time data pipeline built in Python. Edit a text file, save it —
the database updates automatically and the graph redraws itself within
seconds. No manual re-running of scripts required.

---

## What It Does

```
employees.txt  →  file_watcher.py  →  employees.db  →  live_graph.py  →  Chart window
  (you edit)       (detects save,       (SQLite           (redraws every
                    diffs & syncs)       database)          3 seconds)
```

The watcher uses **diff-based sync** — it compares the file against the
database and runs only the SQL statements needed:

| Change in file | SQL executed |
|---|---|
| New row added | `INSERT` for that row only |
| Existing row edited | `UPDATE` for that row only |
| Row deleted | `DELETE` for that row only |
| No change | Nothing — database left untouched |

This is more efficient than a full-table reload and reflects how real
ETL pipelines handle incremental changes.

---

## Project Structure

```
live_sync_project/
├── employees.txt       # Data source — 20 employee records in CSV format
├── setup_database.py   # Run once to create employees.db and the table
├── file_watcher.py     # Watches the file and diffs changes into the database
├── view_database.py    # Prints current database contents to the terminal
├── visualize_data.py   # One-time snapshot graph (bar chart + pie chart)
├── live_graph.py       # Auto-refreshing graph — redraws every 3 seconds
├── requirements.txt    # Python dependencies
└── .gitignore          # Excludes employees.db, *.png, venv/, __pycache__/
```

### File format — `employees.txt`

One record per line, five comma-separated fields:

```
id,name,department,salary,date_joined
1,John Smith,Engineering,75000,2021-03-15
```

Valid departments in the sample data: Engineering, Finance, HR, Marketing, Sales.

---

## Setup

### Prerequisites

- Python 3.8 or higher
- VS Code (recommended) or any terminal

### 1. Clone or unzip the project

```
cd live_sync_project
```

### 2. Create a virtual environment

```
python -m venv venv
```

Activate it:

```bash
# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

### 3. Install dependencies

```
pip install -r requirements.txt
```

This installs `watchdog` and `matplotlib`.

### 4. Create the database (run once only)

```
python setup_database.py
```

Expected output:

```
Database 'employees.db' is ready with table 'employees'.
```

---

## Running the Pipeline

Open **two terminals** in VS Code (click `+` in the terminal panel).
Activate the venv in both. Then:

**Terminal 1 — start the file watcher:**

```
python file_watcher.py
```

Expected output on startup:

```
Running initial sync...
  [INSERT] id=1  John Smith
  ...
  Done — 20 inserted, 0 updated, 0 deleted.

Watching 'employees.txt' for live changes.
```

**Terminal 2 — start the live graph:**

```
python live_graph.py
```

A chart window opens showing a bar chart (average salary by department)
and a pie chart (headcount by department). Leave this window open.

---

## Testing It

Open `employees.txt` in your editor and make any of these changes, then
press `Ctrl+S`:

**Edit a value** — change John Smith's salary from `75000` to `200000`:
```
1,John Smith,Engineering,200000,2021-03-15
```

**Add a new record** — append a line at the end:
```
21,Test User,HR,50000,2026-01-01
```

**Delete a record** — remove any line entirely and save.

After each save, Terminal 1 prints exactly which rows were inserted,
updated, or deleted. The chart window redraws within 3 seconds.

To verify the raw database at any point, open a third terminal and run:

```
python view_database.py
```

---

## One-Time Snapshot Graph

To generate a single graph image instead of the live window:

```
python visualize_data.py
```

This draws the same two charts and saves them as `employee_graph.png`
in the project folder.

---

## How the Diff Works

`file_watcher.py` uses the following logic on every file save:

```python
file_ids = set of IDs in the text file
db_ids   = set of IDs in the database

to_insert = file_ids - db_ids          # in file, not in db → INSERT
to_delete = db_ids - file_ids          # in db, not in file → DELETE
to_update = rows present in both       # where values differ → UPDATE
            where values differ
```

If nothing changed, the function exits immediately without touching the
database.

---

## Dependencies

| Package | Purpose |
|---|---|
| `watchdog` | File system event monitoring — detects when `employees.txt` is saved |
| `matplotlib` | Drawing the bar chart, pie chart, and live animation |

`sqlite3` is part of Python's standard library — no install needed.



## What Is Not Committed to Git

The `.gitignore` excludes:

- `employees.db` — generated at runtime by `setup_database.py`
- `*.png` — generated at runtime by `visualize_data.py`
- `venv/` — your local virtual environment
- `__pycache__/` — Python bytecode cache
