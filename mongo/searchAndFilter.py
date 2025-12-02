from pymongo import MongoClient
import re
from config import mongoUri



client = MongoClient(mongoUri)
db = client["test_db"]
collection = db["Company_HK_Orginal"]

def search_business(keyword: str, limit: int = 5):
    """
    Search 'Business Name' and 'Business Name(Chinese)' for the keyword.
    Returns up to `limit` matching documents.
    """
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
for doc in search_business("航"):
    print(doc.get("Business Name"), "|", doc.get("Business Name(Chinese)"))