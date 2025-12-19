import os
import sqlite3
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

LIVE_DB = os.getenv("LIVE_DB", "license_manager.db")
HISTORY_DB = os.getenv("HISTORY_DB", "history.db")

st.set_page_config(page_title="License Monitor", layout="wide")
st.title("License Monitor")

# ACTIVE SESSIONS

st.header("Active Sessions")
with sqlite3.connect(LIVE_DB) as conn:
    df_live = pd.read_sql("SELECT * FROM active_sessions", conn)

st.dataframe(df_live, use_container_width=True)

# HISTORY

st.header("License History")
with sqlite3.connect(HISTORY_DB) as conn:
    df_hist = pd.read_sql(
        "SELECT * FROM session_history ORDER BY timestamp DESC LIMIT 500",
        conn
    )

st.dataframe(df_hist, use_container_width=True)
