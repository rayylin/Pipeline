from pymongo import MongoClient
from cmpInfo import getTwCmpInfo

# Connect to MongoDB (localhost:27017)
client = MongoClient("mongodb://localhost:27017/")

# Access (or create) database and collection
db = client["sai"]
collection = db["cmp_collection"]


dic = getTwCmpInfo("台灣積體電路製造股份有限公司")

insert_result = collection.insert_one(dic)

# Find one document
document = collection.find_one({"name": "Cecilia"})
print("Found document:", document)

# # Update a document
# collection.update_one({"name": "Alice"}, {"$set": {"age": 31}})

# # Find updated document
# updated = collection.find_one({"name": "Alice"})
# print("Updated document:", updated)

# # Delete document
# collection.delete_one({"name": "Alice"})

# # Confirm deletion
# deleted = collection.find_one({"name": "Alice"})
# print("After deletion:", deleted)