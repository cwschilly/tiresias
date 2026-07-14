"""Maps a Google Sheet row number to its anonymized user ID.

preprocess.clean() hashes each row's *position* in the raw CSV before any
rows are dropped for having too few ratings, so this hash stays stable
across reruns even as the dataset grows.
"""
import hashlib

import pandas as pd


def row_to_user_id(row: int) -> str:
    return f"u{hashlib.md5(str(row).encode()).hexdigest()[:8]}"


def get_user_ratings(ratings: pd.DataFrame, row: int) -> pd.Series:
    """The cleaned, rescaled (0.5-5.0) ratings for one respondent, by film."""
    user_id = row_to_user_id(row)
    if user_id not in ratings.index:
        raise ValueError(
            f"Row {row} has no ratings in the cleaned dataset — either out of "
            f"range, or dropped for having fewer than the minimum ratings."
        )
    return ratings.loc[user_id].dropna()
