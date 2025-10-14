# hkc_basic_info_only.py
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import urllib.robotparser as robotparser
from datetime import datetime, timezone
from typing import Dict, Optional

from pymongo import MongoClient, UpdateOne
from config import mongoUri

# -------------------- Config --------------------
BASE = "https://hongkong-corp.com"
USER_AGENT = "learning-scraper/0.1 (+your-email@example.com)"
TIMEOUT = 20
DELAY_SECONDS = 1.0  # polite pause between requests (kept for consistency)

# 👉 Set this to the *company detail* page you want to fetch
# Example: "https://hongkong-corp.com/co/agarwood-technology-limited"
TARGET_URL = "https://hongkong-corp.com/co/agarwood-technology-limited"
# Optional: if you already know the name you want to store alongside
TARGET_NAME = None  # e.g., "Agarwood Technology Limited"
# ------------------------------------------------


# ---------- Polite HTTP ----------
def allowed_to_fetch(base: str, user_agent: str, path: str) -> bool:
    robots_url = urljoin(base, "/robots.txt")
    rp = robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(user_agent, path)
    except Exception:
        print(f"Warning: could not read robots.txt at {robots_url}. Aborting by default.")
        return False


def fetch_html(url: str, session: requests.Session, timeout: int = TIMEOUT) -> str:
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


# ---------- Basic Information parsing ----------
BASIC_INFO_SECTION_TITLES = [
    "Basic Information", "Basic information",
    "基本資料", "公司基本資料", "公司資料"
]

CANON_KEYS = [
    "brNo",
    "Business Name",
    "Business Name(Chinese)",
    "Registration Date",
    "Business Status",
    "Business Type",
    "Remarks",
    "Winding Up Mode",
    "Date of Dissolution / Ceasing to Exist",
    "Register of Charges",
    "Important Note",
]

LABEL_MAP = {
    r"\b(BR|CR)\s*No\.?\b": "brNo",
    r"Business\s*Registration\s*(?:No|Number)\b": "brNo",
    r"公司(?:註冊|登記)?編號": "brNo",

    r"^Business\s*Name\b": "Business Name",
    r"^公司名稱$": "Business Name",

    r"Business\s*Name\s*\(Chinese\)": "Business Name(Chinese)",
    r"公司名稱（?中文）?$": "Business Name(Chinese)",
    r"中文名稱": "Business Name(Chinese)",

    r"^Registration\s*Date\b": "Registration Date",
    r"註冊日期": "Registration Date",

    r"^Business\s*Status\b": "Business Status",
    r"公司狀態|現況": "Business Status",

    r"^Business\s*Type\b": "Business Type",
    r"公司類別|公司類型": "Business Type",

    r"^Remarks?$": "Remarks",
    r"備註": "Remarks",

    r"^Winding\s*Up\s*Mode\b": "Winding Up Mode",
    r"清盤模式": "Winding Up Mode",

    r"Date\s*of\s*Dissolution\s*/\s*Ceasing\s*to\s*Exist": "Date of Dissolution / Ceasing to Exist",
    r"解散.*日期|註銷.*日期": "Date of Dissolution / Ceasing to Exist",

    r"^Register\s*of\s*Charges\b": "Register of Charges",
    r"押記登記冊": "Register of Charges",

    r"^Important\s*Note\b": "Important Note",
    r"重要提示|重要備註": "Important Note",
}
LABEL_PATTERNS = [(re.compile(p, re.IGNORECASE), key) for p, key in LABEL_MAP.items()]

def _normalize_label(raw: str) -> Optional[str]:
    label = " ".join(raw.replace("\xa0", " ").split()).strip().strip(":：")
    for rx, key in LABEL_PATTERNS:
        if rx.search(label):
            return key
    return None

def _clean_value(v: str) -> str:
    v = v.replace("\xa0", " ")
    v = re.sub(r"\s+", " ", v).strip()
    return v

