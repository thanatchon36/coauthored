"""Pre-registered hypothesis tests H1–H7 (PREREGISTRATION §4) on repository-month aggregates.

Pooled shares use the shared-history-deduplicated rows (``dedup``); repo-weighted shares use full histories.
Confidence intervals are percentile intervals from cluster-bootstrap resamples of repositories within stratum.
One-sided bootstrap p-values (share of resamples on the wrong side of the null) feed the Holm correction; the
decision rule of each hypothesis is the one in the pre-registration, not the p-value.
"""

from __future__ import annotations

import math
import warnings
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import polars as pl

SEED = 20261028
B = 2000
Q3_2026 = ("2026-07", "2026-09")
H2_MONTHS = [f"2026-{m:02d}" for m in range(4, 10)]
H3_WINDOW = ("2025-03", "2026-09")
H5_QUARTERS = ["2025-Q2", "2025-Q3", "2025-Q4", "2026-Q1", "2026-Q2", "2026-Q3"]


@dataclass
class Result:
    hypothesis: str
    statement: str
    estimate: float
    ci: tuple[float, float]
    supported: bool
    p_one_sided: float | None
    detail: dict[str, Any] = field(default_factory=dict)
    p_holm: float | None = None


def _primary(rm: pl.DataFrame, dedup: bool, spec: str = "primary") -> pl.DataFrame:
    return rm.filter((pl.col("spec") == spec) & (pl.col("dedup") == dedup))


def _between(df: pl.DataFrame, lo: str, hi: str) -> pl.DataFrame:
    return df.filter(pl.col("month").is_between(pl.lit(lo), pl.lit(hi)))


def pooled(df: pl.DataFrame) -> float:
    n = int(df["n"].sum())
    return float(df["n_attr"].sum()) / n if n else float("nan")


def repo_weighted(df: pl.DataFrame, min_n: int = 10) -> float:
    d = df.filter(pl.col("n") >= min_n)
    return float((d["n_attr"] / d["n"]).mean()) if d.height else float("nan")  # type: ignore[arg-type]


def odds_ratio(a: pl.DataFrame, b: pl.DataFrame) -> float:
    xa, na = float(a["n_attr"].sum()), float(a["n"].sum())
    xb, nb = float(b["n_attr"].sum()), float(b["n"].sum())
    # Haldane correction keeps the ratio finite when a stratum has no attributed commit
    if min(xa, na - xa, xb, nb - xb) == 0:
        xa, na, xb, nb = xa + 0.5, na + 1, xb + 0.5, nb + 1
    return (xa / (na - xa)) / (xb / (nb - xb))


class Bootstrap:
    """Resample repositories with replacement within each stratum; one draw per call to ``frames``."""

    def __init__(self, df: pl.DataFrame, b: int = B, seed: int = SEED) -> None:
        self.parts = {
            s: {r: g for (r,), g in df.filter(pl.col("stratum") == s).group_by(["repo"], maintain_order=True)}
            for s in sorted(df["stratum"].unique().to_list())
        }
        self.b = b
        self.rng = np.random.default_rng(seed)

    def draws(self) -> list[pl.DataFrame]:
        out = []
        for _ in range(self.b):
            pieces = []
            for _s, groups in self.parts.items():
                names = list(groups)
                for i, k in enumerate(self.rng.integers(0, len(names), len(names))):
                    # relabel so a repository drawn twice counts as two clusters
                    pieces.append(groups[names[k]].with_columns(pl.lit(f"{names[k]}#{i}").alias("repo")))
            out.append(pl.concat(pieces))
        return out


def _ci(values: list[float]) -> tuple[float, float]:
    v = np.asarray([x for x in values if not math.isnan(x)])
    if not v.size:
        return (float("nan"), float("nan"))
    return (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)))


def _p_wrong_side(values: list[float], null: float) -> float:
    """One-sided bootstrap p-value for H: statistic > null."""
    v = [x for x in values if not math.isnan(x)]
    return (sum(x <= null for x in v) + 1) / (len(v) + 1)


def _boot(draws: list[pl.DataFrame], fn: Callable[[pl.DataFrame], float]) -> list[float]:
    return [fn(d) for d in draws]


# --- H1 ---------------------------------------------------------------------------------------------------
def h1(pool: pl.DataFrame, draws: list[pl.DataFrame], full: pl.DataFrame) -> Result:
    def stat(d: pl.DataFrame) -> float:
        return pooled(_between(d.filter(pl.col("stratum") == "S1"), *Q3_2026))

    est, boot = stat(pool), _boot(draws, stat)
    rw = repo_weighted(_between(full.filter(pl.col("stratum") == "S1"), *Q3_2026))
    return Result(
        "H1",
        "Pooled S1 attributed share, 2026-07..09, is at least 5%",
        est,
        _ci(boot),
        est >= 0.05,
        _p_wrong_side(boot, 0.05),
        {"repo_weighted": rw},
    )


