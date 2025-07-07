import pandas as pd
from postgresql import execSelect, execSql
from config import connSqlServer
from decimal import Decimal
from datetime import datetime

df = pd.read_csv(r'C:\\Users\\dwade\\Downloads\\aapl.csv')

print(df.head())


for idx, row in df.head().iterrows():
    
    query = f"""INSERT INTO [stock].[dbo].[StockPriceDaily] values (?,?, ?, ?, ?, ?, ?, ?)"""
    
    values = ("'AAPL'", 
        row['Date'],    
        str(Decimal(row['open'])),        
        str(Decimal(row['high'])),        
        str(Decimal(row['low'])),        
        str(Decimal(row['close'])),        
        str(Decimal(row['adjClose'])),        
        int(row['volume'].replace(",",""))                
    )

    
    
    print(query)

    execSql(query, values, "SqlServer")


print(execSelect("""SELECT *
                      FROM [stock].[dbo].[StockPriceDaily]""", "SqlServer"))