def _find_basic_info_container(soup: BeautifulSoup):
    # Prefer a heading containing "Basic Information" (or Chinese equivalents)
    for hdr in soup.find_all(["h1","h2","h3","h4","h5"], string=True):
        txt = hdr.get_text(" ", strip=True)
        if any(t.lower() in txt.lower() for t in BASIC_INFO_SECTION_TITLES):
            sib = hdr.find_next(lambda tag: tag.name in ["table","dl","section","div"])
            if sib: return sib
            return hdr.parent if hdr.parent else hdr
    # Otherwise, return a likely container containing our labels
    for node in soup.find_all(["table","dl","section","div"]):
        txt = node.get_text(" ", strip=True)
        if any(re.search(p, txt, re.IGNORECASE) for p in LABEL_MAP.keys()):
            return node
    # Fallback: entire page
    return soup

def _pairs_from_table(table) -> Dict[str, str]:
    out = {}
    for tr in table.find_all("tr"):
        cells = tr.find_all(["th","td"])
        if len(cells) < 2: continue
        key = _normalize_label(cells[0].get_text(" ", strip=True))
        if not key: continue
        out[key] = _clean_value(cells[1].get_text(" ", strip=True))
    return out

def _pairs_from_dl(dl) -> Dict[str, str]:
    out = {}
    for dt in dl.find_all("dt"):
        dd = dt.find_next_sibling("dd")
        if not dd: continue
        key = _normalize_label(dt.get_text(" ", strip=True))
        if not key: continue
        out[key] = _clean_value(dd.get_text(" ", strip=True))
    return out

def _pairs_from_label_value_text(container) -> Dict[str, str]:
    out = {}
    for node in container.find_all(text=True):
        txt = str(node)
        if ":" in txt or "：" in txt:
            parts = re.split(r"[:：]", txt, maxsplit=1)
            if len(parts) != 2: continue
            key = _normalize_label(parts[0])
            if not key: continue
            val = _clean_value(parts[1])
            if val:
                out[key] = val
    return out

def parse_basic_info_from_html(html: str) -> Dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    container = _find_basic_info_container(soup)
    data: Dict[str, str] = {}

    table = container.find("table")
    if table:
        data.update(_pairs_from_table(table))
    dl = container.find("dl")
    if dl:
        data.update(_pairs_from_dl(dl))
    data.update(_pairs_from_label_value_text(container))

    return {k: data.get(k, "") for k in CANON_KEYS}

def fetch_company_basic_info(session: requests.Session, url: str) -> Dict[str, str]:
    path = urlparse(url).path
    if not allowed_to_fetch(BASE, USER_AGENT, path):
        return {k: "" for k in CANON_KEYS}
    html = fetch_html(url, session, timeout=TIMEOUT)
    return parse_basic_info_from_html(html)


# ---------- Mongo wiring ----------
def ensure_indexes(db) -> None:
    db["Company_Basic_Info"].create_index("url", unique=True)

def upsert_basic_info(db, url: str, name: Optional[str], info: Dict[str, str]):
    now = datetime.now(timezone.utc)
    doc = {
        "url": url,
        "name": name or info.get("Business Name", ""),
        **{k: info.get(k, "") for k in CANON_KEYS},
        "updateTime": now,
    }
    db["Company_Basic_Info"].update_one(
        {"url": url},
        {
            "$set": doc,
            "$setOnInsert": {"createTime": now},
        },
        upsert=True,
    )


# ---------- Main ----------
def main():
    if not TARGET_URL:
        raise SystemExit("Please set TARGET_URL to a company detail URL (e.g., https://hongkong-corp.com/co/xxxx).")

    # session
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    # mongo
    client = MongoClient(mongoUri)
    db = client["test_db"]
    ensure_indexes(db)

    # fetch & parse
    print(f"Fetching Basic Information from: {TARGET_URL}")
    info = fetch_company_basic_info(session, TARGET_URL)
    # store
    upsert_basic_info(db, TARGET_URL, TARGET_NAME, info)

    # show result
    print("Saved to Company_Basic_Info:")
    print(f"  url:  {TARGET_URL}")
    if TARGET_NAME:
        print(f"  name: {TARGET_NAME}")
    for k in CANON_KEYS:
        print(f"  {k}: {info.get(k, '')}")

    time.sleep(DELAY_SECONDS)

if __name__ == "__main__":
    main()
