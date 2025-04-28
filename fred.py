from fredapi import Fred
from config import fredApi

fred = Fred(api_key= fredApi)
rate = fred.get_series('FEDFUNDS')
print(rate.tail())