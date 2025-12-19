# DSLS License Monitor Lite

A lightweight, realtime dashboard for monitoring **Dassault Systèmes License Server (DSLS)** usage.

---

## Features

- Realtime parsing of DSLS license server logs
- Tracking of active license sessions
- Persistent historical archive (append-only)
- Web-based dashboard built with Streamlit
- Support for log rotation
- Environment-based configuration via `.env`

---

## Architecture

### Backend — `monitor.py`

- Runs continuously in the background
- Monitors a directory for rotating DSLS log files
- Parses log entries in real time using regular expressions
- Maintains a live database of active sessions
- Appends events to the historical database

### Batch Import — `import_history.py`

- One-time or manual execution
- Scans all existing DSLS log files
- Backfills the historical database
- Intended to be run before starting real-time monitoring

### Frontend — `dashboard.py`

- Built with **Streamlit**
- Displays active license sessions
- Provides a searchable historical view

### Databases

- **`license_manager.db`**  
  Contains *only currently active* license sessions

- **`history.db`**  
  Append-only archive containing:
  - License grants
  - Detachments
  - Timeouts

Both databases are created automatically at runtime and must not be committed.

---

## Requirements

- Linux server (Ubuntu / Debian recommended)
- Python **3.8+**
- Read access to the DSLS log directory

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/DaveeCity/License-Monitor-Lite.git
cd license-monitor
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

This project uses environment variables for configuration.

### 1. Create the `.env` file

```bash
cp .env.example .env
```

### 2. Edit `.env`

```env
LOG_DIRECTORY=/path/to/dsls/logs
LOG_PATTERN_FILE=LicenseServer*.log
POLL_INTERVAL=1.0
LIVE_DB=license_manager.db
HISTORY_DB=history.db
```

## Usage

### Import Historical Logs (Optional)

Run this once to populate the history database from existing log files:

```bash
python import_history.py
```

---

### Start the Log Monitor (Backend)

Runs continuously and processes new log entries:

```bash
nohup ./venv/bin/python monitor.py > monitor.log 2>&1 &
```

---

### Start the Dashboard (Frontend)

Starts the Streamlit web interface (default port: 8501):

```bash
nohup ./venv/bin/streamlit run dashboard.py --server.port 8501 > dashboard.log 2>&1 &
```

---

### Access the Dashboard

Open your browser and navigate to:

```
http://<SERVER_IP>:8501
```

---

## Maintenance & Troubleshooting

### Restarting the Services

```bash
pkill -f monitor.py
pkill -f streamlit
```

```bash
nohup ./venv/bin/python monitor.py > monitor.log 2>&1 &
nohup ./venv/bin/streamlit run dashboard.py --server.port 8501 > dashboard.log 2>&1 &
```

### Logs

- Backend errors: `monitor.log`
- Dashboard errors: `dashboard.log`

---

## Security & Privacy

This public version intentionally excludes:

- Real filesystem paths
- Hostnames and domains
- Company identifiers
- Real user or license data

Before deploying in a real environment, configure all paths and patterns locally via `.env`.

---
