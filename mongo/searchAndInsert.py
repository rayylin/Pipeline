from pymongo import MongoClient
from datetime import datetime
import re
import requests  
from config import mongoUri
from enum import Enum
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

class Choice(Enum):
    HK = ("Company_HK_Original", ["Business Name", "Business Name(Chinese)", "brNo"])
    TW = ("Company_TW_Original", ["統一編號", "公司名稱"])
    # UK = "" future dev
    # CN = ""


def parse_choice(user_input: str) -> Choice:
    try:
        return Choice[user_input.upper()]
    except KeyError:
        raise ValueError("Invalid choice. Must be HK or TW")




client = MongoClient(mongoUri)
db = client["company_db"]


# ---- Existing official API function (your code, slightly reformatted) ----
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
            print("No company found in official API.")
            return None
    else:
        print(f"Official API error: {response.status_code}")
        return None

# ---- Helper: slugify name for URL, 
def slugify(name: str) -> str:
    # lower case
    slug = name.lower()
    # replace non-alphanumeric with hyphen
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    # strip hyphens at ends
    slug = slug.strip("-")
    return slug


def getTwCmpInfo(Cmp:str) -> dict[str, str]:

    url = f"https://data.gcis.nat.gov.tw/od/data/api/6BBA2268-1367-4B42-9CCA-BC17499EBE8C?$format=xml&$filter=Company_Name like {Cmp} and Company_Status eq 01&$skip=0&$top=50"#https://top.qcc.com/"#https://finance.sina.com.cn/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36'
    }

    dic = {"CompanySource":"TW",
           "Company_Name": Cmp,
           "Status": ""} 

    response = requests.get(url, headers=headers)
    xml_str = response.text

    root = ET.fromstring(xml_str)

    for row in root.findall('row'):
        for child in row:
            dic[child.tag] =  child.text

    dic["companyRegisteredNumber"] = dic.pop("Business_Accounting_NO")
    dic["businessAddress"] = dic.pop("Company_Location")
    dic["operationStartDate"] = dic.pop("Company_Setup_Date")

    return dic


def upsert_tw_company(collection, api_data: dict) -> bool:
    if not api_data:
        return False

    reg_no = api_data.get("companyRegisteredNumber")
    if not reg_no:
        raise ValueError("TW api_data missing companyRegisteredNumber (cannot upsert safely).")

    now = datetime.now(timezone.utc)

    filter_doc = {"companyRegisteredNumber": reg_no}

    update_doc = {
        "$set": {
            **api_data,
            "CompanySource": "TW",   # ensure consistent
            "updatedAt": now,
        },
        "$setOnInsert": {
            "createdAt": now,
        }
    }

    result = collection.update_one(filter_doc, update_doc, upsert=True)
    # True if inserted OR modified OR matched
    return (result.upserted_id is not None) or (result.modified_count > 0) or (result.matched_count > 0)


# ---- Main function: check DB, else call API and insert ----
def ensure_company_in_db(soruce: str, cmp_name_en: str, cmp_name_zh: str | None = None) -> bool:
    """
    Check if company exists in MongoDB.
    If yes, return True.
    If not, call official API, insert into DB if found, then return True.
    If API also has no record, return False.
    """

    choice = parse_choice(source)
    collection = db[choice.value[0]]  # collection name

    if source == "HK":
        # 1. Check if it exists in our Mongo database
        query = {
            "$or": [
                {"Business Name": cmp_name_en}
            ]
        }
        if cmp_name_zh:
            query["$or"].append({"Business Name(Chinese)": cmp_name_zh})

        existing = collection.find_one(query)
        if existing:
            # Already in DB
            return True

        # 2. Not found in DB → call official API by English name
        api_data = getHkCmpInfo(cmp_name_en)
        if not api_data:
            # Not found even in official API
            return False

        # 3. Map official API result to our DB schema
        # Sample official result:
        # {'Brn': '74668139',
        #  'Chinese_Company_Name': '匯豐數字科技控股集團有限公司',
        #  'English_Company_Name': 'HSBC Digital Technology Holding Group Co., Limited',
        #  'Address_of_Registered_Office': '香港 九龍旺角花園街2-16號 好景商業中心19樓12室',
        #  'Company_Type': 'Private company limited by shares',
        #  'Date_of_Incorporation': '05-12-2022',
        #  'Re-domiciliation_Date': None}

        english_name = api_data.get("English_Company_Name") or cmp_name_en
        chinese_name = api_data.get("Chinese_Company_Name") or cmp_name_zh
        br_no = api_data.get("Brn")

        # Build url similar to example:
        # "https://hongkong-corp.com/co/aerolink-hong-kong-limited"
        url = f"https://hongkong-corp.com/co/{slugify(english_name)}"

        now = datetime.utcnow()

        new_doc = {
            "url": url,
            "Business Name": english_name,
            "Business Name(Chinese)": chinese_name,
            # We don't get status from the API; assume live & unknown fields as in your example
            "Business Status": "仍注册 (Live)",
            "Business Type": api_data.get("Company_Type", "无/Unavailable"),
            "Date of Dissolution / Ceasing to Exist": "无/Unavailable",
            "Important Note": f"Added: {now:%Y-%m-%d %H:%M} Updated: {now:%Y-%m-%d %H:%M}",
            "Register of Charges": "无/Unavailable",
            "Registration Date": api_data.get("Date_of_Incorporation", "无/Unavailable"),
            "Remarks": "无/Unavailable",
            "Winding Up Mode": "无/Unavailable",
            "brNo": br_no,
            "createTime": now,
            "updateTime": now,
            "name": english_name,
        }

        # 4. Insert into MongoDB
        collection.insert_one(new_doc)
        return True
    elif source == "TW":
        query = {
            "$or": [
                {"公司名稱": cmp_name_en}
            ]
        }
        # no Eng Name for TW
        # if cmp_name_zh:
        #     query["$or"].append({"統一編號": cmp_name_zh})

        existing = collection.find_one(query)
        if existing:
            # Already in DB
            return True
        
        api_data = getTwCmpInfo(cmp_name_en)
        if not api_data:
            # Not found even in official API
            return False

       
        saved = upsert_tw_company(collection, api_data)
        return saved

# ---- Example usage ----
if __name__ == "__main__":
    # If company already exists in DB → True, no new insert
    # Else, it tries official API and inserts if found.

    source = "TW"

    exists = ensure_company_in_db(source, 
        cmp_name_en="威宏控股"
    )
    print("Exists or inserted:", exists)