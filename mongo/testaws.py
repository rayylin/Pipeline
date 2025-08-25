from pymongo import MongoClient
from config import mongoUri

uri = mongoUri 

client = MongoClient(uri)

db = client["test_db"]
collection = db["companies_org"]

s= """Company Name: 台灣積體電路製造股份有限公司
Business_Accounting_NO: 22099131
Company_Name: 台灣積體電路製造股份有限公司
Company_Status: 01
Company_Status_Desc: 核准設立
Capital_Stock_Amount: 280500000000
Paid_In_Capital_Amount: 259326155210
Responsible_Name: 魏哲家
Register_Organization: 05
Register_Organization_Desc: 國家科學及技術委員會新竹科學園區管理局
Company_Location: 新竹科學園區新竹市力行六路8號
Company_Setup_Date: 0760221
Change_Of_Approval_Data: 1140805""".split("\n")

company_data = l = {k: v for k, v in (i.split(":") for i in s)}

# Insert one document
insert_result = collection.insert_one(company_data)
print("Inserted document ID:", insert_result.inserted_id)