from pymongo import MongoClient
from config import mongoUri
from datetime import datetime

uri = mongoUri 

client = MongoClient(uri)

db = client["test_db"]
companies_processed = db["companies_processed"]
companies_org = db["companies_org"]

for doc in companies_org.find({"Status": ""}):
    # 1) Upsert into destination (insert or update)
    payload = {k: v for k, v in doc.items() if k not in ["_id", "status"]}  # copy all except _id/status
    companies_processed.update_one(
        {"_id": doc["_id"]},
        {
            "$set": {**payload, "lastProcessedAt": datetime.utcnow()},
            "$setOnInsert": {"firstProcessedAt": datetime.utcnow()},
        },
        upsert=True,
    )

    # 2) Only mark as processed if the record EXISTS in destination
    if companies_processed.find_one({"_id": doc["_id"]}, projection={"_id": 1}):
        companies_org.update_one(
            {"_id": doc["_id"], "status": ""},
            {"$set": {"status": "P", "processedAt": datetime.utcnow()}},
        )