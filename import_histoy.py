import sqlite3
import re
import os
import glob

# -----------------------------
# CONFIGURATION (EDIT LOCALLY!!!!)
# -----------------------------

LOG_DIRECTORY = "/path/to/dsls/logs"  # <-- customize locally
LOG_PATTERN_FILE = "LicenseServer*.log"
DB_HISTORY = "history.db"  # append-only archive

# LOG REGEX Example

LOG_REGEX = re.compile(
    r"^(?P<timestamp>\\d{4}/\\d{2}/\\d{2}\\s\\d{2}:\\d{2}:\\d{2}:\\d{3}).*?"
    r"(?P<action>Grant|Detachment|TimeOut)!!"
    r"(?P<product>[^!]+)!"
    r"[^!]+![^!]+!"
    r"(?P<host>[^!]+).*?"
    r"(?P<user>[^!]+)!"
)

# IMPORT FUNCTION

def import_all_logs():
    print(f"Starting history import into {DB_HISTORY}")

    search_path = os.path.join(LOG_DIRECTORY, LOG_PATTERN_FILE)
    files = sorted(glob.glob(search_path), key=os.path.getmtime)

    conn = sqlite3.connect(DB_HISTORY)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS session_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            action TEXT,
            username TEXT,
            product_code TEXT,
            hostname TEXT
        )
        """
    )

    imported = 0

    for file_path in files:
        if os.path.getsize(file_path) < 1000:
            continue

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                match = LOG_REGEX.search(line)
                if not match:
                    continue

                data = match.groupdict()
                cur.execute(
                    "INSERT INTO session_history (timestamp, action, username, product_code, hostname) VALUES (?, ?, ?, ?, ?)",
                    (
                        data["timestamp"],
                        data["action"],
                        data["user"],
                        data["product"],
                        data["host"],
                    ),
                )
                imported += 1

    conn.commit()
    conn.close()
    print(f"Import completed: {imported} events stored")


if __name__ == "__main__":
    import_all_logs()
