import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv(r'PatternAnalysis.csv')

print(df.head())

from statsmodels.tsa.seasonal import seasonal_decompose


df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
df.set_index('date', inplace=True)

df_motor_oil = df[df['Product_Name'] == 'Motor Oil']

ts = df_motor_oil['quantity'].asfreq('MS')  

result = seasonal_decompose(ts, model='additive', period=12)

result.plot()
plt.suptitle("Seasonal Decomposition of Motor Oil Sales", fontsize=14)
plt.tight_layout()
plt.show()