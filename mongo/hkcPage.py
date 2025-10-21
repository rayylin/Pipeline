# hkc_basic_info_to_original.py
import re
import time
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from urllib.parse import urlparse, urljoin
import urllib.robotparser as robotparser
from datetime import datetime, timezone
from typing import Dict, Optional

from pymongo import MongoClient
from config import mongoUri

# -------------------- Config --------------------
BASE = "https://hongkong-corp.com"
USER_AGENT = "learning-scraper/0.1 (+your-email@example.com)"
TIMEOUT = 20
DELAY_SECONDS = 1.0

TARGET_URL = "https://hongkong-corp.com/co/agarwood-technology-limited"
TARGET_NAME = None
# ------------------------------------------------

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
    r"^Business\s*Name\b": "Business Name",
    r"^公司名稱$": "Business Name",
    r"Business\s*Name\s*\(Chinese\)": "Business Name(Chinese)",
    r"公司名稱（?中文）?$|中文名稱|公司其他名稱": "Business Name(Chinese)",
    r"^Registration\s*Date\b": "Registration Date",
    r"註冊日期|成立日期": "Registration Date",
    r"^Business\s*Status\b": "Business Status",
    r"公司狀態|現況|公司現狀|公司狀態為|公司现况": "Business Status",
    r"^Business\s*Type\b": "Business Type",
    r"公司類別|公司類型|公司类别|公司类型": "Business Type",
    r"^Remarks?$": "Remarks",
    r"備註|备注": "Remarks",
    r"^Winding\s*Up\s*Mode\b": "Winding Up Mode",
    r"清盤模式|清盘模式": "Winding Up Mode",
    r"Date\s*of\s*Dissolution\s*/\s*Ceasing\s*to\s*Exist": "Date of Dissolution / Ceasing to Exist",
    r"已告解散.*日期|不再是.*日期|解散.*日期|註銷.*日期|注销.*日期": "Date of Dissolution / Ceasing to Exist",
    r"^Register\s*of\s*Charges\b": "Register of Charges",
    r"押記登記冊|押记登记册": "Register of Charges",
    r"^Important\s*Note\b": "Important Note",
    r"重要提示|重要備註|重要事項|重要事项": "Important Note",
}
LABEL_PATTERNS = [(re.compile(p, re.IGNORECASE), key) for p, key in LABEL_MAP.items()]
STOP_SECTION_TITLES = ["Name History","更名历史","文件索引","Document Index","Comments","Similar Names"]

def _normalize_label_text(s: str) -> Optional[str]:
    s = " ".join(s.replace("\xa0"," ").split()).strip().strip(":：")
    for rx, key in LABEL_PATTERNS:
        if rx.search(s): return key
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

# ---------- Main ----------
def main():
    if not TARGET_URL:
        raise SystemExit("Please set TARGET_URL to a company detail URL.")
    session = requests.Session(); session.headers.update({"User-Agent": USER_AGENT})
    client = MongoClient(mongoUri); 
    db = client["test_db"]; ensure_indexes(db)

    print(f"Fetching Basic Information from: {TARGET_URL}")
    info = fetch_company_basic_info(session, TARGET_URL)
    upsert_basic_info(db, TARGET_URL, TARGET_NAME, info)

    print("Saved to Company_HK_Orginal:")
    print(f"  url:  {TARGET_URL}")
    if TARGET_NAME: print(f"  name: {TARGET_NAME}")
    for k in CANON_KEYS: print(f"  {k}: {info.get(k, '')}")
    time.sleep(DELAY_SECONDS)

if __name__ == "__main__":
    main()
