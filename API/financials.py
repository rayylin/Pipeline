from polygon import RESTClient
import datetime


import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import polygonapi


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
    