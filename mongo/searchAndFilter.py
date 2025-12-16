from pymongo import MongoClient
import re
from config import mongoUri
from enum import Enum


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


source = "HK"
collectionName = parse_choice(source)


client = MongoClient(mongoUri)
db = client["company_db"]
collection = db[collectionName.value[0]]

def search_business(keyword: str, limit: int = 5):
    # Escape keyword so special regex chars (., *, ?, etc.) don't break the search
    pattern = re.escape(keyword)

    query = {
        "$or": [
            {"Business Name": {"$regex": pattern, "$options": "i"}},         
            {"Business Name(Chinese)": {"$regex": pattern, "$options": "i"}} 
        ]
    }

    results = list(collection.find(query).limit(limit))
    return results


# Search by English keyword
for doc in search_business("Ae"):
    print(doc.get("Business Name"), "|", doc.get("Business Name(Chinese)"))

# Search by Chinese keyword
for doc in search_business("光"):
    print(doc.get("Business Name"), "|", doc.get("Business Name(Chinese)"))