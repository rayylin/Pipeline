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
choice = parse_choice(source)

client = MongoClient(mongoUri)
db = client["company_db"]
collection = db[choice.value[0]]  # collection name

def search_business(keyword: str, limit: int = 5):
    pattern = re.escape(keyword)

    fields = choice.value[1]  # <-- HK/TW search fields list
    query = {
        "$or": [
            {field: {"$regex": pattern, "$options": "i"}}
            for field in fields
        ]
    }

    return list(collection.find(query).limit(limit))


# Search by English keyword
for doc in search_business("Ae"):
    print(doc.get("Business Name"), "|", doc.get("Business Name(Chinese)"), "|", doc.get("brNo"))

# Search by Chinese keyword
for doc in search_business("光"):
    print(doc.get("Business Name"), "|", doc.get("Business Name(Chinese)"), "|", doc.get("brNo"))