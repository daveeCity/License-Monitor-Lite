import sqlite3
import streamlit as st
import pandas as pd

LIVE_DB = "license_manager.db"
HISTORY_DB = "history.db"

st.set_page_config(page_title="License Monitor", layout="wide")
st.title("DSLS License Monitor")

# ACTIVE SESSIONS

st.header("Active Sessions")

conn = sqlite3.connect(LIVE_DB)
df_live = pd.read_sql_query("SELECT * FROM active_sessions", conn)
conn.close()

st.dataframe(df_live, use_container_width=True)

# HISTORY

st.header("License History")

conn = sqlite3.connect(HISTORY_DB)
df_hist = pd.read_sql_query(
    "SELECT * FROM history ORDER BY timestamp DESC LIMIT 500", conn
)
conn.close()

st.dataframe(df_hist, use_container_width=True)