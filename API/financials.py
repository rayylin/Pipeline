import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import polygonapi
from polygon import RESTClient

client = RESTClient(polygonapi)

financials = []
try:
    for f in client.vx.list_stock_financials(
	ticker="AAPL",
	order="desc",
	limit="10",
	sort="filing_date",
	):
        financials.append(f)
except:
    pass

try:
    
    print(len(financials))
    print(financials[0].company_name)

    sf = financials[0]
    for attr, value in sf.__dict__.items():
        print(f"{attr}: {value}")

    for attr, value in sf.financials.balance_sheet.__dict__.items():
        print(f"{attr}: {value}")

except:
    pass
