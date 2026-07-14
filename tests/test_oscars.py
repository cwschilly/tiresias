import math

import numpy as np
import pytest

from constants import ALL_FILMS, ODYSSEY_DEFAULT, OSCARS
from oscars.predict import (fit_oscar_models, predict_counts, validate_oscars,
                            _design_matrix, _fit, _loo_mae)


def test_oscars_data_covers_all_films():
    assert set(OSCARS) == set(ALL_FILMS)
    assert all(wins <= noms for noms, wins in OSCARS.values())


def test_design_matrix_is_one_dimensional():
    X = _design_matrix(ALL_FILMS)
    assert X.shape == (len(ALL_FILMS), 1)


def test_fit_returns_finite_coefficients():
    coeffs = fit_oscar_models()
    for target in ("noms", "wins"):
        assert set(coeffs[target]) == {"intercept", "metric"}
        assert all(math.isfinite(v) for v in coeffs[target].values())


def test_predict_counts_clamps_wins_to_noms():
    # Force wins model far above noms model
    coeffs = {
        "noms": {"intercept": 0.0, "metric": 0.0},   # exp(0) = 1
        "wins": {"intercept": 3.0, "metric": 0.0},   # exp(3) ≈ 20
    }
    noms, wins = predict_counts(coeffs, 5.0, 5.0)
    assert noms == pytest.approx(1.0)
    assert wins == pytest.approx(noms)


def test_predict_counts_matches_poisson_formula():
    coeffs = fit_oscar_models()
    fabula, syuzhet = ODYSSEY_DEFAULT["fabula"], ODYSSEY_DEFAULT["syuzhet"]
    noms, wins = predict_counts(coeffs, fabula, syuzhet)
    metric = math.hypot(fabula, syuzhet)
    c = coeffs["noms"]
    expected = math.exp(c["intercept"] + c["metric"] * metric)
    assert noms == pytest.approx(expected)
    assert 0 <= wins <= noms


def test_loo_recovers_index_driven_counts():
    # Synthetic counts that are a clean Poisson function of the metric
    X = _design_matrix(ALL_FILMS)
    y = np.round(np.exp(0.5 + 0.3 * X[:, 0]))
    mae_model, mae_base = _loo_mae(X, y)
    assert mae_model < mae_base


def test_validate_oscars_report_serializes():
    report = validate_oscars()
    d = report.as_dict()
    assert set(d) == {"n_films", "mae_noms", "mae_noms_baseline", "mae_wins",
                      "mae_wins_baseline", "skill", "verdict"}
    assert d["n_films"] == len(ALL_FILMS)
    assert all(math.isfinite(d[k]) for k in d if k not in ("verdict", "n_films"))


def test_fit_direction_matches_real_pattern():
    # In the real data, big hauls (Oppenheimer, Dunkirk) sit at LOW wackiness —
    # the metric coefficient for wins should be negative
    X = _design_matrix(ALL_FILMS)
    wins = np.array([OSCARS[f][1] for f in ALL_FILMS])
    model = _fit(X, wins)
    assert model.coef_[0] < 0
