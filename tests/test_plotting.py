"""Smoke tests: each plot function runs without error and writes a real file.
Visual correctness isn't practical to assert, but "does it crash" and
"is the file non-empty" catch the bugs that actually happen here."""
import os

from plotting.nolan_scatter import plot_nolan_index
from plotting.oscars_metric import plot_oscars_vs_metric
from plotting.user_curve import plot_user_curve


def _assert_real_png(path):
    assert os.path.isfile(path)
    assert os.path.getsize(path) > 1000


def test_plot_nolan_index_writes_a_png(tmp_path):
    path = plot_nolan_index(path=str(tmp_path / "nolan_index.png"))
    _assert_real_png(path)


def test_plot_oscars_vs_metric_writes_a_png(tmp_path):
    path = plot_oscars_vs_metric(path=str(tmp_path / "oscars.png"))
    _assert_real_png(path)


def test_plot_user_curve_writes_a_png(tmp_path):
    ratings = {"tenet": 3.5, "oppenheimer": 4.5, "dunkirk": 4.0, "inception": 4.0}
    path = plot_user_curve(0, ratings, path=str(tmp_path / "user_0.png"))
    _assert_real_png(path)
