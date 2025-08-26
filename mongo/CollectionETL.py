from pymongo import MongoClient
from config import mongoUri
from datetime import datetime

uri = mongoUri 

client = MongoClient(uri)

db = client["test_db"]
companies_processed = db["companies_processed"]
companies_org = db["companies_org"]

REQUIRED_FIELDS = [
    "companyRegisteredNumber",
    "businessType",
    "operationStartDate",
    "yearsInOperation",
    "annualProfit",
    "annualProfitDisclosed",
    "annualRevenue",
    "annualRevenueDisclosed",
    "businessAddress",
    "totalAssets",
    "totalAssetsDisclosed",
    "totalLiabilities",
    "totalLiabilitiesDisclosed",
    "violations",
    "violationsDetails",
    "askingPrice",
    "employeeRanges",
    "employees",
    "environmentalStatus",
    "environmentalStatusDetails",
    "equipmentList",
    "inventoryValue",
    "licenses",
    "reasonForSelling",
    "suppliersInfo",
    "taxDocs",
    "transitionSupport",
    "UpdateUser",
    "UpdateTime",
    "Validated"
]

for doc in companies_org.find({"Status": ""}):  # be consistent: use lowercase 'status'
    now = datetime.utcnow()

    # Copy all source fields except ids/status flags
    payload = {k: v for k, v in doc.items() if k not in ["_id", "Status"]}

    # ---- Build update document WITHOUT overlapping keys ----
    # $set: everything we actually have from source + lastProcessedAt
    set_fields = {**payload, "lastProcessedAt": now}

    # $setOnInsert: only the required fields that are MISSING in payload + firstProcessedAt
    insert_defaults = {"firstProcessedAt": now}
    for key in REQUIRED_FIELDS:
        if key not in payload:
            insert_defaults[key] = ""  # your requested blank default

    update_doc = {"$set": set_fields}
    # Only include $setOnInsert if there is at least one field to set on insert
    if len(insert_defaults) > 1:  # (besides firstProcessedAt)
        update_doc["$setOnInsert"] = insert_defaults

    # Upsert into destination (no conflicting paths now)
    companies_processed.update_one({"_id": doc["_id"]}, update_doc, upsert=True)

    # Mark as processed only if it really exists in destination
    if companies_processed.find_one({"_id": doc["_id"]}, projection={"_id": 1}):
        companies_org.update_one(
            {"_id": doc["_id"], "Status": ""},
            {"$set": {"Status": "P", "processedAt": now}},
        )