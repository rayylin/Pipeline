from postgresql import execSql, execSelect
from sqlCommand import CreateCashflow, createStockPrice
from alphavantage import fetch_data
import pandas as pd
from io import StringIO

execSql(CreateCashflow)
execSql(createStockPrice)



symbol = "TSLA"

df = fetch_data(symbol)



rows = execSelect("select * from stockPrice")
print(rows)

for idx, row in df.tail().iterrows():
    
    query = f"""INSERT INTO stockPrice values ('{symbol}','{idx.to_pydatetime()}','{row['open']}','{row['high']}','{row['low']}','{row['close']}','{row['volume']}')
                ON CONFLICT (stock_id, date) 
                DO UPDATE SET
                    open = EXCLUDED.open,
                    high = EXCLUDED.high,
                    low = EXCLUDED.low,
                    close = EXCLUDED.close,
                    volume = EXCLUDED.volume;
    
    """
    print(query)

    execSql(query)

    # print(f"Date: {idx.date()}, Time: {idx.time()}, Open: {row['open']}")