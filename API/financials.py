from polygon import RESTClient
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import polygonapi
client = RESTClient(polygonapi)

request = client.get_daily_open_close_agg(
    "TSLA",
    "2025-07-09",
    adjusted="true",
)

print(request)