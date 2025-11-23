# Covered Call Scanner

A Python & Streamlit application that scans NSE options and calculates potential ROI for covered calls. The app fetches live stock and option quotes, identifies out-of-the-money call options, and computes ROI based on stock price and option bid.  

---

## Features

- Fetches real-time stock and option quotes from NSE.  
- Identifies Out-of-The-Money (OTM) Call options for each expiry.  
- Calculates minimum investment and ROI for each option.  
- Saves results to a local JSON file (`deploy.json`) for further use.  
- Interactive Streamlit dashboard to view the data.  

---

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/covered-call-scanner.git
cd covered-call-scanner


