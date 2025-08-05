from pymongo import MongoClient
from cmpInfo import getCmpInfo

# Connect to MongoDB (localhost:27017)
client = MongoClient("mongodb://localhost:27017/")

# Access (or create) database and collection
db = client["sai"]
collection = db["cmp_collection"]


# Get Company information
cmpName = "聯發科技股份有限公司"
cmpSrc = "TW"

#dic = getCmpInfo(cmpName, cmpSrc)


# Insert into mongo
#insert_result = collection.insert_one(dic)

# read from mongo
document = collection.find_one({"Company_Name": cmpName})
print("Found document:", document)

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


person = {
    "name": "蔡明介",
    "gender": "Male",
    "education_level": "Master's",
    "birth": "1950-06-15"
}

person_collection = db["person"]
person_collection.insert_one(person)

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
        "$unwind": "$person_info"  # optional: flatten the result
    }
]

results = list(collection.aggregate(pipeline))

for doc in results:
    print(doc)






