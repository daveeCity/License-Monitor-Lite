import os
import re
import glob
import sqlite3
from dotenv import load_dotenv

# CONFIGURATION (.env)

load_dotenv()

LOG_DIRECTORY = os.getenv("LOG_DIRECTORY", "/path/to/dsls/logs")
LOG_PATTERN_FILE = os.getenv("LOG_PATTERN_FILE", "LicenseServer*.log")
HISTORY_DB = os.getenv("HISTORY_DB", "history.db")

# SANITIZED LOG REGEX

LOG_REGEX = re.compile(
    r"^(?P<timestamp>\d{4}/\d{2}/\d{2}\s\d{2}:\d{2}:\d{2}:\d{3}).*?"
    r"(?P<action>Grant|Detachment|TimeOut)!!"
    r"(?P<product>[^!]+)!.*?"
    r"(?P<host>[^!]+).*?"
    r"(?P<user>[^!]+)!"
)

# IMPORT FUNCTION

def import_all_logs():
    search_path = os.path.join(LOG_DIRECTORY, LOG_PATTERN_FILE)
    files = sorted(glob.glob(search_path), key=os.path.getmtime)

    with sqlite3.connect(HISTORY_DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS session_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                action TEXT,
                username TEXT,
                product_code TEXT,
                hostname TEXT
            )
        """)

        imported = 0

        for file_path in files:
            if os.path.getsize(file_path) < 1000:
                continue

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    match = LOG_REGEX.search(line)
                    if not match:
                        continue

                    d = match.groupdict()
                    conn.execute(
                        "INSERT INTO session_history (timestamp, action, username, product_code, hostname) VALUES (?, ?, ?, ?, ?)",
                        (d["timestamp"], d["action"], d["user"], d["product"], d["host"])
                    )
                    imported += 1

    print(f"History import completed: {imported} events")

if __name__ == "__main__":
    import_all_logs()
