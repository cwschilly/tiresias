import pytest

from constants import NOLAN_INDEX
from nolan_index.aggregate import weighted_euclidean
from personalization.predict import derive_alpha, fit_user


def _axis_rater(axis, slope=0.4, intercept=1.0):
    """A synthetic user whose rating is a function of one axis only (0=fabula, 1=syuzhet)."""
    return {f: min(5.0, max(0.5, intercept + slope * NOLAN_INDEX[f][axis]))
            for f in NOLAN_INDEX}


def _balanced_rater(slope=0.2, intercept=1.0):
    return {f: min(5.0, max(0.5, intercept + slope * weighted_euclidean(*NOLAN_INDEX[f])))
            for f in NOLAN_INDEX}


def test_derive_alpha_is_half_for_flat_ratings():
    assert derive_alpha({f: 3.0 for f in NOLAN_INDEX}) == pytest.approx(0.5)


def test_derive_alpha_leans_toward_the_driving_axis():
    # The axes correlate across the real filmography, so a single-axis rater
    # never derives a pure 0 or 1 — but the lean must be clear and ordered.
    alpha_fabula_head = derive_alpha(_axis_rater(axis=0))
    alpha_syuzhet_head = derive_alpha(_axis_rater(axis=1))
    assert alpha_fabula_head > 0.6
    assert alpha_syuzhet_head < 0.4
    assert alpha_fabula_head > alpha_syuzhet_head


def test_derive_alpha_stays_in_unit_interval():
    for ratings in (_axis_rater(0), _axis_rater(1), _balanced_rater()):
        assert 0.0 <= derive_alpha(ratings) <= 1.0


def test_fit_user_ignores_films_outside_the_catalogue():
    ratings = {"tenet": 5.0, "oppenheimer": 4.0, "dunkirk": 3.5, "not_a_film": 2.0}
    prediction = fit_user(ratings)
    assert set(prediction.films) == {"tenet", "oppenheimer", "dunkirk"}


def test_fit_uses_the_derived_alpha():
    ratings = _balanced_rater()
    prediction = fit_user(ratings)
    assert prediction.alpha == pytest.approx(derive_alpha(ratings))
    expected = weighted_euclidean(*NOLAN_INDEX[prediction.films[0]], alpha=prediction.alpha)
    assert prediction.metric_values[0] == pytest.approx(expected)


def test_predict_evaluates_the_fitted_curve_at_a_target_point():
    ratings = _balanced_rater()
    prediction = fit_user(ratings)
    fabula, syuzhet = NOLAN_INDEX["oppenheimer"]
    assert prediction.predict(fabula, syuzhet) == pytest.approx(
        ratings["oppenheimer"], abs=0.25)
