"""Predicts a specific person's rating for The Odyssey from their own ratings.

Two steps, in order:
  1. derive_alpha — read the person's fabula weight alpha (and syuzhet weight
     beta = 1 - alpha) directly off their ratings, from how strongly each
     axis correlates with rating above/below their own average.
  2. fit_user_curve — aggregate each film's (fabula, syuzhet) into a
     wackiness metric at that alpha, then fit the best-generalizing
     polynomial against it (degree chosen by leave-one-out R²).

Alpha comes first so it can be shown to the person as its own result before
any curve exists. This logic is mirrored exactly in js/personalize.js —
change both or neither.
"""
from dataclasses import dataclass

import numpy as np

from constants import INDEX_SCALE, NOLAN_INDEX
from nolan_index.aggregate import weighted_euclidean
from personalization.curve_fit import CurveFit, fit_user_curve


@dataclass
class UserPrediction:
    fit: CurveFit
    alpha: float              # fabula weight (beta = 1 - alpha is the syuzhet weight)
    films: list
    metric_values: list       # parallel to `films`, at the derived alpha

    def predict(self, fabula: float, syuzhet: float) -> float:
        return self.fit.predict(weighted_euclidean(fabula, syuzhet, self.alpha))


def derive_alpha(ratings: dict) -> float:
    """The person's fabula weight, straight from their ratings.

    Mean-center the ratings and correlate against each axis; alpha is
    fabula's share of the combined affinity magnitude. Direction doesn't
    matter — loving or hating an axis both mean it drives their taste — so
    magnitudes are used. Flat or axis-blind raters fall back to a balanced 0.5.
    """
    films = [f for f in ratings if f in NOLAN_INDEX]
    r = np.array([float(ratings[f]) for f in films])
    b = np.array([NOLAN_INDEX[f][0] / INDEX_SCALE for f in films])
    s = np.array([NOLAN_INDEX[f][1] / INDEX_SCALE for f in films])

    w = r - r.mean()
    denom = np.abs(w).sum()
    if denom < 1e-9:
        return 0.5

    fabula_aff = abs(float(w @ b / denom))
    syuzhet_aff = abs(float(w @ s / denom))
    total = fabula_aff + syuzhet_aff
    return fabula_aff / total if total > 1e-9 else 0.5


def fit_user(ratings: dict) -> UserPrediction:
    """ratings: {film_key: rating}, using only films present in NOLAN_INDEX."""
    films = [f for f in ratings if f in NOLAN_INDEX]
    alpha = derive_alpha(ratings)
    metrics = [weighted_euclidean(*NOLAN_INDEX[f], alpha=alpha) for f in films]
    fit = fit_user_curve(metrics, [ratings[f] for f in films])
    return UserPrediction(fit=fit, alpha=alpha, films=films, metric_values=metrics)
