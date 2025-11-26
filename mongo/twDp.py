from pymongo import MongoClient
import csv
import os
from config import mongoUri
# ==== CONFIGURE THESE ====
csv_file_path_Head = r"C:\\Users\\dwade\\Downloads\\"
fileCollections = ["公司登記(依營業項目別)－電器批發業", "公司登記(依營業項目別)－布疋、衣著、鞋、帽、傘、服飾品零售業", "公司登記(依營業項目別)－化妝品零售業"
                   , "公司登記(依營業項目別)－日常用品零售業", "公司登記(依營業項目別)－汽、機車零件配備零售業", "公司登記(依營業項目別)－電器零售業", "公司登記(依營業項目別)－五金零售業"
                   , "公司登記(依營業項目別)－建材零售業", "公司登記(依營業項目別)－日常用品批發業"]
db_name = "company_db"  # no trailing space
collection_name = "company_Taiwan_Orginal"
# =========================


def normalize_str(v):
    if v is None:
        return ""
    return str(v).strip()


def extract_industry_from_filename(path):
    filename = os.path.basename(path)
    name_no_ext = os.path.splitext(filename)[0]
    # 全形破折號
    if "－" in name_no_ext:
        return name_no_ext.split("－", 1)[1].strip()
    return ""


def main():
    client = MongoClient(mongoUri)
    db = client[db_name]
    collection = db[collection_name]

    

    for file in fileCollections:

        csv_file_path = csv_file_path_Head + file + ".csv"

        industry_value = extract_industry_from_filename(csv_file_path)
        print("產業:", industry_value)

        # 先偵測分隔符
        with open(csv_file_path, "r", encoding="utf-8-sig") as f:
            sample = f.read(2048)
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample)
            delimiter = dialect.delimiter
            print("偵測到的分隔符:", repr(delimiter))

        # 再正式讀取
        with open(csv_file_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter=delimiter)

            # 標準化欄位名稱（避免含 BOM 或多餘空白）
            reader.fieldnames = [fn.strip().replace("\ufeff", "") for fn in reader.fieldnames]
            print("欄位名稱:", reader.fieldnames)

            docs = []
            for row in reader:

                # 正常化資料
                row_clean = {k.strip(): normalize_str(v) for k, v in row.items() if k}

                # 統一編號 → 8 碼
                uid_raw = row_clean.get("統一編號", "")
                uid_digits = "".join(ch for ch in uid_raw if ch.isdigit())
                uid_padded = uid_digits.zfill(8) if uid_digits else ""

                doc = {
                    "統一編號": uid_padded,
                    "公司名稱": row_clean.get("公司名稱", ""),
                    "負責人": row_clean.get("負責人", ""),
                    "公司地址": row_clean.get("公司地址", ""),
                    "資本總額": row_clean.get("資本總額", ""),
                    "實收資本額": row_clean.get("實收資本額", ""),
                    "在境內營運資金": row_clean.get("在境內營運資金", ""),
                    "公司狀態": row_clean.get("公司狀態", ""),
                    "產製日期": row_clean.get("產製日期", ""),
                    "產業": industry_value
                }

                docs.append(doc)

            if docs:
                result = collection.insert_many(docs)
                print(f"Inserted {len(result.inserted_ids)} docs.")
            else:
                print("CSV 無資料行或欄位錯誤")


if __name__ == "__main__":
    main()