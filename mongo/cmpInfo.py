import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


def getTwCmpInfo(Cmp:str):
    url = f"https://data.gcis.nat.gov.tw/od/data/api/6BBA2268-1367-4B42-9CCA-BC17499EBE8C?$format=xml&$filter=Company_Name like {Cmp} and Company_Status eq 01&$skip=0&$top=50"#https://top.qcc.com/"#https://finance.sina.com.cn/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    xml_str = response.text

    return xml_str