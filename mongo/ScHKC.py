# hk_companies_names_status.py
import os
import csv
import time
import argparse
import requests
from typing import Iterator, Dict, Any

API_BASE = "https://api.opencorporates.com/v0.4"

def fetch_page(q: str, page: int, per_page: int = 50, api_token: str | None = None) -> Dict[str, Any]:
    params = {
        "q": q,
        "jurisdiction_code": "hk",   # Hong Kong
        "per_page": per_page,
        "page": page,
        "order": "score",
        "fields": "name,current_status,company_number"  # reduce payload
    }
    headers = {"User-Agent": "FPCUSA-NameStatus/1.0"}
    if api_token:
        params["api_token"] = api_token
    r = requests.get(f"{API_BASE}/companies/search", params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()["results"]

def iterate_results(q: str, start_page: int = 1, max_pages: int | None = None, per_page: int = 50, api_token: str | None = None) -> Iterator[Dict[str, str]]:
    page = start_page
    pages_yielded = 0
    while True:
        data = fetch_page(q=q, page=page, per_page=per_page, api_token=api_token)
        companies = data.get("companies", [])
        if not companies:
            break
        for item in companies:
            c = item.get("company", {})
            yield {
                "name": c.get("name", ""),
                "status": c.get("current_status", ""),
                "company_number": c.get("company_number", ""),
            }
        page += 1
        pages_yielded += 1
        if max_pages and pages_yielded >= max_pages:
            break
        # gentle pacing
        time.sleep(0.2)

def main():
    p = argparse.ArgumentParser(description="Fetch Hong Kong company names and status from OpenCorporates")
    p.add_argument("--query", "-q", default="A*", help="Search query (supports wildcard *, e.g. 'A*')")
    p.add_argument("--page", "-p", type=int, default=1, help="Start page (1-based)")
    p.add_argument("--pages", type=int, default=1, help="How many pages to fetch from the start page")
    p.add_argument("--per-page", type=int, default=50, help="Results per page (max 100)")
    p.add_argument("--csv", default=None, help="Optional CSV output path")
    args = p.parse_args()

    api_token = os.getenv("OPENCO_API_TOKEN")  # optional; free tier works without but has tighter limits

    rows = list(iterate_results(
        q=args.query,
        start_page=args.page,
        max_pages=args.pages,
        per_page=args.per_page,
        api_token=api_token
    ))

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["name", "status", "company_number"])
            w.writeheader()
            w.writerows(rows)
        print(f"Wrote {len(rows)} rows to {args.csv}")
    else:
        for r in rows:
            print(f"{r['name']} — {r['status']} (#{r['company_number']})")

if __name__ == "__main__":
    main()