# --- H2 ---------------------------------------------------------------------------------------------------
def h2(pool: pl.DataFrame, draws: list[pl.DataFrame]) -> Result:
    def by_month(d: pl.DataFrame) -> dict[str, tuple[float, float]]:
        out = {}
        for m in H2_MONTHS:
            mm = d.filter(pl.col("month") == m)
            out[m] = (
                pooled(mm.filter(pl.col("stratum") == "S1")),
                pooled(mm.filter(pl.col("stratum") == "S3")),
            )
        return out

    def stat(d: pl.DataFrame) -> float:
        q = _between(d, *Q3_2026)
        return odds_ratio(q.filter(pl.col("stratum") == "S1"), q.filter(pl.col("stratum") == "S3"))

    months = by_month(pool)
    every_month = all(a > b for a, b in months.values())
    est, boot = stat(pool), _boot(draws, stat)
    ci = _ci(boot)
    return Result(
        "H2",
        "S1 > S3 in every month 2026-04..09, and the 2026-Q3 odds ratio S1:S3 is at least 2 (CI excludes 1)",
        est,
        ci,
        every_month and est >= 2 and ci[0] > 1,
        _p_wrong_side([math.log(x) for x in boot], 0.0),
        {"monthly_s1_s3": months, "every_month": every_month},
    )


# --- H3 ---------------------------------------------------------------------------------------------------
def _month_index(month: str, origin: str = H3_WINDOW[0]) -> int:
    y, m = map(int, month.split("-"))
    y0, m0 = map(int, origin.split("-"))
    return (y - y0) * 12 + (m - m0)


def glm_slopes(d: pl.DataFrame) -> dict[str, float]:
    """Binomial GLM logit(share) ~ month × stratum on repository-month counts; month slopes per stratum."""
    import statsmodels.api as sm

    d = _between(d, *H3_WINDOW).filter(pl.col("n") > 0)
    t = np.asarray([_month_index(m) for m in d["month"].to_list()], dtype=float)
    strata = ["S1", "S2", "S3"]
    s = d["stratum"].to_list()
    cols = [np.ones_like(t), t]
    for k in strata[1:]:
        ind = np.asarray([x == k for x in s], dtype=float)
        cols += [ind, ind * t]
    x = np.column_stack(cols)
    y = np.column_stack([d["n_attr"].to_numpy(), (d["n"] - d["n_attr"]).to_numpy()])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fit = sm.GLM(y, x, family=sm.families.Binomial()).fit()
    b = fit.params
    return {"S1": float(b[1]), "S2": float(b[1] + b[3]), "S3": float(b[1] + b[5])}


def h3(pool: pl.DataFrame, draws: list[pl.DataFrame]) -> Result:
    est = glm_slopes(pool)
    boot = [glm_slopes(d) for d in draws]
    ci = {k: _ci([x[k] for x in boot]) for k in ("S1", "S2", "S3")}
    diff = [x["S1"] - x["S3"] for x in boot]
    ci_diff = _ci(diff)
    ok = ci["S1"][0] > 0 and ci["S2"][0] > 0 and ci_diff[0] > 0
    return Result(
        "H3",
        "Positive monthly logit slope in S1 and in S2, and S1 slope > S3 slope (CIs exclude 0)",
        est["S1"] - est["S3"],
        ci_diff,
        ok,
        _p_wrong_side(diff, 0.0),
        {"slopes": est, "slope_ci": ci},
    )


# --- H4 ---------------------------------------------------------------------------------------------------
def h4(pool: pl.DataFrame, draws: list[pl.DataFrame]) -> Result:
    def stat(d: pl.DataFrame) -> float:
        q = _between(d, *Q3_2026)
        return pooled(q.filter(pl.col("stratum") == "S2")) - pooled(q.filter(pl.col("stratum") == "S1"))

    est, boot = stat(pool), _boot(draws, stat)
    ci = _ci(boot)
    return Result(
        "H4",
        "Pooled 2026-Q3 share in S2 exceeds that in S1 (CI of the difference excludes 0)",
        est,
        ci,
        ci[0] > 0,
        _p_wrong_side(boot, 0.0),
    )


# --- H5 ---------------------------------------------------------------------------------------------------
def quarter(month: str) -> str:
    y, m = month.split("-")
    return f"{y}-Q{(int(m) - 1) // 3 + 1}"


