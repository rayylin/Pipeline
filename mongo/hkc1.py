# hkc_collect_and_fetch.py
import time
import re
import string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib.robotparser as robotparser
from datetime import datetime, timezone
from typing import Optional, Iterable, Dict, List, Tuple

from pymongo import MongoClient, UpdateOne
from config import mongoUri

# -------------------- Config --------------------
BASE = "https://hongkong-corp.com"
USER_AGENT = "learning-scraper/0.1 (+your-email@example.com)"

# Letters to scan for the page-count collection task (A–Z).
LETTER_BUCKETS = list(string.ascii_uppercase)   # set to ["A"] while testing

# Politeness / timeouts
DELAY_SECONDS = 1.5
TIMEOUT = 20

# What company list to fetch right now (your ask)
FETCH_LETTER = "A"
FETCH_PAGE = 1
# ------------------------------------------------


# ---------- HTTP & robots ----------
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


# ---------- Page parsing ----------
def build_page_url(base: str, letter: str, page: int) -> str:
    return urljoin(base, f"/{letter}/{page}")


def get_total_pages_from_html(html: str, letter: str) -> Optional[int]:
    """
    Robustly find total pages. Prefers 'X/Y' counters like '1/8864' or 'Page 1 of 8864'.
    Falls back to scanning links (which may undercount if only neighbors are linked).
    """
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    # Prefer "X/Y" (e.g., "Previous 1/8864 Next")
    m_ratio = re.search(r"\b\d+\s*/\s*(\d+)\b", text)
    if m_ratio:
        try:
            return int(m_ratio.group(1))
        except ValueError:
            pass

    # Fallback: "Page X of Y"
    m_page_of = re.search(r"Page\s+\d+\s+of\s+(\d+)", text, re.IGNORECASE)
    if m_page_of:
        try:
            return int(m_page_of.group(1))
        except ValueError:
            pass

    # Last resort: largest '/<LETTER>/<num>' link
    max_page = None
    pat = re.compile(rf"/{re.escape(letter)}/(\d+)$")
    for a in soup.find_all("a", href=True):
        m = pat.search(a["href"])
        if m:
            p = int(m.group(1))
            if max_page is None or p > max_page:
                max_page = p
    return max_page


def get_total_pages_for_letter(session: requests.Session, letter: str) -> Optional[int]:
    """Fetch '/<letter>/1' and parse total page count."""
    url = build_page_url(BASE, letter, 1)
    path = urlparse(url).path
    if not allowed_to_fetch(BASE, USER_AGENT, path):
        print(f"robots.txt disallows fetching {path}; skipping {letter}.")
        return None
    html = fetch_html(url, session)
    return get_total_pages_from_html(html, letter)


# ---------- Companies (name + URL) ----------
def parse_companies_from_html(html: str, base_url: str = BASE) -> List[Tuple[str, str]]:
    """
    Extract (company_name, absolute_url) from a letter page.
    Companies are anchors whose href starts with '/co/'.
    """
    soup = BeautifulSoup(html, "html.parser")
    out: List[Tuple[str, str]] = []

    for a in soup.select('a[href^="/co/"]'):
        name = a.get_text(strip=True)
        href = a.get("href", "").strip()
        if not name or not href:
            continue
        if len(name) < 2:
            continue
        url = urljoin(base_url, href)
        out.append((name, url))

    # de-dup while preserving order
    seen = set()
    unique: List[Tuple[str, str]] = []
    for name, url in out:
        if url not in seen:
            seen.add(url)
            unique.append((name, url))
    return unique


def fetch_companies_on_page(
    session: requests.Session,
    letter: str,
    page: int,
    polite_check_robots: bool = True,
) -> List[Tuple[str, str]]:
    """Fetch `/LETTER/page` and return a list of (name, url)."""
    url = build_page_url(BASE, letter, page)
    if polite_check_robots:
        path = urlparse(url).path
        if not allowed_to_fetch(BASE, USER_AGENT, path):
            return []
    html = fetch_html(url, session, timeout=TIMEOUT)
    return parse_companies_from_html(html, BASE)


