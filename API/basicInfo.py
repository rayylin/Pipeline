import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import polygonapi
from polygon import RESTClient


client = RESTClient(polygonapi)

details = client.get_ticker_details(
	"AAPL",
	)

print(type(details))
print(details.active)
print(details.address.city)