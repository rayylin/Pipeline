import re
import time
import threading
import argparse
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from urllib.parse import urlparse, urljoin
import urllib.robotparser as robotparser
from datetime import datetime, timezone
from typing import Dict, Optional

from pymongo import MongoClient
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from concurrent.futures import ThreadPoolExecutor, as_completed

# -------------------- Config --------------------
# You must provide mongoUri in config.py or set it here directly.
from config import mongoUri

BASE = "https://hongkong-corp.com"
USER_AGENT = "learning-scraper/0.1 (saaic111v5@sai.com)"
TIMEOUT = 22
DELAY_SECONDS = 0.1  # polite pacing; shared across threads
TARGET_URL = "https://hongkong-corp.com/co/agarwood-technology-limited"
TARGET_NAME = None
DB_NAME = "test_db"
# ------------------------------------------------

# ---------- Shared rate limiter (global across threads) ----------
_rate_lock = threading.Lock()
_next_allowed_at = 0.0  # monotonic seconds

def throttle():
    """Ensure at most 1 request per DELAY_SECONDS across all threads."""
    global _next_allowed_at
    now = time.monotonic()
    with _rate_lock:
        wait = max(0.0, _next_allowed_at - now)
        if wait > 0:
            time.sleep(wait)
        _next_allowed_at = max(now, _next_allowed_at) + DELAY_SECONDS

def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["HEAD", "GET", "OPTIONS"])
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=100, pool_maxsize=100)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s

# ---------- Polite HTTP ----------
def allowed_to_fetch(base: str, user_agent: str, path: str) -> bool:
    robots_url = urljoin(base, "/robots.txt")
    rp = robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url); rp.read()
        return rp.can_fetch(user_agent, path)
    except Exception:
        print(f"Warning: could not read robots.txt at {robots_url}. Aborting by default.")
        return False

def fetch_html(url: str, session: requests.Session, timeout: int = TIMEOUT) -> str:
    throttle()
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text

# ---------- Basic Information parsing ----------
BASIC_INFO_SECTION_TITLES = [
    "Basic Info","Basic Information","Basic information",
    "基本信息","基本資料","公司基本資料","公司資料"
]

CANON_KEYS = [
    "brNo","Business Name","Business Name(Chinese)","Registration Date",
    "Business Status","Business Type","Remarks","Winding Up Mode",
    "Date of Dissolution / Ceasing to Exist","Register of Charges","Important Note",
]

LABEL_MAP = {
    r"\b(BR|CR)\s*No\.?\b": "brNo",
    r"Business\s*Registration\s*(?:No|Number)\b": "brNo",
    r"公司(?:註冊|登記)?編號|商業登記(?:號|號碼)": "brNo",

    r"\bBusiness\s*Name\b": "Business Name",
    r"公司名稱|公司名称": "Business Name",

    r"Business\s*Name\s*\(Chinese\)": "Business Name(Chinese)",
    r"公司名稱（?中文）?|中文名稱|公司其他名稱|公司其他名称": "Business Name(Chinese)",

    r"\bRegistration\s*Date\b": "Registration Date",
    r"註冊日期|成立日期": "Registration Date",

    r"\bBusiness\s*Status\b": "Business Status",
    r"公司狀態|現況|公司現狀|公司狀態為|公司现况": "Business Status",

    r"\bBusiness\s*Type\b": "Business Type",
    r"公司類別|公司類型|公司类别|公司类型": "Business Type",

    r"\bRemarks?\b": "Remarks",
    r"備註|备注": "Remarks",

    r"\bWinding\s*Up\s*Mode\b": "Winding Up Mode",
    r"清盤模式|清盘模式": "Winding Up Mode",

    r"Date\s*of\s*Dissolution\s*/\s*Ceasing\s*to\s*Exist": "Date of Dissolution / Ceasing to Exist",
    r"已告解散.*日期|不再是.*日期|解散.*日期|註銷.*日期|注销.*日期": "Date of Dissolution / Ceasing to Exist",

    r"\bRegister\s*of\s*Charges\b": "Register of Charges",
    r"押記登記冊|押记登记册": "Register of Charges",

    r"\bImportant\s*Note\b": "Important Note",
    r"重要提示|重要備註|重要事項|重要事项": "Important Note",
}
LABEL_PATTERNS = [(re.compile(p, re.IGNORECASE), key) for p, key in LABEL_MAP.items()]
STOP_SECTION_TITLES = ["Name History","更名历史","文件索引","Document Index","Comments","Similar Names"]

