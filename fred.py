from fredapi import Fred
from config import fredApi

fred = Fred(api_key= fredApi)
rate = fred.get_series('FEDFUNDS')
print(rate.tail())

l = ["UNRATE"  # Unemployment rate
     ,"PAYEMS" # Nonfarm Payrolls
     ,'FEDFUNDS']

for i in l:
    rate = fred.get_series(i)
    print(rate.tail())
    print(rate.shape[0])


