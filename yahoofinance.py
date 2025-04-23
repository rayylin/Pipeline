import yfinance as yf

# Choose the stock ticker (e.g., Apple)
ticker = 'AAPL'
stock = yf.Ticker(ticker)

# Fetch the cash flow statement
cashflow = stock.cashflow

# Show the cash flow statement
print("Cash Flow Statement:")
print(cashflow)



cashflow_transposed = cashflow.transpose()

print("\nTransposed Cash Flow Statement:")
print(cashflow_transposed)

print(cashflow_transposed.columns.values)