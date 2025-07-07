import pandas as pd
from postgresql import execSelect, execSql
from config import connSqlServer

df = pd.read_csv(r'C:\\Users\\dwade\\Downloads\\aapl.csv')

print(df.head())


print(execSelect("""SELECT *
                      FROM [stock].[dbo].[StockPrice]""", "SqlServer"))