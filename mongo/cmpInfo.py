import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

from enum import Enum

# Define four sources
class Source(Enum):
    TW = "TW"
    CN = "CN"
    UK = "UK"
    HK = "HK"


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


def getHkCmpInfo(cmp_name: str) -> dict[str, str] | None:
    url = "https://data.cr.gov.hk/cr/api/api/v1/api_builder/json/local/search"

    params = {
        "query[0][key1]": "Comp_name",
        "query[0][key2]": "begins_with",
        "query[0][key3]": cmp_name
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data and isinstance(data, list):
            return data[0]  # Safely return first dict
        else:
            print("No company found.")
            return None
    else:
        print(f"Error: {response.status_code}")
        return None

def getCmpInfo(Cmp:str ="台灣積體電路製造股份有限公司", src:str = "TW") -> dict[str, str]:
    try:
        source_enum = Source(src)
    except ValueError:
        raise ValueError(f"Invalid source: {src}")

    if source_enum == Source.TW:
        return getTwCmpInfo(Cmp)
    elif source_enum == Source.CN:
        pass
    elif source_enum == Source.UK:
        pass
    elif source_enum == Source.HK:
        return getHkCmpInfo(Cmp)
    else:
        raise ValueError(f"Unsupported source: {src}")
    




# We could use dispatch map if there are too many sources
source_dispatch = {
    Source.TW: getTwCmpInfo,
    Source.HK: getHkCmpInfo
}

def getCmpInfo1(Cmp: str = "", src: Source = Source.TW) -> dict[str, str]:
    try:
        return source_dispatch[src](Cmp)
    except KeyError:
        raise ValueError(f"Unsupported source: {src}")




    
    