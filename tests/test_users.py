import pandas as pd
import pytest

from preprocessing.users import get_user_ratings, row_to_user_id


def test_row_to_user_id_is_stable_and_deterministic():
    assert row_to_user_id(0) == row_to_user_id(0)
    assert row_to_user_id(0) != row_to_user_id(1)


def test_get_user_ratings_looks_up_by_original_row_position():
    # Row 1's hash must match preprocessing.preprocess.clean()'s indexing,
    # which hashes range(len(df)) *before* dropping any rows.
    ratings = pd.DataFrame(
        {"tenet": [5.0, 4.0], "dunkirk": [3.0, None]},
        index=[row_to_user_id(0), row_to_user_id(1)],
    )
    row0 = get_user_ratings(ratings, 0)
    assert row0["tenet"] == 5.0
    assert row0["dunkirk"] == 3.0


def test_get_user_ratings_drops_unrated_films():
    ratings = pd.DataFrame({"tenet": [4.0], "dunkirk": [None]}, index=[row_to_user_id(0)])
    row0 = get_user_ratings(ratings, 0)
    assert "dunkirk" not in row0.index


def test_get_user_ratings_raises_for_missing_row():
    ratings = pd.DataFrame({"tenet": [4.0]}, index=[row_to_user_id(0)])
    with pytest.raises(ValueError):
        get_user_ratings(ratings, 7)
