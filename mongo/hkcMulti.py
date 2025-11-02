from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event, Thread
from pymongo import MongoClient
from config import mongoUri
from hkc1 import Fetch_Page_url, ensure_indexes
from hkcPage import process_all_from_queue
import requests
import time
import os

dic = {"M":8515, "N":4152, "O":2823, "P":67877, "Q":1087, "R":4957,"S":16566, "T":8400, "U":2565, "V":2291, "W":7585, "X":1620, "Y":4312, "Z":2228, "0":1086}

USER_AGENT = "learning-scraper/0.1 (+your-email@example.com)"
DELAY_SECONDS = 0.1                 # per-thread delay between requests
QUEUE_FLUSH_SECONDS = 5.0           # how often to drain your queue

# ---- Mongo bootstrap ----
client = MongoClient(mongoUri)
db = client["test_db"]
ensure_indexes(db)

def make_session():
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    return s

def worker_for_key(k: str, v: int, db):
    """Fetch all pages for key k sequentially (per key),
    but keys run in parallel across threads."""
    session = make_session()
    for i in range(1, v):
        try:
            Fetch_Page_url(k, i, session, db)
        except Exception as e:
            print(f"[{k}] Iteration {i} failed: {e}")
        # modest pacing; adjust if you have server-side rate limits
        time.sleep(DELAY_SECONDS)

def queue_flusher(stop_event: Event):
    """Flush your processing queue on a timer from a single thread."""
    while not stop_event.is_set():
        try:
            process_all_from_queue(max_docs=None, sleep_sec=0.1)
        except Exception as e:
            print(f"[queue] flush failed: {e}")
        # sleep between flushes
        stop_event.wait(QUEUE_FLUSH_SECONDS)

if __name__ == "__main__":
    # choose a sensible worker count: I/O-bound => more than cores is ok, but don't go crazy
    max_workers = min(8, (os.cpu_count() or 4) * 2)

    stop = Event()
    flusher_thread = Thread(target=queue_flusher, args=(stop,), daemon=True)
    flusher_thread.start()

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = [pool.submit(worker_for_key, k, v, db) for k, v in dic.items()]
            # Optional: progress / error aggregation
            for f in as_completed(futures):
                # will re-raise if an unhandled exception escaped worker
                f.result()
    finally:
        # stop queue flusher and flush one last time
        stop.set()
        flusher_thread.join(timeout=2.0)
        try:
            process_all_from_queue(max_docs=None, sleep_sec=0.1)
        except Exception as e:
            print(f"[queue] final flush failed: {e}")