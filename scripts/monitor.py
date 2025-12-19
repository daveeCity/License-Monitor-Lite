import os
import re
import time
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# CONFIGURATION (.env)

load_dotenv()

LOG_DIRECTORY = os.getenv("LOG_DIRECTORY", "/path/to/dsls/logs")
LOG_PATTERN_FILE = os.getenv("LOG_PATTERN_FILE", "LicenseServer*.log")
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "1.0"))

LIVE_DB = os.getenv("LIVE_DB", "license_manager.db")
HISTORY_DB = os.getenv("HISTORY_DB", "history.db")

# DATABASE SETUP

def init_live_db():
    with sqlite3.connect(LIVE_DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS active_sessions (
                user TEXT,
                feature TEXT,
                host TEXT,
                start_time TEXT
            )
        """)

def init_history_db():
    with sqlite3.connect(HISTORY_DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                timestamp TEXT,
                action TEXT,
                user TEXT,
                feature TEXT,
                host TEXT
            )
        """)

# LOG PARSING

GRANT_PATTERN = re.compile(
    r"GRANT\s+(?P<feature>\S+)\s+(?P<user>\S+)@(?P<host>\S+)"
)
TIMEOUT_PATTERN = re.compile(
    r"TIMEOUT\s+(?P<feature>\S+)\s+(?P<user>\S+)@(?P<host>\S+)"
)

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
    with sqlite3.connect(LIVE_DB) as conn:
        conn.execute(
            "INSERT INTO active_sessions VALUES (?, ?, ?, datetime('now'))",
            (data["user"], data["feature"], data["host"])
        )

def remove_session(data):
    with sqlite3.connect(LIVE_DB) as conn:
        conn.execute(
            "DELETE FROM active_sessions WHERE user=? AND feature=? AND host=?",
            (data["user"], data["feature"], data["host"])
        )

def add_history(action, data):
    with sqlite3.connect(HISTORY_DB) as conn:
        conn.execute(
            "INSERT INTO history VALUES (datetime('now'), ?, ?, ?, ?)",
            (action, data["user"], data["feature"], data["host"])
        )

# FILE FOLLOWER

def follow(file):
    file.seek(0, os.SEEK_END)
    while True:
        line = file.readline()
        if not line:
            time.sleep(POLL_INTERVAL)
            continue
        yield line

# MAIN

def main():
    init_live_db()
    init_history_db()

    log_dir = Path(LOG_DIRECTORY)
    log_files = sorted(log_dir.glob(LOG_PATTERN_FILE))

    if not log_files:
        raise RuntimeError("No log files found")

    current_log = log_files[-1]

    with open(current_log, "r", encoding="utf-8", errors="ignore") as f:
        for line in follow(f):
            process_line(line)

if __name__ == "__main__":
    main()