def tool_shares(tools: pl.DataFrame) -> dict[str, dict[str, float]]:
    t = tools.with_columns(pl.col("month").map_elements(quarter, return_dtype=pl.String).alias("q"))
    out: dict[str, dict[str, float]] = {}
    for (q,), g in t.group_by(["q"]):
        agg = g.group_by("tool").agg(pl.col("n_attr").sum())
        total = float(agg["n_attr"].sum())
        out[str(q)] = {r["tool"]: r["n_attr"] / total for r in agg.iter_rows(named=True)}
    return out


def h5_margin(tools: pl.DataFrame) -> float:
    """Smallest margin, over the quarters, of Claude Code's share over the next tool's (> 0 = plurality)."""
    shares = tool_shares(tools)
    margins = []
    for q in H5_QUARTERS:
        s = shares.get(q, {})
        claude = s.get("Claude Code", 0.0)
        other = max((v for k, v in s.items() if k != "Claude Code"), default=0.0)
        margins.append(claude - other)
    return min(margins)


def h5(tools: pl.DataFrame, draws: list[pl.DataFrame]) -> Result:
    est = h5_margin(tools)
    boot = _boot(draws, h5_margin)
    return Result(
        "H5",
        "Claude Code has the plurality of attributed commits in S1 ∪ S2 every quarter 2025-Q2..2026-Q3",
        est,
        _ci(boot),
        est > 0,
        _p_wrong_side(boot, 0.0),
        {"quarterly_shares": tool_shares(tools)},
    )


# --- H6 ---------------------------------------------------------------------------------------------------
def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (centre - half, centre + half)


def h6(survival: pl.DataFrame) -> Result:
    from scipy.stats import binomtest

    a = survival.filter(pl.col("head_attributed"))
    k, n = int(a["survived"].cast(pl.Int64).sum()), a.height
    est = k / n if n else float("nan")
    by_method = {
        str(m): (
            int(g["survived"].cast(pl.Int64).sum()),
            g.height,
            wilson(int(g["survived"].cast(pl.Int64).sum()), g.height),
        )
        for (m,), g in a.group_by(["method"])
    }
    p = float(binomtest(k, n, 0.8, alternative="greater").pvalue) if n else None
    return Result(
        "H6",
        "At least 80% of sampled merged PRs with an attributed head commit keep the attribution",
        est,
        wilson(k, n),
        n > 0 and est >= 0.8,
        p,
        {"k": k, "n": n, "by_method": by_method, "inspected": survival.height},
    )


# --- H7 (exploratory) -------------------------------------------------------------------------------------
def h7(full: pl.DataFrame, policy: pl.DataFrame) -> Result:
    q = _between(full, *Q3_2026).join(policy.select("repo", "policy"), on="repo", how="left")
    shares = {str(c): pooled(g) for (c,), g in q.group_by(["policy"]) if c is not None}
    disc = shares.get("requires_disclosure", float("nan"))
    rest = pooled(q.filter(pl.col("policy").is_in(["bans", "silent"])))
    return Result(
        "H7",
        "Repositories requiring disclosure have a higher attributed share than those banning or silent "
        "(exploratory)",
        disc - rest,
        (float("nan"), float("nan")),
        disc > rest,
        None,
        {"by_policy": shares},
    )


def holm(results: list[Result]) -> None:
    """Holm step-down adjustment over the results that carry a p-value, in place."""
    ps = sorted((r.p_one_sided, i) for i, r in enumerate(results) if r.p_one_sided is not None)
    m, running = len(ps), 0.0
    for rank, (p, i) in enumerate(ps):
        running = max(running, min(1.0, (m - rank) * p))
        results[i].p_holm = running


def run_all(
    rm: pl.DataFrame,
    tools: pl.DataFrame,
    survival: pl.DataFrame | None,
    policy: pl.DataFrame | None,
    b: int = B,
) -> list[Result]:
    pool = _primary(rm, dedup=True)
    full = _primary(rm, dedup=False)
    draws = Bootstrap(pool, b=b).draws()
    t = tools.filter((pl.col("spec") == "primary") & pl.col("stratum").is_in(["S1", "S2"]))
    if "dedup" in t.columns:
        t = t.filter(pl.col("dedup"))
    tool_draws = Bootstrap(t, b=b).draws()
    out = [h1(pool, draws, full), h2(pool, draws), h3(pool, draws), h4(pool, draws), h5(t, tool_draws)]
    if survival is not None:
        out.append(h6(survival))
    holm(out)
    if policy is not None:
        out.append(h7(full, policy))
    return out
