"""Fetches and parses a Guardian contributor's article archive."""

import re

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.theguardian.com"
USER_AGENT = "Mozilla/5.0 (compatible; tiresias-research-script/1.0)"

# Guardian article paths look like /film/2023/jul/19/oppenheimer-review-...
# Tag pages (/film/drama) and date-filter pages (/profile/x/2023/jul/19/all)
# don't match, since both have too few or too many path segments before the date.
ARTICLE_HREF_RE = re.compile(r"^/[\w-]+/\d{4}/[a-z]{3}/\d{2}/[\w-]+$")


def fetch_profile_page(author, page, session=None, timeout=15):
    session = session or requests.Session()
    response = session.get(
        f"{BASE_URL}/profile/{author}",
        params={"page": page},
        headers={"User-Agent": USER_AGENT},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.text


def extract_articles(html):
    """Returns a deduplicated list of (headline, url) for every article link."""
    soup = BeautifulSoup(html, "html.parser")
    seen = set()
    articles = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        path = href[len(BASE_URL):] if href.startswith(BASE_URL) else href
        if not ARTICLE_HREF_RE.match(path):
            continue

        title = (link.get("aria-label") or link.get_text(strip=True)).strip()
        if not title:
            continue

        url = href if href.startswith("http") else BASE_URL + href
        if url in seen:
            continue

        seen.add(url)
        articles.append((title, url))
    return articles
