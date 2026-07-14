"""Goal 1: is the Nolan Index a suitable predictor of taste?

For each user, leave one film out, fit rating ~ 1 + fabula + syuzhet on the
rest, and predict the held-out film. If the index means anything, this must
beat predicting the user's mean rating (which knows nothing about films).
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd

from constants import ALL_FILMS, NOLAN_INDEX, INDEX_SCALE

## A user needs 4+ ratings to fit a 3-parameter model and still hold one out
MIN_RATINGS_FOR_CV = 4


@dataclass
class ValidationReport:
    n_users: int
    n_predictions: int
    rmse_index: float
    rmse_user_mean: float
    rmse_film_mean: float
    skill: float          # 1 - rmse_index / rmse_user_mean; > 0 means the index helps
    verdict: str

    def as_dict(self) -> dict:
        return {k: round(v, 4) if isinstance(v, float) else v
                for k, v in self.__dict__.items()}


def _design_row(film: str) -> list[float]:
    fabula, syuzhet = NOLAN_INDEX[film]
    return [1.0, fabula / INDEX_SCALE, syuzhet / INDEX_SCALE]


def _loo_errors(films: list[str], r: np.ndarray, film_means: pd.Series):
    """Leave-one-out squared errors for the index model and both baselines."""
    A = np.array([_design_row(f) for f in films])
    err_idx, err_user, err_film = [], [], []
    for i, film in enumerate(films):
        keep = np.arange(len(films)) != i
        coef, *_ = np.linalg.lstsq(A[keep], r[keep], rcond=None)
        pred = float(np.clip(A[i] @ coef, 0.5, 5.0))
        err_idx.append((pred - r[i]) ** 2)
        err_user.append((r[keep].mean() - r[i]) ** 2)
        err_film.append((film_means[film] - r[i]) ** 2)
    return err_idx, err_user, err_film


def _verdict(skill: float) -> str:
    if skill > 0.15:
        return "THE INDEX SEES CLEARLY — syuzhet & fabula craziness predict mortal taste."
    if skill > 0.0:
        return "THE INDEX SEES DIMLY — a faint signal in the entrails, but a signal."
    return "THE INDEX IS BLIND — much like Tiresias. Gather more mortals."


def validate_index(ratings: pd.DataFrame) -> ValidationReport:
    film_means = ratings.mean(axis=0).reindex(ALL_FILMS).fillna(ratings.stack().mean())

    all_idx, all_user, all_film = [], [], []
    n_users = 0
    for user in ratings.index:
        rated = [f for f in ALL_FILMS if pd.notna(ratings.loc[user, f])]
        if len(rated) < MIN_RATINGS_FOR_CV:
            continue
        n_users += 1
        r = ratings.loc[user, rated].values.astype(float)
        e_idx, e_user, e_film = _loo_errors(rated, r, film_means)
        all_idx += e_idx; all_user += e_user; all_film += e_film

    rmse = lambda e: float(np.sqrt(np.mean(e)))
    rmse_index, rmse_user, rmse_film = rmse(all_idx), rmse(all_user), rmse(all_film)
    # A perfect baseline (identical ratings everywhere) leaves the index no room to help
    skill = 1.0 - rmse_index / rmse_user if rmse_user > 1e-9 else 0.0

    return ValidationReport(
        n_users=n_users,
        n_predictions=len(all_idx),
        rmse_index=rmse_index,
        rmse_user_mean=rmse_user,
        rmse_film_mean=rmse_film,
        skill=skill,
        verdict=_verdict(skill),
    )


def print_report(report: ValidationReport) -> None:
    print("\n── Goal 1: Is the Nolan Index a suitable predictor? ──")
    print(f"Users evaluated:        {report.n_users}")
    print(f"Held-out predictions:   {report.n_predictions}")
    print(f"RMSE (Nolan Index):     {report.rmse_index:.3f}")
    print(f"RMSE (user-mean):       {report.rmse_user_mean:.3f}")
    print(f"RMSE (film-mean):       {report.rmse_film_mean:.3f}")
    print(f"Skill vs user-mean:     {report.skill:+.1%}")
    print(f"Verdict: {report.verdict}\n")
