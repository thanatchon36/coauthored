import numpy as np
import polars as pl
import pytest

pytest.importorskip("scipy")

from coauthored.analysis import glmm  # noqa: E402

MONTHS = [f"2025-{m:02d}" for m in range(3, 13)] + [f"2026-{m:02d}" for m in range(1, 10)]
INDEX = {m: i for i, m in enumerate(MONTHS)}


def _simulate(
    slopes: dict[str, float], sd_slope: float, repos: int = 12, seed: int = 1, n: tuple[int, int] = (50, 400)
) -> tuple[pl.DataFrame, dict[str, float]]:
    """Rows plus each stratum's mean of the drawn repository slopes (what the fixed slope estimates)."""
    rng = np.random.default_rng(seed)
    rows, drawn = [], {k: 0.0 for k in slopes}
    for stratum, slope in slopes.items():
        for r in range(repos):
            a = -4.0 + rng.normal(0, 0.8)
            b = slope + rng.normal(0, sd_slope)
            drawn[stratum] += b / repos
            for m, i in INDEX.items():
                size = int(rng.integers(*n))
                p = 1 / (1 + np.exp(-(a + b * i)))
                rows.append(
                    {
                        "repo": f"{stratum}/{r}",
                        "stratum": stratum,
                        "month": m,
                        "n": size,
                        "n_attr": int(rng.binomial(size, p)),
                    }
                )
    return pl.DataFrame(rows), drawn


def test_recovers_fixed_slopes_and_covers() -> None:
    truth = {"S1": 0.20, "S2": 0.05, "S3": 0.12}
    rows, drawn = _simulate(truth, sd_slope=0.04, n=(2000, 5000))
    fit = glmm.fit(rows, INDEX)
    assert fit.converged
    s = fit.slopes()
    for k, v in drawn.items():
        est, lo, hi = s[k]
        assert abs(est - v) < 0.01
        assert lo < v < hi
    assert s["S1-S3"][1] > 0  # S1 clearly steeper than S3
    assert 0.0 < np.sqrt(fit.sigma[1, 1]) * 1 / fit.scale < 0.15


def test_wide_interval_when_repos_disagree() -> None:
    fit = glmm.fit(_simulate({"S1": 0.1, "S2": 0.1, "S3": 0.1}, sd_slope=0.15, repos=5)[0], INDEX)
    _est, lo, hi = fit.slopes()["S1-S3"]
    assert lo < 0 < hi
