# count_pages_store_mongo.py
import re
import time
import logging
from datetime import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from typing import List, Optional, Dict

# replace this import with your existing config that defines mongoUri
from config import mongoUri

# ---- Config ----
BASE = "https://hongkong-corp.com"
USER_AGENT = "learning-scraper/0.1 (+your-email@example.com)"
CHARACTERS = [chr(c) for c in range(ord("A"), ord("Z") + 1)]  # default A-Z
START_PAGE = 1
REQUEST_TIMEOUT = 20
RETRY_ATTEMPTS = 3
DELAY_BETWEEN_REQUESTS = 1.2  # be polite
LOG_LEVEL = logging.INFO

# ---- Logging ----
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ---- Mongo setup ----
client = MongoClient(mongoUri)
db = client["test_db"]
collection = db["Companies_Page_Dic"]


def allowed_to_fetch(base: str, user_agent: str, path: str) -> bool:
    """Check robots.txt permission. Conservative: if robots.txt can't be read, return False."""
    import urllib.robotparser as robotparser

    robots_url = urljoin(base, "/robots.txt")
    rp = robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        ok = rp.can_fetch(user_agent, path)
        logger.debug("robots.txt: can_fetch(%s) => %s", path, ok)
        return ok
    except Exception as e:
        logger.warning("Could not read robots.txt at %s: %s. Aborting by default.", robots_url, e)
        return False


def fetch(url: str, session: requests.Session, timeout: int = REQUEST_TIMEOUT) -> str:
    """Fetch a URL with retries, raise for non-200 except handle gracefully upstream."""
    for attempt in range(RETRY_ATTEMPTS):
        try:
            resp = session.get(url, timeout=timeout)
            if resp.status_code == 200:
                return resp.text
            elif resp.status_code == 404:
                # Not found: caller will interpret as zero pages
                logger.debug("Received 404 for %s", url)
                resp.raise_for_status()
            else:
                resp.raise_for_status()
        except requests.RequestException as e:
            logger.warning("Request failed (%s): %s (attempt %d/%d)", url, e, attempt + 1, RETRY_ATTEMPTS)
            time.sleep(1 + attempt * 1.5)
    # after retries, raise last exception
    raise RuntimeError(f"Failed to fetch {url} after {RETRY_ATTEMPTS} attempts")


def parse_max_page_from_html(html: str, char: str) -> Dict:
    """Parse HTML and find the maximum page number for this character.
       Returns dict with keys: pages (int), raw_links (list of hrefs), company_count_sample (int).
    """
    soup = BeautifulSoup(html, "html.parser")

    # 1) collect pagination numeric links: match paths like '/A/3' or '/A/10'
    raw_links = []
    page_numbers = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # normalize path (ignore query params)
        path = urlparse(href).path
        raw_links.append(href)
        # regex: /<char>/<number> (case-insensitive)
        m = re.match(rf"^/{re.escape(char)}/(\d+)$", path, flags=re.I)
        if m:
            page_numbers.add(int(m.group(1)))

    # 2) fallback: if no numeric pagination found, detect if there are company nodes on the page
    #    heuristics: site used headings like h6 for company names (previous scripts used that).
    company_nodes = soup.select("h6, h4, h3, .company, .company-list-item")  # broad
    company_count_sample = len(company_nodes)

    if page_numbers:
        max_page = max(page_numbers)
    else:
        # If there are companies on first page -> at least 1
        if company_count_sample > 0:
            max_page = 1
        else:
            max_page = 0

    return {
        "pages": max_page,
        "raw_pagination_links": list(set(raw_links)),
        "company_count_sample": company_count_sample,
    }


def get_max_pages_for_char(char: str, session: requests.Session) -> int:
    """Get max pages for character `char`. Tries page 1 and inspects pagination links."""
    path = f"/{char}/{START_PAGE}"
    url = urljoin(BASE, path)
    try:
        html = fetch(url, session)
    except Exception as e:
        logger.info("Could not fetch %s: %s", url, e)
        return 0

    parsed = parse_max_page_from_html(html, char)
    pages = parsed["pages"]

    # If parsed.pages == 1, we might still want to double-check if the site hides numeric links:
    # but for learning purposes this rule is reliable: if pagination links exist we used them;
    # otherwise we assume single page if companies found, else zero.
    logger.debug("Character %s -> parse result: %s", char, parsed)
    return pages


def upsert_char_pages(char: str, pages: int, raw_links: List[str]):
    """Upsert result into MongoDB collection."""
    doc = {
        "char": char,
        "pages": pages,
        "raw_pagination_links": raw_links,
        "source": BASE,
        "checked_at": datetime.utcnow(),
    }
    result = collection.update_one({"char": char}, {"$set": doc}, upsert=True)
    logger.info("Upserted %s -> pages=%d (matched=%s, modified=%s, upserted_id=%s)",
                char, pages, result.matched_count, result.modified_count, getattr(result, "upserted_id", None))


def main(chars: Optional[List[str]] = None):
    chars = chars or CHARACTERS

    # check robots
    test_path = "/A/1"
    if not allowed_to_fetch(BASE, USER_AGENT, test_path):
        logger.error("Robots disallow scraping or robots.txt could not be read. Exiting.")
        return

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    for i, ch in enumerate(chars, start=1):
        try:
            logger.info("Checking character %s (%d/%d)", ch, i, len(chars))
            pages = get_max_pages_for_char(ch, session)

            # For auditability, fetch page1 again and parse raw links for storage
            try:
                html = fetch(urljoin(BASE, f"/{ch}/1"), session)
                parsed = parse_max_page_from_html(html, ch)
                raw_links = parsed["raw_pagination_links"]
            except Exception:
                raw_links = []

            upsert_char_pages(ch, pages, raw_links)
        except Exception as e:
            logger.exception("Error while processing %s: %s", ch, e)
        finally:
            time.sleep(DELAY_BETWEEN_REQUESTS)

    logger.info("Done checking characters.")


if __name__ == "__main__":
    main()
