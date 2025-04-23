from postgresql import execSql
from sqlCommand import CreateCashflow, createStockPrice
from alphavantage import fetch_data

execSql(CreateCashflow)

execSql(createStockPrice)

df = fetch_data("AAPL")

for i in df.tail():
    print(i)
