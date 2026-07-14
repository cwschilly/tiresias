import hashlib
import os

import pandas as pd

# Only code maintainers have access to the fetch script
try:
    from .fetch import fetch_responses
except ImportError:
    fetch_responses = None

from constants import ALL_FILMS, DATA_FILEPATH, MIN_RATINGS


def read_responses(refresh: bool = False) -> pd.DataFrame:
    """Read form responses from CSV, optionally refreshing from Google Sheets."""
    if refresh:
        if fetch_responses is None:
            raise RuntimeError("Fetching is reserved for maintainers (fetch.py not present).")
        return fetch_responses()

    if not os.path.isfile(DATA_FILEPATH):
        raise FileNotFoundError(f"{DATA_FILEPATH} not found — create an issue in GitHub.")
    return pd.read_csv(DATA_FILEPATH)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    # Restrict to films the index still tracks — the raw CSV can carry columns
    # for retired films (e.g. Insomnia), which must not count toward a
    # respondent's rating total or leak into any downstream computation.
    df = df[ALL_FILMS]

    # Coerce to numeric — empty cells become NaN
    df = df.apply(pd.to_numeric, errors="coerce")

    # Assign anonymous user IDs
    df.index = [f"u{hashlib.md5(str(i).encode()).hexdigest()[:8]}"
                for i in range(len(df))]

    # Drop users below minimum rating threshold
    df = df[df.count(axis=1) >= MIN_RATINGS]

    # Normalize 1-10 to 0.5-5.0
    return df / 2.0


def read_and_clean(refresh: bool = False) -> pd.DataFrame:
    return clean(read_responses(refresh))
