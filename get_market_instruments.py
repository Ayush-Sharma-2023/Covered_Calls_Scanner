import requests
import gzip
import json
from io import BytesIO

url= "https://assets.upstox.com/market-quote/instruments/exchange/complete.json.gz"


response = requests.get(url)
response.raise_for_status()

with gzip.GzipFile(fileobj=BytesIO(response.content)) as gz:
  data = json.load(gz)

with open("json/data.json", "w", encoding="utf-8") as f:
  json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Saved {len(data)} instruments added to json.data")