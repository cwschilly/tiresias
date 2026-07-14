import numpy as np
import pandas as pd

from constants import ALL_FILMS, NOLAN_INDEX
from validation.validate import validate_index


def _users_from_rule(rule, n_users=6, films=None):
    films = films or ALL_FILMS
    rows = []
    for u in range(n_users):
        rows.append({f: rule(u, *NOLAN_INDEX[f]) for f in films})
    return pd.DataFrame(rows, index=[f"u{u}" for u in range(n_users)])


def test_index_driven_users_yield_positive_skill():
    # Ratings are a clean linear function of the index -> huge skill
    rule = lambda u, fabula, syuzhet: np.clip(1.0 + 0.25 * fabula + 0.15 * syuzhet, 0.5, 5.0)
    report = validate_index(_users_from_rule(rule))
    assert report.skill > 0.5
    assert "SEES CLEARLY" in report.verdict


def test_random_users_yield_low_skill():
    rng = np.random.default_rng(0)
    rule = lambda u, fabula, syuzhet: float(rng.uniform(0.5, 5.0))
    report = validate_index(_users_from_rule(rule))
    assert report.skill < 0.15


def test_users_below_cv_threshold_are_skipped():
    df = pd.DataFrame(
        [{"tenet": 5.0, "batman_begins": 1.0, "dunkirk": 3.0},  # only 3 ratings
         {f: 3.0 for f in ALL_FILMS}],
        index=["u_sparse", "u_full"])
    report = validate_index(df)
    assert report.n_users == 1
    assert report.n_predictions == len(ALL_FILMS)


def test_report_serializes_for_pipeline_json():
    rule = lambda u, fabula, syuzhet: np.clip(1.0 + 0.3 * fabula, 0.5, 5.0)
    d = validate_index(_users_from_rule(rule)).as_dict()
    assert set(d) == {"n_users", "n_predictions", "rmse_index",
                      "rmse_user_mean", "rmse_film_mean", "skill", "verdict"}
