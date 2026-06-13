import os
import hashlib
import pandas as pd

# Only code maintainers have access to the fetch script
try:
    from .fetch import fetch_responses
except ImportError:
    fetch_responses = None

from constants import MIN_RATINGS, DATA_FILEPATH

def read_responses() -> pd.DataFrame:
    """
    Read form responses from CSV, optionally refreshing from Google Sheets.
    If the file is missing and fetch is unavailable, raises FileNotFoundError.
    """
    can_fetch   = fetch_responses is not None
    file_exists = os.path.isfile(DATA_FILEPATH)

    if not file_exists and not can_fetch:
        raise FileNotFoundError(f"{DATA_FILEPATH} not found--create an issue in GitHub.")

    if can_fetch:
        prompt  = "Refresh responses from Google Sheets?" if file_exists else "File not found. Fetch from Google Sheets?"
        do_fetch = input(f"{prompt} (y/n): ").strip().lower() in ("y", "yes")
        if do_fetch:
            return fetch_responses()

    return pd.read_csv(DATA_FILEPATH)

def clean(df: pd.DataFrame) -> pd.DataFrame:
    # Coerce to numeric — empty cells become NaN
    df = df.apply(pd.to_numeric, errors="coerce")

    # Assign anonymous user IDs
    df.index = [f"u{hashlib.md5(str(i).encode()).hexdigest()[:8]}"
                for i in range(len(df))]

    # Drop users below minimum rating threshold
    df = df[df.count(axis=1) >= MIN_RATINGS]
    print(f"Users after filtering: {len(df)}")

    # Normalize 1–10 to 0.5–5.0
    return df / 2.0

def read_and_clean() -> pd.DataFrame:
    raw_data = read_responses()
    return clean(raw_data)
