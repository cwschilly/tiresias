import numpy as np
import pandas as pd

from constants import ALL_FILMS, MIN_RATINGS
from preprocessing.preprocess import clean


def _raw(rows):
    return pd.DataFrame(rows, columns=ALL_FILMS)


def test_clean_scales_to_half_stars():
    df = clean(_raw([{"tenet": 10, "batman_begins": 1, "dunkirk": 5}]))
    assert df.iloc[0]["tenet"] == 5.0
    assert df.iloc[0]["batman_begins"] == 0.5
    assert df.iloc[0]["dunkirk"] == 2.5


def test_clean_drops_users_below_min_ratings():
    rows = [{"tenet": 8},                                        # 1 rating -> dropped
            {"tenet": 8, "batman_begins": 6, "dunkirk": 7}]      # 3 ratings -> kept
    df = clean(_raw(rows))
    assert len(df) == 1
    assert df.iloc[0].count() >= MIN_RATINGS


def test_clean_coerces_junk_to_nan():
    df = clean(_raw([{"tenet": "ten", "batman_begins": 6, "dunkirk": 7, "memento": 8}]))
    assert pd.isna(df.iloc[0]["tenet"])
    assert df.iloc[0]["batman_begins"] == 3.0


def test_clean_ignores_columns_outside_the_current_index():
    # A raw sheet export can carry columns for retired films (e.g. Insomnia);
    # those must not count toward MIN_RATINGS or survive into the output.
    row = {f: np.nan for f in ALL_FILMS} | {"tenet": 8, "batman_begins": 6, "insomnia": 9}
    df = clean(pd.DataFrame([row]))
    assert "insomnia" not in df.columns
    assert len(df) == 0  # only 2 real ratings, below MIN_RATINGS
