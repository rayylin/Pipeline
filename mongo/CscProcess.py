import pandas as pd
from pymongo import MongoClient
from config import mongoUri   # config.py must define: mongoUri = "mongodb+srv://..."

# MongoDB connection
uri = mongoUri
client = MongoClient(uri)
db = client["test_db"]
collection = db["companies_org"]

# Path to your CSV
csv_path = r"C:\Users\dwade\Desktop\Pipeline\mongo\CmpReg_TextilePlastics.csv"

# Header mapping: Chinese -> English
FIELD_MAP = {
    "統一編號": "companyRegisteredNumber",
    "公司名稱": "Company_Name",
    "負責人": "Responsible_Name",
    "公司地址": "businessAddress",
    "資本總額": "totalAssets",
    "實收資本額": "Paid-inCapital",
    "在境內營運資金": "OperatingFundsInTerritory",
    "公司狀態": "Company_Status_Desc",
    "產製日期": "UpdatedTime"
}

# --- Step 1: Read CSV ---
# If it’s actually comma-separated, just remove delimiter="\t"
df = pd.read_csv(csv_path, delimiter="\t", encoding="utf-8")

# --- Step 2: Rename columns ---
df.rename(columns=FIELD_MAP, inplace=True)

# --- Step 3: Convert numeric columns to int (optional) ---
for col in ["totalAssets", "Paid-inCapital", "OperatingFundsInTerritory"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")

# --- Step 4: Convert DataFrame to dicts and insert ---
docs = df.to_dict(orient="records")

if docs:
    collection.insert_many(docs)
    print(f"✅ Inserted {len(docs)} documents into {db.name}.{collection.name}")
else:
    print("⚠️ No documents to insert.")