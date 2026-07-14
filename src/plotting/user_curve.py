"""Task 4: one respondent's ratings vs. the aggregated Nolan Index metric,
with their best-fit curve and a marker predicting their Odyssey rating."""
import os

import numpy as np

from constants import FILM_LABELS, ODYSSEY_DEFAULT, OUTPUT_DIR
from nolan_index.aggregate import weighted_euclidean
from personalization.predict import fit_user
from plotting.style import GOLD, GREEN_DARK, INK, add_titles, equation_box, fit_line, new_figure, save, style_marker

_DEGREE_NAME = {1: "linear", 2: "quadratic", 3: "cubic"}


def plot_user_curve(row: int, ratings: dict, path: str = None) -> str:
    """ratings: {film_key: rating in 0.5-5.0}, e.g. from preprocessing.users.get_user_ratings."""
    prediction = fit_user(ratings)
    fit = prediction.fit

    fig, ax = new_figure()
    add_titles(fig, f"Respondent #{row}'s Nolan Curve", "Your Rating vs. Wackiness Index")

    for film, x in zip(prediction.films, prediction.metric_values):
        style_marker(ax, [x], [ratings[film]])
        ax.annotate(FILM_LABELS[film].split(" (")[0], (x, ratings[film]),
                   textcoords="offset points", xytext=(8, 6), fontsize=8,
                   fontfamily="Georgia", color=INK)

    lo, hi = min(prediction.metric_values), max(prediction.metric_values)
    pad = (hi - lo) * 0.15 or 1.0
    xs = np.linspace(lo - pad, hi + pad, 200)
    fit_line(ax, xs, [fit.predict(x) for x in xs])

    odyssey_x = weighted_euclidean(ODYSSEY_DEFAULT["fabula"], ODYSSEY_DEFAULT["syuzhet"],
                                   prediction.alpha)
    odyssey_rating = fit.predict(odyssey_x)
    ax.scatter([odyssey_x], [odyssey_rating], marker="*", s=260,
              color=GOLD, edgecolors="#8a6a0e", zorder=5)
    ax.annotate(f"The Odyssey: {odyssey_rating:.1f}", (odyssey_x, odyssey_rating),
               textcoords="offset points", xytext=(10, -14), fontsize=9,
               style="italic", fontfamily="Georgia")

    degree_name = _DEGREE_NAME[fit.degree]
    equation_box(ax, f"{degree_name} fit, fabula weight α = {prediction.alpha:.1f}, "
                     f"R² = {fit.r2_in_sample:.2f} (LOO R² = {fit.r2_loo:.2f})")

    ax.set_xlabel("Wackiness Index ->", fontfamily="Georgia", fontweight="bold", color=GREEN_DARK)
    ax.set_ylabel("Your Rating ->", fontfamily="Georgia", fontweight="bold", color=GREEN_DARK)

    path = path or os.path.join(OUTPUT_DIR, "users", f"user_{row}.png")
    save(fig, path)
    return path
