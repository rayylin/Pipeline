from pymongo import MongoClient, UpdateOne
from config import mongoUri
from hkc1 import Fetch_Page_url, ensure_indexes
from hkcPage import process_all_from_queue
import requests
import time

dic = {"A":8897, "B":7293, "C":14083, "D":4995, "E":6163, "F":7337, "G":10526,"H":26632}


USER_AGENT = "learning-scraper/0.1 (+your-email@example.com)"
DELAY_SECONDS = 0.1


# Shared session
session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})

# ---- Mongo bootstrap ----
uri = mongoUri
client = MongoClient(uri)
db = client["test_db"]
ensure_indexes(db)

for k, v in dic.items():
    for i in range(1, v):
        try:            
            Fetch_Page_url(k, i, session, db)
            time.sleep(DELAY_SECONDS)
            if i % 30 == 0:
                process_all_from_queue(max_docs = None, sleep_sec = 0.1)
        except Exception as e:
            print(f"Iteration {i} failed: {e}")
            continue


    