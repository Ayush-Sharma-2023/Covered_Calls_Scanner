import requests
def getMarketQuote(token, keys):
  if (type(keys) == list):
    keys = ",".join(keys)

  url = f'https://api.upstox.com/v2/market-quote/quotes?instrument_key={keys}'
  headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': f'Bearer {token}'
  }

  response = requests.get(url, headers=headers)
  data = response.json()
  data = data["data"]
  return data

