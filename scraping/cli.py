"""Scans a Guardian contributor's archive for Christopher Nolan film reviews.

Usage (from the project root):
    python -m scraping.cli --author peterbradshaw
"""

import argparse
import time

from scraping.guardian import extract_articles, fetch_profile_page
from scraping.nolan_match import NOLAN_TITLES, match_nolan_title


def scan(author, start_page, max_pages, delay):
    """Walks pages until one comes back with no articles at all."""
    found = {title: [] for title in NOLAN_TITLES}
    page = start_page
    for _ in range(max_pages):
        html = fetch_profile_page(author, page)
        articles = extract_articles(html)
        if not articles:
            break

        for headline, url in articles:
            match = match_nolan_title(headline)
            if match:
                found[match].append((headline, url))

        page += 1
        time.sleep(delay)
    return found


def _print_report(found):
    for title in NOLAN_TITLES:
        matches = found[title]
        if not matches:
            print(f"{title}: not found")
            continue
        for headline, url in matches:
            print(f"{title}: {headline}\n  {url}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--author", default="peterbradshaw")
    parser.add_argument("--start-page", type=int, default=1)
    parser.add_argument("--max-pages", type=int, default=200)
    parser.add_argument("--delay", type=float, default=1.0, help="seconds between page requests")
    args = parser.parse_args()

    found = scan(args.author, args.start_page, args.max_pages, args.delay)
    _print_report(found)


if __name__ == "__main__":
    main()
