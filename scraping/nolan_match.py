"""Matches Guardian headlines to Christopher Nolan film reviews.

Reuses the project's own film list from src/constants.py instead of
keeping a second copy of Nolan's filmography in sync.
"""

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from constants import FILM_LABELS, ODYSSEY_DEFAULT  # noqa: E402

_YEAR_SUFFIX_RE = re.compile(r"\s*\(\d{4}\)$")


def _strip_year(label):
    return _YEAR_SUFFIX_RE.sub("", label)


NOLAN_TITLES = sorted(
    {_strip_year(label) for label in FILM_LABELS.values()} | {_strip_year(ODYSSEY_DEFAULT["label"])},
    key=len,
    reverse=True,
)


def match_nolan_title(headline):
    """Returns the Nolan film title a headline reviews, or None.

    Guardian review headlines follow "<Title> review – <blurb>", so a
    match requires the literal word "review" immediately after the title
    (not just the title appearing somewhere in the text).
    """
    for title in NOLAN_TITLES:
        pattern = rf"^{re.escape(title)}\s+review\b"
        if re.match(pattern, headline, re.IGNORECASE):
            return title
    return None
