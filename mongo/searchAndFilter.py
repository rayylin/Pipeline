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




client = MongoClient(mongoUri)
db = client["company_db"]

source = "TW"
choice = parse_choice(source)
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


def print_business_docs(docs, fields):
    for doc in docs:
        values = [str(doc.get(field, "")) for field in fields]
        print(" | ".join(values))

# Search by English keyword
results = search_business("發")
print_business_docs(results, choice.value[1])


source = "HK"
choice = parse_choice(source)
collection = db[choice.value[0]]  # collection name

results = search_business("發")
print_business_docs(results, choice.value[1])