#!/usr/bin/env python3
"""
Project Truck Finder
Searches Craigslist daily for target mid-size trucks within the configured
radius of the home ZIP code. Stale listings (not seen in 3+ days) are purged.
"""
import os
import sys
import webbrowser
from datetime import datetime

from config import OUTPUT_DIR, REPORT_PATH, get_cities_in_radius
from database import init_db, reset_new_flags, upsert_listing, cleanup_stale_listings, get_all_listings, get_stats
from filter import filter_listing
from report import generate_report
from scrapers.craigslist import CraigslistScraper


def main(open_browser: bool = True):
    print(f"\n{'='*60}")
    print(f"  Project Truck Finder  |  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    cities = get_cities_in_radius()
    print(f"  Searching {len(cities)} Craigslist markets within radius")
    print(f"{'='*60}\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    init_db()
    reset_new_flags()

    scrapers = [
        CraigslistScraper(),
    ]

    session_new = 0

    for scraper in scrapers:
        print(f"[{scraper.name}] Searching...")
        try:
            raw_listings = scraper.search()
        except Exception as e:
            print(f"[{scraper.name}] FAILED: {e}")
            continue

        scraper_new = 0
        scraper_kept = 0
        for raw in raw_listings:
            listing = filter_listing(raw)
            if listing is None:
                continue
            scraper_kept += 1
            if upsert_listing(listing):
                scraper_new += 1
                session_new += 1

        print(f"[{scraper.name}] {len(raw_listings)} raw  |  {scraper_kept} matched  |  {scraper_new} new\n")

    removed = cleanup_stale_listings(days=3)

    stats = get_stats()
    print(f"{'='*60}")
    print(f"  Total in database : {stats['total']}")
    print(f"  New this run      : {session_new}")
    if removed:
        print(f"  Removed (stale)   : {removed}")
    for make, cnt in stats["by_make"].items():
        print(f"  {make:<18}: {cnt}")
    print(f"{'='*60}\n")

    listings = get_all_listings()
    generate_report(listings, session_new)

    report_abs = os.path.abspath(REPORT_PATH)
    print(f"Report: file://{report_abs}\n")

    if open_browser:
        webbrowser.open(f"file://{report_abs}")


if __name__ == "__main__":
    main(open_browser="--no-browser" not in sys.argv)
