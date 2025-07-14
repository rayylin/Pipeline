
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import polygonapi


import requests
from config import polygonapi  # or use os.getenv() if using .env

from polygon import RESTClient
import datetime



def GetLatestDaily(ticker:str):


    client = RESTClient(polygonapi)

    today = LastOpenDate = datetime.datetime.now()
    weekday = today.strftime("%w")

    if weekday in ("0","6"): # Saturdat, Sunday
        LastOpenDate  = today +  datetime.timedelta(days=-2) if weekday == 0 else today +  datetime.timedelta(days=-1) # if weekday in ("0","6") else today

    request = client.get_daily_open_close_agg(
        ticker,
        f"{LastOpenDate.strftime("%Y-%m-%d")}",
        adjusted="true",
    )

    return request

if __name__ ==  '__main__':
    tick = "AAPL"
    req = GetLatestDaily(tick)

    print(f"close:{req.close} : , high:{req.high} : , low:{req.low} : , open:{req.open} : , volume:{req.volume} : ,")

    

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




# from polygon import RESTClient
# from polygon.rest.models import (
#     TickerNews,
# )


# client = RESTClient(polygonapi)

# ticker = "AAPL"

# # List Aggregates (Bars)
# aggs = []
# for a in client.list_aggs(ticker=ticker, multiplier=1, timespan="minute", from_="2023-01-01", to="2023-06-13", limit=50000):
#     aggs.append(a)

# print(aggs)

# # Get Last Trade
# trade = client.get_last_trade(ticker=ticker)
# print(trade)

# # List Trades
# trades = client.list_trades(ticker=ticker, timestamp="2022-01-04")
# for trade in trades:
#     print(trade)

# # Get Last Quote
# quote = client.get_last_quote(ticker=ticker)
# print(quote)

# # List Quotes
# quotes = client.list_quotes(ticker=ticker, timestamp="2022-01-04")
# for quote in quotes:
#     print(quote)