def _normalize_label_text(s: str) -> Optional[str]:
    s = " ".join(s.replace("\xa0", " ").split()).strip().strip(":：")
    if re.search(r"Business\s*Name\s*\(Chinese\)", s, re.IGNORECASE):
        return "Business Name(Chinese)"
    if ("公司名稱" in s or "公司名称" in s) and re.search(r"\bBusiness\s*Name\b", s, re.IGNORECASE):
        return "Business Name"
    for rx, key in LABEL_PATTERNS:
        if rx.search(s):
            return key
    return None

def _text(node: Optional[Tag]) -> str:
    if node is None: return ""
    return " ".join(node.get_text(" ", strip=True).replace("\xa0"," ").split())

def _clean_value(v: str) -> str:
    v = v.replace("\xa0"," "); v = re.sub(r"\s+"," ", v).strip()
    return v.strip(")）]】>。：:、 ")

def _normalize_br_no(v: str) -> str:
    if not v: return ""
    cleaned = v.strip().strip(")）]】>。：:、 ")
    m = re.search(r"\b(\d{8})\b", cleaned)
    if m: return m.group(1)
    digits = re.sub(r"\D","", cleaned)
    return digits[:8] if len(digits) >= 8 else cleaned

def _is_section_header(tag: Tag) -> bool:
    if tag.name in ["h1","h2","h3","h4","h5","h6"]:
        t = _text(tag)
        return any(st.lower() in t.lower() for st in STOP_SECTION_TITLES)
    return False

def _find_basic_info_header(soup: BeautifulSoup) -> Optional[Tag]:
    for hdr in soup.find_all(["h1","h2","h3","h4","h5","h6"]):
        t = _text(hdr)
        if any(title.lower() in t.lower() for title in BASIC_INFO_SECTION_TITLES):
            return hdr
    return None

def _next_value_after(tag: Tag) -> str:
    for nxt in tag.find_all_next():
        if isinstance(nxt, Tag):
            if _is_section_header(nxt): break
            t = _text(nxt)
            if not t: continue
            if _normalize_label_text(t): continue
            return _clean_value(t)
        elif isinstance(nxt, NavigableString):
            s = str(nxt).strip()
            if s: return _clean_value(s)
    return ""

def parse_basic_info_from_html(html: str) -> Dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    data: Dict[str, str] = {k: "" for k in CANON_KEYS}

    header = _find_basic_info_header(soup)
    search_root = header if header is not None else soup

    table = search_root.find_next("table") if header else soup.find("table")
    if table:
        for tr in table.find_all("tr"):
            cells = tr.find_all(["th","td"])
            if len(cells) >= 2:
                key = _normalize_label_text(_text(cells[0]))
                if key: data[key] = _clean_value(_text(cells[1]))

    dl = search_root.find_next("dl") if header else soup.find("dl")
    if dl:
        for dt in dl.find_all("dt"):
            dd = dt.find_next_sibling("dd")
            if dd:
                key = _normalize_label_text(_text(dt))
                if key: data[key] = _clean_value(_text(dd))

    scan_start = header if header else soup
    for tag in scan_start.find_all_next(True):
        if header and _is_section_header(tag) and tag is not header: break
        t = _text(tag)
        key = _normalize_label_text(t)
        if not key: continue
        val = _next_value_after(tag)
        if not val: continue
        if key == "Business Type" and data[key]:
            if re.search(r"[A-Za-z]", val): data[key] = val
        else:
            data[key] = val

    data["brNo"] = _normalize_br_no(data.get("brNo",""))
    return data

def fetch_company_basic_info(session: requests.Session, url: str) -> Dict[str, str]:
    path = urlparse(url).path
    if not allowed_to_fetch(BASE, USER_AGENT, path):
        return {k: "" for k in CANON_KEYS}
    html = fetch_html(url, session, timeout=TIMEOUT)
    return parse_basic_info_from_html(html)

# ---------- Mongo helpers ----------
def ensure_indexes(db):
    db["Company_HK_Orginal"].create_index("url", unique=True)

def upsert_basic_info(db, url: str, name: Optional[str], info: dict):
    now = datetime.now(timezone.utc)
    doc = {"url": url, "name": name or info.get("Business Name",""), **info, "updateTime": now}
    db["Company_HK_Orginal"].update_one(
        {"url": url},
        {"$set": doc, "$setOnInsert": {"createTime": now}},
        upsert=True,
    )

def fetch_Page_Info_with_session(targetUrl: str, session: requests.Session):
    if not targetUrl:
        raise SystemExit("Please set TARGET_URL to a company detail URL")
    client = MongoClient(mongoUri)
    db = client[DB_NAME]
    ensure_indexes(db)
    info = fetch_company_basic_info(session, targetUrl)
    upsert_basic_info(db, targetUrl, TARGET_NAME, info)
    if TARGET_NAME:
        print(f"  name: {TARGET_NAME}")
    for k in CANON_KEYS:
        print(f"  {k}: {info.get(k, '')}")

