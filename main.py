import requests
import json
import pandas as pd
import numpy as np
from getMarketQuote import getMarketQuote
import streamlit as st

st.set_page_config(layout="wide", page_title="Covered Call Scanner")

with open("json/data.json", "r") as f: 
    data = json.load(f)
with open("json/token.json", "r") as f: 
    token = json.load(f)["access_token"]

df = pd.DataFrame(data)

stocks_df = (df[ 
  (df["segment"] == "NSE_FO") & 
  (df["instrument_type"] == "FUT") &
  (df["asset_type"] == "EQUITY") 
]).drop_duplicates(subset="name")

expiries = stocks_df["expiry"].drop_duplicates().tolist()

stocks_df = stocks_df[["name", "lot_size", "asset_key"]]
stock_keys = stocks_df["asset_key"].to_list()

print(f"Fetching quotes for {len(stock_keys)} stocks...")
temp_data = getMarketQuote(token, stock_keys)
temp_data = list(temp_data.values())
temp_data_df = pd.json_normalize(temp_data)

temp_data_df["best_ask"] = temp_data_df["depth.sell"].apply(
    lambda x: x[0]["price"] if isinstance(x, list) and len(x) > 0 and "price" in x[0] else 0
)

temp_data_df = temp_data_df[["instrument_token", "symbol", "last_price", "best_ask"]]
temp_data_df = temp_data_df.rename(columns={
    "symbol": "stock_symbol",
    "last_price": "stock_ltp", 
    "best_ask": "stock_ask"
})

stocks_df = pd.merge(
    stocks_df, 
    temp_data_df, 
    left_on="asset_key", 
    right_on="instrument_token", 
    how="left"
)

print("\n--- Processing Expiries ---")

for exp in expiries:
    formatted_exp_date = pd.to_datetime(exp, unit="ms").strftime("%Y-%m-%d")
    print(f"Processing Expiry: {formatted_exp_date}")
    
    call_keys_map = [] 

    for index, row in stocks_df.iterrows():
        key = row['asset_key']
        
        stock_ask = row.get('stock_ask', 0)
        stock_ltp = row.get('stock_ltp', 0)
        ref_price = stock_ask if stock_ask > 0 else stock_ltp
        
        if ref_price == 0: continue 

        options_subset = df[ 
            (df["expiry"] == exp) &
            (df["segment"] == "NSE_FO") &
            (df["instrument_type"] == "CE") &
            (df["asset_key"] == key)
        ]

        options_subset = options_subset[options_subset["strike_price"] > ref_price].sort_values(by="strike_price")

        if not options_subset.empty:
            target_option = options_subset.iloc[0]
            call_keys_map.append({
                "asset_key": key,
                "instrument_key": target_option["instrument_key"]
            })
    
    if not call_keys_map:
        print(f"  -> No options found for {formatted_exp_date}")
        continue

    print(f"  -> Fetching quotes for {len(call_keys_map)} options...")
    
    api_keys = [item['instrument_key'] for item in call_keys_map]
    
    try:
        call_data = getMarketQuote(token, api_keys)
        call_data_list = list(call_data.values())
        
        if not call_data_list: continue

        call_df = pd.json_normalize(call_data_list)
        
        def get_option_price(row):
            if "depth.buy" in row and isinstance(row["depth.buy"], list) and len(row["depth.buy"]) > 0:
                return row["depth.buy"][0].get("price", 0)
            
            return 0

        call_df["option_price"] = call_df.apply(get_option_price, axis=1)
        
        prices_df = call_df[["instrument_token", "option_price"]]
        keys_map_df = pd.DataFrame(call_keys_map)

        final_expiry_data = pd.merge(keys_map_df, prices_df, left_on="instrument_key", right_on="instrument_token")
        
        final_expiry_data = final_expiry_data.rename(columns={"option_price": formatted_exp_date})
        final_expiry_data = final_expiry_data[["asset_key", formatted_exp_date]]

        stocks_df = pd.merge(stocks_df, final_expiry_data, on="asset_key", how="left")

    except Exception as e:
        print(f"  -> Error processing expiry {formatted_exp_date}: {e}")
        continue



print("\n--- Calculating ROI & Investment ---")

stocks_df["effective_price"] = np.where(
    stocks_df["stock_ask"] > 0, 
    stocks_df["stock_ask"], 
    stocks_df["stock_ltp"]
)

stocks_df["min_investment"] = stocks_df["lot_size"] * stocks_df["effective_price"]

date_cols = [col for col in stocks_df.columns if "-" in str(col) and col[0].isdigit()]

for col in date_cols:
    roi_col = f"ROI_{col}"
    
    stocks_df[col] = stocks_df[col].fillna(0)
    
    stocks_df[roi_col] = np.where(
        stocks_df["effective_price"] > 0,
        (stocks_df[col] / stocks_df["effective_price"]) * 100,
        0
    )
    stocks_df[roi_col] = stocks_df[roi_col].round(2)

stocks_df = stocks_df.sort_values(by="min_investment", ascending=True).reset_index(drop=True)

base_cols = ["name", "lot_size", "min_investment", "stock_ltp", "stock_ask"]
roi_cols = [f"ROI_{d}" for d in date_cols]
price_cols = date_cols

final_view = stocks_df[base_cols + price_cols + roi_cols]
current_time = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

output_json = {
    "last_fetched": current_time,
    "data": final_view.to_dict(orient="records")
}

with open("deploy.json", "w") as f:
    json.dump(output_json, f, indent=2)

print("final_view with timestamp saved to deploy.json")
print("PAGE IS READY TO VIEW")

st.title("COVERED CALL SCANNER")
st.write("Data Last fetched:", current_time)
st.dataframe(final_view, use_container_width=True)