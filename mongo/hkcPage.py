import re
from typing import Dict, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests

# --- add to your constants if you want ---
BASIC_INFO_SECTION_TITLES = [
    "Basic Information", "Basic information",
    "基本資料", "公司基本資料", "公司資料"
]

# Canonical output keys and a map from many possible label spellings -> canonical key
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
    # BR / CR / 公司編號
    r"\b(BR|CR)\s*No\.?\b": "brNo",
    r"Business\s*Registration\s*(?:No|Number)\b": "brNo",
    r"公司(?:註冊|登記)?編號": "brNo",

    # Business name
    r"^Business\s*Name\b": "Business Name",
    r"^公司名稱$": "Business Name",

    # Business name (Chinese)
    r"Business\s*Name\s*\(Chinese\)": "Business Name(Chinese)",
    r"公司名稱（?中文）?$": "Business Name(Chinese)",
    r"中文名稱": "Business Name(Chinese)",

    # Registration date
    r"^Registration\s*Date\b": "Registration Date",
    r"註冊日期": "Registration Date",

    # Status
    r"^Business\s*Status\b": "Business Status",
    r"公司狀態|現況": "Business Status",

    # Type
    r"^Business\s*Type\b": "Business Type",
    r"公司類別|公司類型": "Business Type",

    # Remarks / 備註
    r"^Remarks?$": "Remarks",
    r"備註": "Remarks",

    # Winding up
    r"^Winding\s*Up\s*Mode\b": "Winding Up Mode",
    r"清盤模式": "Winding Up Mode",

    # Dissolution date
    r"Date\s*of\s*Dissolution\s*/\s*Ceasing\s*to\s*Exist": "Date of Dissolution / Ceasing to Exist",
    r"解散.*日期|註銷.*日期": "Date of Dissolution / Ceasing to Exist",

    # Register of charges
    r"^Register\s*of\s*Charges\b": "Register of Charges",
    r"押記登記冊": "Register of Charges",

    # Important note
    r"^Important\s*Note\b": "Important Note",
    r"重要提示|重要備註": "Important Note",
}

# Pre-compile label regexes
LABEL_PATTERNS = [(re.compile(pat, re.IGNORECASE), key) for pat, key in LABEL_MAP.items()]

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
    """
    Try to locate the Basic Information section root node.
    We search for a heading with known titles and return a nearby block (table, dl, or section).
    Fallback: return the whole soup to let parsers scan globally.
    """
    # 1) Find headings by text
    for hdr in soup.find_all(["h1", "h2", "h3", "h4", "h5"], string=True):
        txt = hdr.get_text(" ", strip=True)
        if any(title.lower() in txt.lower() for title in BASIC_INFO_SECTION_TITLES):
            # Prefer a sibling table/dl
            sib = hdr.find_next(lambda tag: tag.name in ["table", "dl", "section", "div"])
            if sib:
                return sib
            return hdr.parent if hdr.parent else hdr

    # 2) Look for a table/dl that contains one of the labels
    candidates = soup.find_all(["table", "dl", "section", "div"])
    for node in candidates:
        txt = node.get_text(" ", strip=True)
        if any(re.search(pat, txt, re.IGNORECASE) for pat in LABEL_MAP.keys()):
            return node

    # 3) Fallback: whole soup
    return soup

def _parse_pairs_from_table(table) -> Dict[str, str]:
    """
    Parse label/value pairs from a table (tr > th/td or td/td).
    """
    out = {}
    for tr in table.find_all("tr"):
        cells = tr.find_all(["th", "td"])
        if len(cells) < 2:
            continue
        raw_label = cells[0].get_text(" ", strip=True)
        key = _normalize_label(raw_label)
        if not key:
            continue
        value = _clean_value(cells[1].get_text(" ", strip=True))
        out[key] = value
    return out

def _parse_pairs_from_dl(dl) -> Dict[str, str]:
    """
    Parse <dl><dt>Label</dt><dd>Value</dd>...</dl>
    """
    out = {}
    dts = dl.find_all("dt")
    for dt in dts:
        dd = dt.find_next_sibling("dd")
        if not dd:
            continue
        key = _normalize_label(dt.get_text(" ", strip=True))
        if not key:
            continue
        out[key] = _clean_value(dd.get_text(" ", strip=True))
    return out

def _parse_pairs_from_label_value_blocks(container) -> Dict[str, str]:
    """
    Generic parser: find nodes that look like "Label: Value" (or "Label：Value").
    Useful when site renders as paragraphs/divs.
    """
    out = {}
    for node in container.find_all(text=True):
        txt = str(node)
        if ":" in txt or "：" in txt:
            # Split on the first colon-like character
            parts = re.split(r"[:：]", txt, maxsplit=1)
            if len(parts) != 2:
                continue
            key = _normalize_label(parts[0])
            if not key:
                continue
            val = _clean_value(parts[1])
            if val:
                out[key] = val
    return out

def parse_basic_info_from_html(html: str) -> Dict[str, str]:
    """
    Given a company page HTML, return a dict with the requested keys.
    Missing fields become "".
    """
    soup = BeautifulSoup(html, "html.parser")
    container = _find_basic_info_container(soup)
    data: Dict[str, str] = {}

    # Try table
    table = container.find("table")
    if table:
        data.update(_parse_pairs_from_table(table))
    # Try definition list
    dl = container.find("dl")
    if dl:
        data.update(_parse_pairs_from_dl(dl))
    # Generic label/value text scan
    data.update(_parse_pairs_from_label_value_blocks(container))

    # Build canonical result
    result = {k: data.get(k, "") for k in CANON_KEYS}
    return result

def fetch_company_basic_info(session: requests.Session, url: str) -> Dict[str, str]:
    """
    Polite fetch of a company page, then extract the Basic Information block.
    """
    # robots.txt check
    path = urlparse(url).path
    if not allowed_to_fetch(BASE, USER_AGENT, path):
        return {k: "" for k in CANON_KEYS}
    html = fetch_html(url, session, timeout=TIMEOUT)
    info = parse_basic_info_from_html(html)
    return info
