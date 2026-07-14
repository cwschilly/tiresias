"""Task 3: Oscar nominations and wins as a function of the aggregated metric."""
import os

import numpy as np

from constants import ALL_FILMS, OSCARS, OUTPUT_DIR
from nolan_index.aggregate import DEFAULT_METHOD, film_metric
from oscars.predict import fit_oscar_models
from plotting.style import GREEN_DARK, GREEN_MID, RUST, RUST_DARK, add_titles, fit_line, new_figure, save, style_marker


def plot_oscars_vs_metric(coeffs: dict = None, method: str = DEFAULT_METHOD, path: str = None) -> str:
    coeffs = coeffs or fit_oscar_models(method)
    fig, ax = new_figure()
    add_titles(fig, "The Academy vs. the Nolan Index",
              "Oscar Nominations & Wins vs. Wackiness Index")

    metrics = np.array([film_metric(f, method) for f in ALL_FILMS])
    noms = np.array([OSCARS[f][0] for f in ALL_FILMS])
    wins = np.array([OSCARS[f][1] for f in ALL_FILMS])

    style_marker(ax, metrics, noms, facecolors=GREEN_MID, edgecolors=GREEN_DARK,
                label="Nominations (actual)")
    style_marker(ax, metrics, wins, facecolors=RUST, edgecolors=RUST_DARK, marker="D",
                label="Wins (actual)")

    xs = np.linspace(metrics.min() - 1, metrics.max() + 1, 200)
    noms_curve = np.exp(coeffs["noms"]["intercept"] + coeffs["noms"]["metric"] * xs)
    wins_raw = np.exp(coeffs["wins"]["intercept"] + coeffs["wins"]["metric"] * xs)
    wins_curve = np.minimum(wins_raw, noms_curve)

    fit_line(ax, xs, noms_curve, color=GREEN_MID)
    fit_line(ax, xs, wins_curve, color=RUST)

    ax.set_xlabel("Wackiness Index ->", fontfamily="Georgia", fontweight="bold", color=GREEN_DARK)
    ax.set_ylabel("Oscar count", fontfamily="Georgia", fontweight="bold", color=GREEN_DARK)
    ax.legend(loc="upper right", frameon=False, fontsize=9)

    path = path or os.path.join(OUTPUT_DIR, "oscars.png")
    save(fig, path)
    return path
