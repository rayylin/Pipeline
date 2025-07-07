
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import polygonapi


import requests
from config import polygonapi  # or use os.getenv() if using .env

# Sample stock ticker
ticker = "AAPL"

# Endpoint: Previous close (works in free tier)
url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev?adjusted=true&apiKey={polygonapi}"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    if "results" in data:
        prev_close = data["results"][0]["c"]
        print(f"Previous close for {ticker}: ${prev_close}")
    else:
        print("No results found.")
else:
    print(f"Error {response.status_code}: {response.text}")




from polygon import RESTClient
from polygon.rest.models import (
    TickerNews,
)

client = RESTClient("b5UCMzdBDke3aeFqLkfakPjG2xQbJcoW")

ticker = "AAPL"

# List Aggregates (Bars)
aggs = []
for a in client.list_aggs(ticker=ticker, multiplier=1, timespan="minute", from_="2023-01-01", to="2023-06-13", limit=50000):
    aggs.append(a)

print(aggs)

# Get Last Trade
trade = client.get_last_trade(ticker=ticker)
print(trade)

# List Trades
trades = client.list_trades(ticker=ticker, timestamp="2022-01-04")
for trade in trades:
    print(trade)

# Get Last Quote
quote = client.get_last_quote(ticker=ticker)
print(quote)

# List Quotes
quotes = client.list_quotes(ticker=ticker, timestamp="2022-01-04")
for quote in quotes:
    print(quote)

