from polygon import RESTClient
from config import polygonapi  # or use os.getenv() if using .env

client = RESTClient(polygonapi)

request = client.get_daily_open_close_agg(
    "AAPL",
    "2025-07-09",
    adjusted="true",
)

print(request)