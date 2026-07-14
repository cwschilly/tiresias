"""Fits one person's ratings against the aggregated Nolan Index metric.

Tries a small family of polynomial degrees and picks whichever generalizes
best under leave-one-out cross-validation, rather than whichever fits the
training points most tightly — in-sample R² trivially favors the highest
degree available, which with ~12 points per person would mean nonsense.
"""
import warnings
from dataclasses import dataclass

import numpy as np

# Minimum points needed for a degree-d fit to still have 2+ points left out
# one at a time during LOO-CV.
MIN_POINTS_FOR_DEGREE = {1: 3, 2: 4, 3: 5}
CUBIC_MIN_POINTS = 8   # only offer cubic once there's enough data to trust it


@dataclass
class CurveFit:
    degree: int
    coeffs: np.ndarray      # highest power first (numpy.polyfit convention)
    r2_in_sample: float
    r2_loo: float

    def predict(self, x: float) -> float:
        return float(_clamp(np.polyval(self.coeffs, x)))


def _clamp(prediction):
    return np.clip(prediction, 0.5, 5.0)


def _r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - y_true.mean()) ** 2))
    return 1.0 - ss_res / ss_tot if ss_tot > 1e-9 else 0.0


def _loo_r2(x: np.ndarray, y: np.ndarray, degree: int) -> float:
    """Leave-one-out R², scored only on held-out points the remaining points
    bracket. A film outside the training x-range (usually Tenet, far beyond
    everything else on the wackiness axis) can only be extrapolated, and no
    polynomial can be fairly validated on extrapolation — the catastrophic
    held-out error would force a flat linear fit on exactly the users whose
    taste is most curved. Extreme films still train every other fold."""
    preds, trues = [], []
    for i in range(len(y)):
        keep = np.arange(len(y)) != i
        if not (x[keep].min() <= x[i] <= x[keep].max()):
            continue
        # Near-duplicate x values (e.g. films collapsing together at an extreme
        # aggregation weight) make polyfit rank-deficient; those candidates
        # score badly under LOO and lose the selection anyway, so the warning
        # carries no signal.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", np.exceptions.RankWarning)
            coeffs = np.polyfit(x[keep], y[keep], degree)
        # Score the predictor as deployed — clamped to the rating scale
        preds.append(float(_clamp(np.polyval(coeffs, x[i]))))
        trues.append(y[i])
    return _r2(np.array(trues), np.array(preds))


def _candidate_degrees(n_points: int) -> list[int]:
    degrees = [d for d, minimum in MIN_POINTS_FOR_DEGREE.items() if n_points >= minimum]
    if n_points < CUBIC_MIN_POINTS:
        degrees = [d for d in degrees if d != 3]
    return degrees


def fit_user_curve(metric_values, ratings) -> CurveFit:
    """metric_values, ratings: parallel sequences, one entry per rated film."""
    x = np.array(metric_values, dtype=float)
    y = np.array(ratings, dtype=float)
    if len(x) < 3:
        raise ValueError("Need at least 3 rated films to fit a curve.")

    best_degree, best_r2_loo = None, None
    for degree in _candidate_degrees(len(x)):
        r2_loo = _loo_r2(x, y, degree)
        if best_r2_loo is None or r2_loo > best_r2_loo:
            best_degree, best_r2_loo = degree, r2_loo

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", np.exceptions.RankWarning)
        coeffs = np.polyfit(x, y, best_degree)
    r2_in_sample = _r2(y, _clamp(np.polyval(coeffs, x)))
    return CurveFit(degree=best_degree, coeffs=coeffs,
                    r2_in_sample=r2_in_sample, r2_loo=best_r2_loo)
