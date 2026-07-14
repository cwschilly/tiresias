"""Aggregates a film's (fabula, syuzhet) coordinates into a single scalar.

Kept separate from constants.py so the aggregation method can be swapped —
here and in js/aggregate.js, which mirrors this file exactly — without
touching anything that consumes the resulting metric.
"""
import math

from constants import NOLAN_INDEX


def euclidean(fabula: float, syuzhet: float) -> float:
    """Straight-line distance from (0, 0) — how far a film sits from 'unremarkable'."""
    return math.hypot(fabula, syuzhet)


def weighted_euclidean(fabula: float, syuzhet: float, alpha: float = 0.5) -> float:
    """Euclidean distance with alpha = fabula weight, beta = syuzhet weight.

    alpha + beta always sum to 1, so alpha is the only free parameter; beta is
    just its complement, named for clarity in the formula below.
    alpha = 0.5 reduces exactly to euclidean(); alpha = 1.0 ignores syuzhet
    entirely, alpha = 0.0 ignores fabula. Lets a fit discover that a person's
    taste tracks one axis more than the other.
    """
    beta = 1 - alpha
    return math.sqrt(2 * alpha * fabula ** 2 + 2 * beta * syuzhet ** 2)


AGGREGATORS = {"euclidean": euclidean}
DEFAULT_METHOD = "euclidean"


def aggregate(fabula: float, syuzhet: float, method: str = DEFAULT_METHOD) -> float:
    return AGGREGATORS[method](fabula, syuzhet)


def film_metric(film: str, method: str = DEFAULT_METHOD) -> float:
    fabula, syuzhet = NOLAN_INDEX[film]
    return aggregate(fabula, syuzhet, method)