# ---------- Mongo helpers ----------
def ensure_indexes(db) -> None:
    # For page totals
    db["Companies_Page_Dic"].create_index("letter", unique=True)
    # For company URLs
    db["Company_Url_Dic"].create_index("url", unique=True)


def build_pagecount_upserts(results: Dict[str, Optional[int]]) -> List[UpdateOne]:
    now = datetime.now(timezone.utc)
    ops: List[UpdateOne] = []
    for letter, total in results.items():
        source_url = build_page_url(BASE, letter, 1)
        doc = {
            "letter": letter,
            "total_pages": total,
            "source_url": source_url,
            "updated_at": now,
        }
        ops.append(UpdateOne({"letter": letter}, {"$set": doc}, upsert=True))
    return ops


def build_company_upserts(pairs: List[Tuple[str, str]]) -> List[UpdateOne]:
    """
    For each (name, url), upsert into Company_Url_Dic with:
      - name
      - url
      - status: "" (default)
      - createTime: set on insert (UTC)
      - updateTime: set on every write (UTC)
    """
    now = datetime.now(timezone.utc)
    ops: List[UpdateOne] = []
    for name, url in pairs:
        ops.append(
            UpdateOne(
                {"url": url},
                {
                    "$set": {
                        "name": name,
                        "url": url,
                        "status": "",
                        "updateTime": now,
                    },
                    "$setOnInsert": {
                        "createTime": now,
                    },
                },
                upsert=True,
            )
        )
    return ops


# ---------- Orchestration ----------
def collect_page_counts(letters: Iterable[str]) -> Dict[str, Optional[int]]:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    out: Dict[str, Optional[int]] = {}
    for i, letter in enumerate(letters, 1):
        try:
            total = get_total_pages_for_letter(session, letter)
            out[letter] = total
            print(f"[{i}/{len(letters)}] {letter}: total_pages={total}")
        except requests.HTTPError as e:
            print(f"HTTP error for {letter}: {e}")
            out[letter] = None
        except Exception as e:
            print(f"Unexpected error for {letter}: {e}")
            out[letter] = None
        time.sleep(DELAY_SECONDS)
    return out


def main():
    # Shared session
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    # ---- Mongo bootstrap ----
    uri = mongoUri
    client = MongoClient(uri)
    db = client["test_db"]
    ensure_indexes(db)

    # ---- Task 1: collect and store total pages per letter ----
    print("Collecting total page counts per letter...")
    page_counts = collect_page_counts(LETTER_BUCKETS)
    ops1 = build_pagecount_upserts(page_counts)
    if ops1:
        res1 = db["Companies_Page_Dic"].bulk_write(ops1, ordered=False)
        print(
            f"Companies_Page_Dic upsert complete. matched={res1.matched_count}, "
            f"modified={res1.modified_count}, upserted={len(res1.upserted_ids)}"
        )
    else:
        print("No page-count ops to write.")

    # ---- Task 2: fetch A/1 companies and store into Company_Url_Dic ----
    print(f"\nFetching companies for {FETCH_LETTER}/{FETCH_PAGE} and writing to Company_Url_Dic...")
    pairs = fetch_companies_on_page(session, FETCH_LETTER, FETCH_PAGE)
    if not pairs:
        print("No companies found or fetch not allowed.")
        return

    ops2 = build_company_upserts(pairs)
    res2 = db["Company_Url_Dic"].bulk_write(ops2, ordered=False)
    print(
        f"Company_Url_Dic upsert complete. matched={res2.matched_count}, "
        f"modified={res2.modified_count}, upserted={len(res2.upserted_ids)}"
    )

    # Also print a couple examples to stdout for visibility
    for name, url in pairs[:5]:
        print(f"example: {name} -> {url}")


if __name__ == "__main__":
    main()