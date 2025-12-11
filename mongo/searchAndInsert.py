from pymongo import MongoClient
from datetime import datetime
import re
import requests  # you already use this

# ---- Mongo connection (you already have this) ----
mongoUri = "YOUR_MONGO_njURhIdd_HERE"
client = MongoClient(mongoUri)
db = client["test_db"]
collection = db["Company_HK_Orginal"]

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

# ---- Helper: slugify name for URL, similar to your example URL ----
def slugify(name: str) -> str:
    # lower case
    slug = name.lower()
    # replace non-alphanumeric with hyphen
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    # strip hyphens at ends
    slug = slug.strip("-")
    return slug

# ---- Main function: check DB, else call API and insert ----
def ensure_company_in_db(
    cmp_name_en: str,
    cmp_name_zh: str | None = None
) -> bool:
    """
    Check if company exists in MongoDB.
    If yes, return True.
    If not, call official API, insert into DB if found, then return True.
    If API also has no record, return False.
    """

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

# ---- Example usage ----
if __name__ == "__main__":
    # If company already exists in DB → True, no new insert
    # Else, it tries official API and inserts if found.
    exists = ensure_company_in_db(
        cmp_name_en="HSBC Digital Technology Holding Group Co., Limited",
        cmp_name_zh="匯豐數字科技控股集團有限公司"
    )
    print("Exists or inserted:", exists)