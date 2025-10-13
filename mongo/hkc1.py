# scrape_hkc.py
import time
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib.robotparser as robotparser
from typing import List, Tuple, Optional

BASE = "https://hongkong-corp.com"
LETTER = "A"          # which letter bucket to crawl
START_PAGE = 1        # starting page number within the bucket
USER_AGENT = "learning-scraper/0.1 (+your-email@example.com)"

MAX_PAGES = 3         # safety: how many pages to fetch this run (set None to crawl all)
DELAY_SECONDS = 2     # polite delay between requests


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


def fetch_html(url: str, session: requests.Session, timeout: int = 20) -> str:
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def parse_companies_from_html(html: str, base_url: str) -> List[Tuple[str, str]]:
    """
    Return list of (company_name, absolute_link).
    Companies appear as anchors whose href starts with '/co/'.
    """
    soup = BeautifulSoup(html, "html.parser")
    out: List[Tuple[str, str]] = []

    for a in soup.select('a[href^="/co/"]'):
        name = a.get_text(strip=True)
        href = a.get("href", "").strip()
        if not name or not href:
            continue
        # guard against non-company links under /co/ that have no readable name
        if len(name) < 2:
            continue
        link = urljoin(base_url, href)
        out.append((name, link))

    # de-dup while preserving order
    seen = set()
    unique = []
    for name, link in out:
        if link not in seen:
            seen.add(link)
            unique.append((name, link))
    return unique


def get_total_pages_from_html(html: str, letter: str) -> Optional[int]:
    """
    Find the maximum page number from pagination links like /A/8864.
    Works even if there is no explicit 'Last' link.
    """
    soup = BeautifulSoup(html, "html.parser")
    max_page = None
    # Look for any link that matches /{LETTER}/{number}
    pattern = re.compile(rf"/{re.escape(letter)}/(\d+)$")
    for a in soup.find_all("a", href=True):
        m = pattern.search(a["href"])
        if m:
            p = int(m.group(1))
            if max_page is None or p > max_page:
                max_page = p
    # Some pages render "Page X of Y"—as a fallback, try to parse that text
    if max_page is None:
        text = soup.get_text(" ", strip=True)
        m2 = re.search(r"Page\s+\d+\s+of\s+(\d+)", text, re.IGNORECASE)
        if m2:
            max_page = int(m2.group(1))
    return max_page


def build_page_url(base: str, letter: str, page: int) -> str:
    return urljoin(base, f"/{letter}/{page}")


def main():
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    start_url = build_page_url(BASE, LETTER, START_PAGE)

    # robots.txt check for the path we're about to fetch
    path = urlparse(start_url).path
    if not allowed_to_fetch(BASE, USER_AGENT, path):
        print("robots.txt disallows scraping this path or robots.txt couldn't be read. Exiting.")
        return

    # fetch first page to determine total pages
    html = fetch_html(start_url, session)
    total_pages = get_total_pages_from_html(html, LETTER)
    if total_pages is None:
        print("Could not determine total pages.")
    else:
        print(f"Total pages for /{LETTER}: {total_pages}")

    pages_scraped = 0
    current_page = START_PAGE
    while True:
        url = build_page_url(BASE, LETTER, current_page)
        print(f"\nFetching page {current_page}: {url}")
        html = fetch_html(url, session)
        companies = parse_companies_from_html(html, BASE)

        for name, link in companies:
            print(f"{name} -> {link}")

        pages_scraped += 1
        if MAX_PAGES is not None and pages_scraped >= MAX_PAGES:
            break

        # stop if we reached the known last page
        if total_pages is not None and current_page >= total_pages:
            break

        current_page += 1
        time.sleep(DELAY_SECONDS)

    print(f"\nDone. Scraped {pages_scraped} page(s).")


if __name__ == "__main__":
    main()