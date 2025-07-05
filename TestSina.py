# -*- coding: utf-8 -*-
import requests
import re
import pandas as pd

Maxpage = 1
urlhead = "https://finance.sina.com.cn/stock/hkstock/ggscyd/2025-07-05/doc-infeknpv0201536.shtml"
# "http://stock.finance.sina.com.cn/fundInfo/api/openapi.php/CaihuiFundInfoService.getNav?callback=jQuery1112039651495097167233_1509076629050&symbol=000311&datefrom=&dateto=&page="

data = []

# Get data from Sina
for i in range(Maxpage):
    url = urlhead + str(i+1)
    html = requests.get(url).content
    print(html)
    data = data + re.findall(u'\{"fbrq.*?"\}',str(html))
    
# Transform Data to pandas
Time = ['']*len(data)
JJJZ = ['']*len(data)
LJJZ = ['']*len(data)

for i in range(len(data)):
    dataArray = data[i].split('"')
    Time[i] = pd.to_datetime(dataArray[3][0:10])
    JJJZ[i] = float(dataArray[7][0:10])
    LJJZ[i] = float(dataArray[11][0:10])
    
df = pd.DataFrame({'Date' : Time,
                    'JJJZ' : JJJZ,
                    'LJJZ' : LJJZ})
    
df = df.sort_values(by='Date').set_index('Date')
df.plot()
