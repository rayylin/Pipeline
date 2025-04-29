from fredapi import Fred
from config import fredApi

fred = Fred(api_key= fredApi)
rate = fred.get_series('FEDFUNDS')
print(rate.tail())

l = [# Interest Rates
     'FEDFUNDS' # Federal Funds Rate
     ,"MORTGAGE30US" # Mortgage rates
     ,"GS10"    # 10-Year Treasury

     # Inflation & Prices
     ,"CPIAUCSL" # CPI (Consumer Price Index)
     ,"PCE"      # PCE
     ,"PPIACO"   # Producer Price Index

     # Employment & Labor
     ,"UNRATE"    # Unemployment rate
     ,"PAYEMS"    # Nonfarm Payrolls

     # GDP & Growth	
     , "GDP" # Real GDP
     , "GDPC1" # Real Gross Domestic Product

     # Housing 
     ,"HOUST"     # New Housing Starts
     ,"CSUSHPISA" #Home Price Index
     ]

for i in l:
    rate = fred.get_series(i)
    print(rate.tail())
    print(rate.shape[0])


