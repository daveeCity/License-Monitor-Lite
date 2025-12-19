import os
import re
import time
import sqlite3
from pathlib import Path

# -----------------------------
# CONFIGURATION (EDIT LOCALLY!!)
# -----------------------------

LOG_DIRECTORY = "/path/to/dsls/logs"  # <-- customize locally
LOG_PATTERN_FILE = "LicenseServer*.log"
POLL_INTERVAL = 1.0  # seconds

LIVE_DB = "license_manager.db"
HISTORY_DB = "history.db"

# DATABASE SETUP

def init_live_db():
    conn = sqlite3.connect(LIVE_DB)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS active_sessions (
            user TEXT,
            feature TEXT,
            host TEXT,
            start_time TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def init_history_db():
    conn = sqlite3.connect(HISTORY_DB)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            timestamp TEXT,
            action TEXT,
            user TEXT,
            feature TEXT,
            host TEXT
        )
        """
    )
    conn.commit()
    conn.close()

# LOG PARSING

# Example patterns
GRANT_PATTERN = re.compile(r"GRANT (?P<feature>\S+) (?P<user>\S+)@(?P<host>\S+)")
TIMEOUT_PATTERN = re.compile(r"TIMEOUT (?P<feature>\S+) (?P<user>\S+)@(?P<host>\S+)")


def process_line(line: str):
    if match := GRANT_PATTERN.search(line):
        data = match.groupdict()
        add_session(data)
        add_history("GRANT", data)

    elif match := TIMEOUT_PATTERN.search(line):
        data = match.groupdict()
        remove_session(data)
        add_history("TIMEOUT", data)


# DATABASE OPERATIONS

def add_session(data):
    conn = sqlite3.connect(LIVE_DB)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO active_sessions VALUES (?, ?, ?, datetime('now'))",
        (data["user"], data["feature"], data["host"]),
    )
    conn.commit()
    conn.close()


def remove_session(data):
    conn = sqlite3.connect(LIVE_DB)
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM active_sessions WHERE user=? AND feature=? AND host=?",
        (data["user"], data["feature"], data["host"]),
    )
    conn.commit()
    conn.close()


def add_history(action, data):
    conn = sqlite3.connect(HISTORY_DB)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO history VALUES (datetime('now'), ?, ?, ?, ?)",
        (action, data["user"], data["feature"], data["host"]),
    )
    conn.commit()
    conn.close()


# MAIN LOOP

def follow(file):
    file.seek(0, os.SEEK_END)
    while True:
        line = file.readline()
        if not line:
            time.sleep(POLL_INTERVAL)
            continue
        yield line


def main():
    init_live_db()
    init_history_db()

    log_dir = Path(LOG_DIRECTORY)
    log_files = sorted(log_dir.glob(LOG_PATTERN_FILE))

    if not log_files:
        raise RuntimeError("No log files found")

    current_log = log_files[-1]

    with open(current_log, "r") as f:
        for line in follow(f):
            process_line(line)


if __name__ == "__main__":
    main()


