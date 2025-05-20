import yfinance as yf
import time

for i in range(3):
    try:
        # Choose the stock ticker (e.g., Apple)
        ticker = 'AAPL'
        stock = yf.Ticker(ticker)



        info = stock.info
        # Print selected info
        print("Company Name:", info.get("longName"))
        print("Industry:", info.get("industry"))
        print("Sector:", info.get("sector"))
        print("Website:", info.get("website"))
        print("Country:", info.get("country"))
        print("Full-time Employees:", info.get("fullTimeEmployees"))
        print("Summary:", info.get("longBusinessSummary"))
        print("Summary:", info.get("calendar"))
    except:
        print("Rate Limit")
        time.sleep(4)


# Fetch the cash flow statement
# cashflow = stock.cashflow

# # Show the cash flow statement
# print("Cash Flow Statement:")
# print(cashflow)



# cashflow_transposed = cashflow.transpose()

# print("\nTransposed Cash Flow Statement:")
# print(cashflow_transposed)

# print(cashflow_transposed.columns.values)