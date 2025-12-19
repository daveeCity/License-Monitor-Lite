# License-Monitor-Lite

A lightweight, realtime dashboard for monitoring **License Server** usage.

---

## Features

* Realtime parsing of license server logs
* Detection of active user sessions
* Persistent session history
* Web-based dashboard for visualization
* Automatic handling of log rotation

---

## Architecture

### Backend — `monitor.py`

* Runs continuously in the background
* Monitors a directory for rotating log files
* Parses log entries in real time using regular expressions
* Updates local SQLite databases

### Frontend — `dashboard.py`

* Built with **Streamlit**
* Displays active license sessions
* Provides historical usage views

### Databases

* **`license_manager.db`**
  Contains *only currently active* license sessions (live state)

* **`history.db`**
  Append-only archive storing:

  * License grants
  * Detachments
  * Timeouts
    This database is never truncated and is used for historical analysis

---

## Installation

### Prerequisites

* Linux server (Ubuntu / Debian recommended)
* Python **3.8+**
* Read access to the log directory

---

### Setup

#### 1. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

All environment specific data **must be customized locally**.

Open `monitor.py` and configure the variables at the top of the file:

```python
# Path to the directory containing DSLS logs
LOG_DIRECTORY = "/path/to/dsls/logs"

# Pattern used to match DSLS log files
LOG_PATTERN_FILE = "LicenseServer*.log"
```

## Usage

### 1. Start the Log Monitor (Backend)

Runs continuously and processes log updates.

```bash
nohup ./venv/bin/python monitor.py > monitor.log 2>&1 &
```

### 2. Start the Dashboard (Frontend)

Launches the Streamlit web interface (default port: `8501`).

```bash
nohup ./venv/bin/streamlit run dashboard.py --server.port 8501 > dashboard.log 2>&1 &
```

### 3. Access the Dashboard

Open a browser and navigate to:

```
http://<SERVER_IP>:8501
```

---

## Maintenance & Troubleshooting

### Restarting the System

If the server reboots or the application stops:

```bash
pkill -f monitor.py
pkill -f streamlit
```

```bash
cd ~/license-monitor
nohup ./venv/bin/python monitor.py > monitor.log 2>&1 &
nohup ./venv/bin/streamlit run dashboard.py --server.port 8501 > dashboard.log 2>&1 &
```

### Logs

* Backend errors → `monitor.log`
* Dashboard errors → `dashboard.log`

---

## Repository Setup

```bash
git clone https://github.com/YOUR_USERNAME/license-monitor.git
cd license-monitor
```

---

DSLS and Dassault Systèmes are trademarks of their respective owners.
