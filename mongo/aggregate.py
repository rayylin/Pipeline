from pymongo import MongoClient, ASCENDING

# 0) Connect
client = MongoClient("mongodb://localhost:27017/")
db = client["sai"]

# --- CLEAN SLATE FOR DEMO (optional) ---
db.s1.drop()
db.s2.drop()
db.d1.drop()


s1_docs = [
    {"company": "TSMC", "source": "TW", "revenue": 100, "note": "from s1"},
    {"company": "MediaTec", "source": "TW", "revenue": 80,  "note": "from s1"},
    {"company": "ASUS", "source": "TW", "revenue": 60,  "note": "from s2"}
]

s2_docs = [
    {"company": "TSMC", "source": "TW", "revenue": 105, "note": "from s2 (newer)"},
    {"company": "ASUS", "source": "TW", "revenue": 60,  "note": "from s2"},
]

db.s1.insert_many(s1_docs)
db.s2.insert_many(s2_docs)

# Helpful index on d1's merge key for performance
db.d1.create_index([("company", ASCENDING)], unique=True)

# 2) Aggregation: s1 union s2 → merge into d1 on "company"
pipeline = [
    # shape/keep only the fields you want to persist in d1
    {"$project": {"company": 1, "source": 1, "revenue": 1, "note": 1, "_id": 0}},
    {
        "$unionWith": {
            "coll": "s2",
            "pipeline": [
                {"$project": {"company": 1, "source": 1, "revenue": 1, "note": 1, "_id": 0}}
            ],
        }
    },
    {
        "$merge": {
            "into": "d1",
            "on": "company",            # natural key; change to your own unique key if needed
            "whenMatched": "merge",     # updates existing docs
            "whenNotMatched": "insert"  # inserts new docs
        }
    }
]

# run the pipeline from s1 (it will pull s2 via $unionWith)
list(db.s1.aggregate(pipeline, allowDiskUse=True))

# 3) Show result
print("Documents in d1:")
for doc in db.d1.find({}, {"_id": 0}).sort("company", ASCENDING):
    print(doc)