# ---------- Mongo: URL queue (Company_Url_Dic) ----------
def ensure_indexes_queue(db):
    col = db["Company_Url_Dic"]
    col.create_index("url", unique=True)
    col.create_index("status")

def claim_one_pending(db) -> Optional[dict]:
    """
    Atomically claim ONE pending URL (status "" or missing).
    Sets status="IN_PROGRESS" to avoid double-processing.
    """
    from pymongo import ReturnDocument
    now = datetime.now(timezone.utc)
    return db["Company_Url_Dic"].find_one_and_update(
        {"$or": [{"status": ""}, {"status": {"$exists": False}}]},
        {"$set": {"status": "IN_PROGRESS", "updateTime": now}},
        sort=[("_id", 1)],
        return_document=ReturnDocument.AFTER,
    )

def mark_processed(db, _id, extra: dict | None = None):
    now = datetime.now(timezone.utc)
    update = {"$set": {"status": "P", "updateTime": now}}
    if extra: update["$set"].update(extra)
    db["Company_Url_Dic"].update_one({"_id": _id}, update)

def mark_error(db, _id, error_message: str):
    now = datetime.now(timezone.utc)
    db["Company_Url_Dic"].update_one(
        {"_id": _id},
        {"$set": {"status": "E", "error": error_message[:500], "updateTime": now}},
    )

# ---------- Single-item processor (for reference / fallback) ----------
def process_one_from_queue():
    client = MongoClient(mongoUri)
    db = client[DB_NAME]
    ensure_indexes_queue(db)
    doc = claim_one_pending(db)
    if not doc:
        return False
    _id = doc["_id"]; url = doc.get("url", ""); name = doc.get("name", "")
    print(f"Processing {_id} | {name} -> {url}")
    try:
        session = make_session()
        fetch_Page_Info_with_session(url, session)
        mark_processed(db, _id)
        print(f"Done & marked P: {_id}")
        return True
    except Exception as e:
        mark_error(db, _id, str(e))
        print(f"Error & marked E: {_id} | {e}")
        return True

def process_all_from_queue(max_docs: int | None = None, sleep_sec: float = 0.2):
    processed = 0
    while True:
        did = process_one_from_queue()
        if not did:
            print("Queue empty. All pending records processed.")
            break
        processed += 1
        if max_docs is not None and processed >= max_docs:
            print(f"Reached max_docs={max_docs}. Stopping.")
            break
        time.sleep(sleep_sec)
    print(f"Total processed this run: {processed}")

# ---------- Parallel workers ----------
def worker_loop(thread_no: int, idle_seconds: float):
    """
    Each worker repeatedly claims & processes items.
    Exits after the queue stays empty for ~idle_seconds.
    """
    client = MongoClient(mongoUri)  # MongoClient is thread-safe; per-thread is fine
    db = client[DB_NAME]
    ensure_indexes_queue(db)
    session = make_session()

    last_work = time.monotonic()
    while True:
        doc = claim_one_pending(db)
        if not doc:
            if time.monotonic() - last_work > idle_seconds:
                print(f"[T{thread_no}] idle > {idle_seconds}s, exiting.")
                return
            time.sleep(0.2)
            continue

        last_work = time.monotonic()
        _id = doc["_id"]; url = doc.get("url", ""); name = doc.get("name", "")
        print(f"[T{thread_no}] {_id} | {name} -> {url}")
        try:
            fetch_Page_Info_with_session(url, session)
            mark_processed(db, _id)
            print(f"[T{thread_no}] done P: {_id}")
        except Exception as e:
            mark_error(db, _id, str(e))
            print(f"[T{thread_no}] error E: {_id} | {e}")

def process_queue_parallel(workers: int = 8, idle_seconds: float = 5.0):
    print(f"Starting {workers} threads...")
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(worker_loop, i+1, idle_seconds) for i in range(workers)]
        for f in as_completed(futures):
            _ = f.result()
    print("All threads exited.")

# ---------- CLI ----------
def main():
    parser = argparse.ArgumentParser(description="Parallel HK company scraper queue worker")
    parser.add_argument("--workers", type=int, default=8, help="Number of worker threads")
    parser.add_argument("--idle", type=float, default=5.0, help="Seconds of idle before workers exit")
    parser.add_argument("--sequential", action="store_true", help="Run sequential fallback instead of parallel")
    parser.add_argument("--max_docs", type=int, default=None, help="Sequential: cap number of docs")
    parser.add_argument("--sleep", type=float, default=0.2, help="Sequential: sleep between docs")
    args = parser.parse_args()

    if args.sequential:
        process_all_from_queue(max_docs=args.max_docs, sleep_sec=args.sleep)
    else:
        process_queue_parallel(workers=args.workers, idle_seconds=args.idle)

if __name__ == "__main__":
    main()