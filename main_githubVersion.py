import streamlit as st
import pandas as pd
import json

# --- Load JSON ---
with open("deploy.json", "r") as f:
    content = json.load(f)

# Extract timestamp and data
current_time = content.get("last_fetched", "N/A")
data = content.get("data", [])

# Convert to DataFrame
df = pd.DataFrame(data)

# --- Streamlit App ---
st.set_page_config(layout="wide", page_title="Covered Call Viewer")

st.title("Covered Call Scanner")
# st.info("Test")
# st.context("TEST")
# st.sidebar

st.info(f"Data last fetched:   {current_time}")

st.dataframe(df, use_container_width=True)
