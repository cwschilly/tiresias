import math

import pytest

from constants import NOLAN_INDEX
from nolan_index.aggregate import aggregate, euclidean, film_metric, weighted_euclidean


def test_euclidean_matches_pythagorean_distance():
    assert euclidean(3, 4) == pytest.approx(5.0)
    assert euclidean(0, 0) == 0.0


def test_weighted_euclidean_at_half_reduces_to_euclidean():
    assert weighted_euclidean(3, 4, alpha=0.5) == pytest.approx(euclidean(3, 4))


def test_weighted_euclidean_extremes_ignore_one_axis():
    # alpha=1.0 -> full fabula weight, syuzhet ignored
    assert weighted_euclidean(3, 99, alpha=1.0) == pytest.approx(math.sqrt(2) * 3)
    # alpha=0.0 -> full syuzhet weight, fabula ignored
    assert weighted_euclidean(99, 4, alpha=0.0) == pytest.approx(math.sqrt(2) * 4)


def test_aggregate_dispatches_to_named_method():
    assert aggregate(6, 8, method="euclidean") == pytest.approx(10.0)


def test_aggregate_rejects_unknown_method():
    with pytest.raises(KeyError):
        aggregate(1, 1, method="not-a-real-method")


def test_film_metric_uses_nolan_index_coordinates():
    fabula, syuzhet = NOLAN_INDEX["tenet"]
    assert film_metric("tenet") == pytest.approx(math.hypot(fabula, syuzhet))
