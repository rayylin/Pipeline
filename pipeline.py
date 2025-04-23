from postgresql import execSql, execSelect
from sqlCommand import CreateCashflow, createStockPrice
from alphavantage import fetch_data
import pandas as pd
from io import StringIO

execSql(CreateCashflow)
execSql(createStockPrice)



symbol = "SNOW"
df = fetch_data(symbol)



# data = """datetime,open,high,low,close,volume,moving_avg
# 2025-04-22 19:59:00,143.95,143.9500,143.9500,143.9500,10.0,
# 2025-04-22 19:58:00,143.81,143.8100,143.6000,143.6000,95.0,
# 2025-04-22 19:56:00,143.87,143.8700,143.8700,143.8700,100.0,
# 2025-04-22 19:55:00,143.88,143.8800,143.8800,143.8800,15.0,
# 2025-04-22 19:54:00,143.71,143.7100,143.7100,143.7100,20.0,143.80200
# 2025-04-22 18:00:00,143.39,143.5000,143.3500,143.3500,128.0,143.23000
# 2025-04-22 17:59:00,143.35,143.4000,143.3500,143.4000,30.0,143.31000
# 2025-04-22 17:58:00,143.36,143.3900,143.3500,143.3900,742.0,143.29000
# 2025-04-22 17:57:00,143.20,143.3991,143.2000,143.3600,318.0,143.28200
# """

# df = pd.read_csv(StringIO(data), parse_dates=["datetime"])
# df.set_index("datetime", inplace=True)

# print(df)

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