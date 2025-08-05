import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

from enum import Enum

class Source(Enum):
    TW = "TW"
    CN = "CN"
    UK = "UK"
    HK = "HK"

def getCmpInfo(Cmp:str ="台灣積體電路製造股份有限公司", src:str = "TW") -> dict[str, str]:
    
    if src == Source.TW:
        return getTwCmpInfo(Cmp)
    elif src == Source.CN:
        pass
    elif src == Source.UK:
        pass
    elif src == Source.HK:
        pass
    else:
        raise ValueError(f"Unsupported source: {src}")
    


def getTwCmpInfo(Cmp:str) -> dict[str, str]:

    url = f"https://data.gcis.nat.gov.tw/od/data/api/6BBA2268-1367-4B42-9CCA-BC17499EBE8C?$format=xml&$filter=Company_Name like {Cmp} and Company_Status eq 01&$skip=0&$top=50"#https://top.qcc.com/"#https://finance.sina.com.cn/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36'
    }

    dic = {"CompanySource":"TW"}

    response = requests.get(url, headers=headers)
    xml_str = response.text

    root = ET.fromstring(xml_str)

    for row in root.findall('row'):
        for child in row:
            dic[child.tag] =  child.text

    return dic