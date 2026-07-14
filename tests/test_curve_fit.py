import numpy as np
import pytest

from personalization.curve_fit import fit_user_curve


def test_requires_at_least_three_points():
    with pytest.raises(ValueError):
        fit_user_curve([1.0, 2.0], [3.0, 4.0])


def test_linear_data_gets_a_linear_fit():
    x = [1, 2, 3, 4, 5]
    y = [1.0 + 0.5 * v for v in x]   # exact line
    fit = fit_user_curve(x, y)
    assert fit.degree == 1
    assert fit.r2_in_sample == pytest.approx(1.0, abs=1e-6)
    assert fit.predict(3) == pytest.approx(2.5, abs=1e-6)


def test_cubic_only_offered_with_enough_points():
    # Exactly on a cubic curve, but only 6 points -> cubic isn't a candidate yet
    x = np.linspace(-2, 2, 6)
    y = 0.5 * x ** 3 - x + 3
    fit = fit_user_curve(x.tolist(), y.tolist())
    assert fit.degree in (1, 2)


def test_cubic_chosen_when_data_is_cubic_and_points_suffice():
    x = np.linspace(-3, 3, 9)
    y = 0.4 * x ** 3 - 0.3 * x ** 2 + x + 2.5
    y = np.clip(y, 0.5, 5.0)
    fit = fit_user_curve(x.tolist(), y.tolist())
    assert fit.degree == 3
    assert fit.r2_loo > 0.9


def test_predictions_are_clamped_to_rating_bounds():
    x = [0, 1, 2, 3]
    y = [5.0, 5.0, 5.0, 5.0]
    fit = fit_user_curve(x, y)
    assert fit.predict(100) <= 5.0
    assert fit.predict(-100) >= 0.5


def test_isolated_leverage_point_does_not_force_a_flat_linear_fit():
    # A curved cluster plus one far-out film (think Tenet at wackiness 20).
    # LOO must score predictions clamped to the rating scale, as deployed —
    # otherwise held-out extrapolation at the leverage point punishes curved
    # fits for absurd ratings they could never actually emit, and a clearly
    # curved taste gets a flat line with R² ~ 0.
    x = [2, 3, 4, 5, 6, 7, 8, 9, 20]
    y = [max(0.5, min(5.0, 5 - 0.08 * (v - 6) ** 2)) for v in x]
    fit = fit_user_curve(x, y)
    assert fit.degree >= 2
    assert fit.r2_loo > 0.9
    assert fit.predict(20) == pytest.approx(0.5)
