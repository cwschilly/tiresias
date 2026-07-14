from scraping.guardian import extract_articles

SAMPLE_HTML = """
<li><a href="/film/2026/may/14/space-jam-review-michael-jordans-90s-merch"
       aria-label="Space Jam review – Michael Jordan's 90s merch-hocking basketball blockbuster rises again">
   </a></li>
<li><a href="/film/2023/jul/19/oppenheimer-review-christopher-nolan-cillian-murphy"
       aria-label="Oppenheimer review – Christopher Nolan's mighty visual achievement">
   </a></li>
<li><a href="/film/cannesfilmfestival">Cannes film festival</a></li>
<li><a href="/profile/peterbradshaw/2026/may/13/all">13 May</a></li>
"""


def test_extracts_dated_article_links_with_aria_label_title():
    titles = [title for title, _ in extract_articles(SAMPLE_HTML)]
    assert "Oppenheimer review – Christopher Nolan's mighty visual achievement" in titles


def test_ignores_tag_pages_and_date_filter_links():
    urls = [url for _, url in extract_articles(SAMPLE_HTML)]
    assert not any("cannesfilmfestival" in url for url in urls)
    assert not any("/profile/peterbradshaw/2026" in url for url in urls)


def test_dedupes_repeated_links():
    assert len(extract_articles(SAMPLE_HTML + SAMPLE_HTML)) == 2
