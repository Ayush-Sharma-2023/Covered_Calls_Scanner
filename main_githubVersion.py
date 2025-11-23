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

# st.subheader("About")

st.markdown("""
# About Covered Call Scanner

The **Covered Call Scanner** is a tool designed to help analyze potential **covered call** opportunities in the Indian stock market. Using the **Upstox API**, the app fetches live stock and option data from NSE, including stocks and call options for different expiries.

## Workflow

- **Data Collection:** Raw market data is fetched from Upstox for all relevant stocks and options.
- **Data Processing:** Using **Pandas**, the data is cleaned, filtered, and structured into data frames for easier analysis.
- **Option Selection:** For each stock, the first **out-of-the-money (OTM) call options** are identified for all available expiries.
- **Price and ROI Calculation:** Best bid and ask prices are used to calculate **effective investment** and potential **ROI** for each option.
- **Output:** The results are presented in an interactive **Streamlit dashboard** and saved as a JSON file (`deploy.json`) for further use.

This tool streamlines a complex multi-step process into a simple interface, allowing users to quickly scan options and evaluate potential returns, all in real-time.
""")
