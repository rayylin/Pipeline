from pymongo import MongoClient

# Connect to MongoDB (localhost:27017)
client = MongoClient("mongodb://localhost:27017/")

# Access (or create) database and collection
db = client["test_database"]
collection = db["test_collection"]

# Insert a document
insert_result = collection.insert_one({"name": "Alice", "age": 30})
print("Inserted ID:", insert_result.inserted_id)

# Find one document
document = collection.find_one({"name": "Alice"})
print("Found document:", document)

# Update a document
collection.update_one({"name": "Alice"}, {"$set": {"age": 31}})

# Find updated document
updated = collection.find_one({"name": "Alice"})
print("Updated document:", updated)

# Delete document
collection.delete_one({"name": "Alice"})

# Confirm deletion
deleted = collection.find_one({"name": "Alice"})
print("After deletion:", deleted)