import requests
import pandas as pd

def fetch_data(symbol='SNOW', **kwargs):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey=xx'
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame.from_dict(data['Time Series (1min)'], orient='index')
    df.index = pd.to_datetime(df.index)
    df.columns = ['open', 'high', 'low', 'close', 'volume']
    df = df.astype(float)
    df['moving_avg'] = df['close'].rolling(window=5).mean()
    # Store result in XCom
    # kwargs['ti'].xcom_push(key='fetched_df', value=df.to_json())
    return df
    
def transform_data(df):
    df = df.sort_index()
    df['moving_avg'] = df['close'].rolling(window=5).mean()
    df['anomaly'] = abs(df['close'] - df['moving_avg']) > 2 * df['close'].std()
    print(df.tail())  # For testing/logging purpose

df = fetch_data()
print(df)
print("---------------------")
print(transform_data(df))