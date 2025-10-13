# scrape_hkc.py
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib.robotparser as robotparser

BASE = "https://hongkong-corp.com"
START_PATH = "/A/4"  

USER_AGENT = "learning-scraper/0.1 (+your-email@example.com)"


def allowed_to_fetch(base: str, user_agent: str, path: str) -> bool:
    """Check robots.txt for permission to fetch `path`."""
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


def parse_companies_from_html(html: str):
    soup = BeautifulSoup(html, "html.parser")
    # On this site company blocks appear to be headings (h6) with the name and the status letter/date in the following text node — adjust selectors if needed.
    results = []
    # look for heading tags that appear to contain company names
    for h in soup.select("h6, h4, h3"):   # broaden to catch variations
        name = h.get_text(strip=True)
        if not name:
            continue
        # attempt to find the status/date nearby (e.g., the next sibling text)
        status = ""
        # check next sibling text
        nxt = h.find_next_sibling(text=True)
        if nxt:
            status = nxt.strip()
        # fallback: look for small tags or span after the heading
        if not status:
            small = h.find_next(["small", "span"])
            if small:
                status = small.get_text(strip=True)
        results.append({"name": name, "status_raw": status})
    return results


def find_next_page(html: str, base_url: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    # The page has a "Next" link — try to find it by text
    link = soup.find("a", string=lambda s: s and "Next" in s)
    if link and link.get("href"):
        return urljoin(base_url, link["href"])
    return None


def main():
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    start_url = urljoin(BASE, START_PATH)

    # Check robots.txt
    path = urlparse(start_url).path
    if not allowed_to_fetch(BASE, USER_AGENT, path):
        print("robots.txt disallows scraping this path or robots.txt couldn't be read. Exiting.")
        return

    url = start_url
    pages_scraped = 0
    max_pages = 3   # change to limit how many pages you follow during learning
    delay_seconds = 3  # be polite; increase if you plan to scrape many pages

    while url and pages_scraped < max_pages:
        print(f"Fetching: {url}")
        html = fetch_html(url, session)
        rows = parse_companies_from_html(html)
        for r in rows:
            print(r["name"], "—", r["status_raw"])
        pages_scraped += 1
        time.sleep(delay_seconds)
        url = find_next_page(html, BASE)

    print(f"Done. Scraped {pages_scraped} page(s).")


if __name__ == "__main__":
    main()