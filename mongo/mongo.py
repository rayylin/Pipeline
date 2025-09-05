from pymongo import MongoClient
from cmpInfo import getCmpInfo, getTwCmpInfo
from config import mongoUri


# Connect to MongoDB (localhost:27017)
uri = mongoUri 

client = MongoClient(uri)


# Access (or create) database and collection
db = client["sai"]
collection = db["cmp_collection"]


# Get Company information
cmpName = "威宏控股"#"台灣積體電路製造股份有限公司"#"聯發科技股份有限公司"
cmpSrc = "TW"

dic = getCmpInfo(cmpName, cmpSrc)


# Insert into mongo
insert_result = collection.insert_one(dic)

# read all from mongo
results = collection.find()

for doc in results:
    print(doc)

# read a specific cmp
document = collection.find_one({"Company_Name": cmpName})
print("Found document:", document)

# count with a filter
count = collection.count_documents({"Company_Setup_Date": "0760221"})
print(f"Companies: {count}")

# sum up a field
pipeline = [
    {
        "$addFields": {
            "capital_num": { "$toLong": "$Capital_Stock_Amount" } # Cast string to number using $toLong
        }
    },
    {
        "$group": {
            "_id": None,
            "total_capital": { "$sum": "$capital_num" }
        }
    }
]

result = list(collection.aggregate(pipeline))
print("Total capital stock:", result[0]["total_capital"])



# Update a document
collection.update_one({"Company_Name": cmpName}, {"$set": {"age": 32, "emp": 3222222}}) # if we want to update/add new item, just add another item in the dicionary
# notice that there should be only one $set; otherwise the later one would overwrite the previouse one.
collection.update_one({"Company_Name": cmpName}, {"$set": {"age": 32}, "$unset": {"emp": ""}}) # if want to delete a column, use unset
print("----------------Updated------------------")

# Find updated document
updated = collection.find_one({"Company_Name": cmpName})
print("Updated document:", updated)

# Delete document
# collection.delete_one({"Company_Name": cmpName})


# Create another collection to perform look up
# person = {
#     "name": "蔡明介",
#     "gender": "Male",
#     "education_level": "Master's",
#     "birth": "1950-06-15"
# }

# person_collection = db["person"]
# person_collection.insert_one(person)

# use lookup to join two collections
pipeline = [
    {
        "$lookup": {
            "from": "person",                    # target collection
            "localField": "Responsible_Name",    # field in company
            "foreignField": "name",              # field in person
            "as": "person_info"                  # result array field
        }
    },
    {
        "$unwind": "$person_info" 
    }
]

results = list(collection.aggregate(pipeline))

for doc in results:
    print(doc)






