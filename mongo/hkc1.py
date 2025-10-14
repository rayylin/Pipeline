# collect_letter_page_counts.py
import time
import re
import string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib.robotparser as robotparser
from datetime import datetime, timezone
from typing import Optional, Iterable, Dict, List

from pymongo import MongoClient, UpdateOne
from config import mongoUri

BASE = "https://hongkong-corp.com"
USER_AGENT = "learning-scraper/0.1 (+your-email@example.com)"

# Letters to scan — adjust if the site also supports digits or other buckets
LETTER_BUCKETS = list(string.ascii_uppercase)  # ["A", "B", ..., "Z"]

DELAY_SECONDS = 1.5   # polite delay between letters
TIMEOUT = 20          # request timeout


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
    Determine the maximum page number from pagination links like /A/8864.
    Works even if there's no explicit 'Last' link.
    """
    soup = BeautifulSoup(html, "html.parser")
    max_page = None
    pattern = re.compile(rf"/{re.escape(letter)}/(\d+)$")

    for a in soup.find_all("a", href=True):
        m = pattern.search(a["href"])
        if m:
            p = int(m.group(1))
            if max_page is None or p > max_page:
                max_page = p

    if max_page is None:
        # Fallback if the page renders "Page X of Y"
        text = soup.get_text(" ", strip=True)
        m2 = re.search(r"Page\s+\d+\s+of\s+(\d+)", text, re.IGNORECASE)
        if m2:
            max_page = int(m2.group(1))

    return max_page


def get_total_pages_for_letter(session: requests.Session, letter: str) -> Optional[int]:
    """
    Fetch /<letter>/1 and parse total page count.
    Returns None if it cannot be determined.
    """
    url = build_page_url(BASE, letter, 1)
    path = urlparse(url).path
    if not allowed_to_fetch(BASE, USER_AGENT, path):
        print(f"robots.txt disallows fetching {path}; skipping {letter}.")
        return None

    html = fetch_html(url, session)
    return get_total_pages_from_html(html, letter)


# ---------- Mongo helpers ----------
def ensure_indexes(collection) -> None:
    # Ensure unique index on letter so we can upsert cleanly
    collection.create_index("letter", unique=True)


def build_upserts(results: Dict[str, Optional[int]]) -> List[UpdateOne]:
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
        ops.append(
            UpdateOne(
                {"letter": letter},
                {"$set": doc},
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
    # 1) collect page counts
    results = collect_page_counts(LETTER_BUCKETS)

    # 2) store in MongoDB
    uri = mongoUri
    client = MongoClient(uri)
    db = client["test_db"]
    collection = db["Companies_Page_Dic"]
    ensure_indexes(collection)

    ops = build_upserts(results)
    if ops:
        res = collection.bulk_write(ops, ordered=False)
        print(
            f"Mongo upsert complete. matched={res.matched_count}, "
            f"modified={res.modified_count}, upserted={len(res.upserted_ids)}"
        )
    else:
        print("No ops to write.")


if __name__ == "__main__":
    main()