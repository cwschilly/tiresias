"""Goal 2: predict The Odyssey's Oscar haul from its position on the Nolan Index.

Poisson regression of nomination and win counts on the aggregated Nolan Index
metric (see nolan_index/aggregate.py), fit on all 12 films and validated with
leave-one-film-out CV against a mean-count baseline. Coefficients ship to the
website via pipeline.json, where prediction is just
exp(intercept + coef * metric).
"""
from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import PoissonRegressor

from constants import ALL_FILMS, ODYSSEY_DEFAULT, OSCARS
from nolan_index.aggregate import DEFAULT_METHOD, aggregate, film_metric


@dataclass
class OscarReport:
    n_films: int
    mae_noms: float
    mae_noms_baseline: float
    mae_wins: float
    mae_wins_baseline: float
    skill: float          # 1 - mae_noms / baseline; > 0 means the index helps
    verdict: str

    def as_dict(self) -> dict:
        return {k: round(v, 4) if isinstance(v, float) else v
                for k, v in self.__dict__.items()}


def _design_matrix(films: list[str], method: str = DEFAULT_METHOD) -> np.ndarray:
    return np.array([[film_metric(f, method)] for f in films])


def _fit(X: np.ndarray, y: np.ndarray) -> PoissonRegressor:
    return PoissonRegressor(alpha=0.1, max_iter=1000).fit(X, y)


def _coeffs(model: PoissonRegressor) -> dict:
    return {"intercept": float(model.intercept_), "metric": float(model.coef_[0])}


def fit_oscar_models(method: str = DEFAULT_METHOD) -> dict:
    """Fit on all films; returns the coefficient block for pipeline.json."""
    X = _design_matrix(ALL_FILMS, method)
    noms = np.array([OSCARS[f][0] for f in ALL_FILMS])
    wins = np.array([OSCARS[f][1] for f in ALL_FILMS])
    return {"noms": _coeffs(_fit(X, noms)), "wins": _coeffs(_fit(X, wins)), "method": method}


def predict_counts(coeffs: dict, fabula: float, syuzhet: float) -> tuple[float, float]:
    """Expected (nominations, wins) at an index position; wins can't exceed noms."""
    metric = aggregate(fabula, syuzhet, coeffs.get("method", DEFAULT_METHOD))
    expected = lambda c: float(np.exp(c["intercept"] + c["metric"] * metric))
    noms = expected(coeffs["noms"])
    return noms, min(expected(coeffs["wins"]), noms)


def _loo_mae(X: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Leave-one-film-out MAE for the Poisson model and the mean baseline."""
    err_model, err_base = [], []
    for i in range(len(y)):
        keep = np.arange(len(y)) != i
        model = _fit(X[keep], y[keep])
        err_model.append(abs(float(model.predict(X[i:i + 1])[0]) - y[i]))
        err_base.append(abs(y[keep].mean() - y[i]))
    return float(np.mean(err_model)), float(np.mean(err_base))


def _verdict(skill: float) -> str:
    if skill > 0.15:
        return "THE ACADEMY IS PREDICTABLE — craziness coordinates foretell the gold."
    if skill > 0.0:
        return "THE ACADEMY WHISPERS — the index hears something, faintly."
    return "THE ACADEMY IS CHAOS — no index can chart the hearts of 10,000 voters."


def validate_oscars(method: str = DEFAULT_METHOD) -> OscarReport:
    X = _design_matrix(ALL_FILMS, method)
    noms = np.array([OSCARS[f][0] for f in ALL_FILMS])
    wins = np.array([OSCARS[f][1] for f in ALL_FILMS])

    mae_noms, mae_noms_base = _loo_mae(X, noms)
    mae_wins, mae_wins_base = _loo_mae(X, wins)
    skill = 1.0 - mae_noms / mae_noms_base if mae_noms_base > 1e-9 else 0.0

    return OscarReport(
        n_films=len(ALL_FILMS),
        mae_noms=mae_noms,
        mae_noms_baseline=mae_noms_base,
        mae_wins=mae_wins,
        mae_wins_baseline=mae_wins_base,
        skill=skill,
        verdict=_verdict(skill),
    )


def print_report(report: OscarReport, coeffs: dict) -> None:
    noms, wins = predict_counts(coeffs, ODYSSEY_DEFAULT["fabula"], ODYSSEY_DEFAULT["syuzhet"])
    print("── Goal 2: Can the Nolan Index predict Oscars? ──")
    print(f"Films (all of them):        {report.n_films}")
    print(f"LOO MAE noms (index/base):  {report.mae_noms:.2f} / {report.mae_noms_baseline:.2f}")
    print(f"LOO MAE wins (index/base):  {report.mae_wins:.2f} / {report.mae_wins_baseline:.2f}")
    print(f"Skill vs mean-count:        {report.skill:+.1%}")
    print(f"Verdict: {report.verdict}")
    print(f"Odyssey at default (fabula {ODYSSEY_DEFAULT['fabula']:.0f}, syuzhet {ODYSSEY_DEFAULT['syuzhet']:.0f}): "
          f"{noms:.1f} nominations, {wins:.1f} wins expected\n")
