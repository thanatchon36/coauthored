"""`coauthored analyze`: every table, figure and number in the paper from committed aggregates, no network.

Inputs: data/aggregated/*.parquet, data/survival.csv, data/policy.csv (+ configs/policy_overrides.yaml),
configs/repos.yaml. Outputs: results/numbers.json, results/tables/*.md, results/figures/*.{svg,png}.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import polars as pl
import yaml

from coauthored.analysis import figures as fig
from coauthored.analysis import hypotheses as h

DATA, CONFIGS, RESULTS = Path("data"), Path("configs"), Path("results")


def _clean(x: Any) -> Any:
    """JSON-safe: NaN → None, tuples → lists, nested."""
    if isinstance(x, float):
        return None if math.isnan(x) else round(x, 6)
    if isinstance(x, dict):
        return {str(k): _clean(v) for k, v in x.items()}
    if isinstance(x, list | tuple):
        return [_clean(v) for v in x]
    if isinstance(x, np.floating | np.integer):
        return _clean(x.item())
    return x


def load_policy() -> pl.DataFrame | None:
    path = DATA / "policy.csv"
    if not path.exists():
        return None
    policy = pl.read_csv(path)
    overrides = CONFIGS / "policy_overrides.yaml"
    if overrides.exists():
        final = {r["repo"]: r["final"] for r in yaml.safe_load(overrides.read_text())["repos"]}
        policy = policy.with_columns(
            pl.col("repo")
            .map_elements(lambda r: final.get(r), return_dtype=pl.String)
            .fill_null(pl.col("policy"))
            .alias("policy")
        )
    return policy


def load_survival() -> pl.DataFrame | None:
    path = DATA / "survival.csv"
    if not path.exists():
        return None
    s = pl.read_csv(path)
    return s.with_columns(
        pl.col("head_attributed").cast(pl.Boolean),
        pl.col("survived")
        .cast(pl.String)
        .replace({"": None})
        .replace_strict({"True": True, "False": False}, default=None, return_dtype=pl.Boolean),
    )


def monthly_series(pool: pl.DataFrame, draws: list[pl.DataFrame]) -> pl.DataFrame:
    def by(d: pl.DataFrame) -> pl.DataFrame:
        return (
            d.group_by("stratum", "month")
            .agg(pl.col("n").sum(), pl.col("n_attr").sum())
            .with_columns((pl.col("n_attr") / pl.col("n")).alias("share"))
        )

    point = by(pool)
    boot = pl.concat(
        [
            by(d).select("stratum", "month", "share").with_columns(pl.lit(i).alias("b"))
            for i, d in enumerate(draws)
        ]
    )
    band = boot.group_by("stratum", "month").agg(
        pl.col("share").quantile(0.025).alias("lo"), pl.col("share").quantile(0.975).alias("hi")
    )
    return point.join(band, on=["stratum", "month"]).sort("stratum", "month")


def _quarter_col(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(pl.col("month").map_elements(h.quarter, return_dtype=pl.String).alias("q"))


def _per_repo_q3(df: pl.DataFrame) -> pl.DataFrame:
    q = h._between(df, *h.Q3_2026)
    breadth = (
        q.filter(pl.col("n") >= 10)
        .group_by("stratum", "repo")
        .agg((pl.col("authors_attr") / pl.col("authors")).mean().alias("breadth"))
    )
    agg = q.group_by("stratum", "repo").agg(pl.col("n").sum(), pl.col("n_attr").sum())
    return agg.join(breadth, on=["stratum", "repo"], how="left").with_columns(
        (pl.col("n_attr") / pl.col("n")).alias("share")
    )


def _md_table(rows: list[dict[str, Any]], cols: list[str]) -> str:
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    out += ["| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows]
    return "\n".join(out) + "\n"


def _fmt(r: h.Result) -> dict[str, Any]:
    return {
        "hypothesis": r.hypothesis,
        "estimate": f"{r.estimate:.4f}",
        "95% CI": f"[{r.ci[0]:.4f}, {r.ci[1]:.4f}]" if not math.isnan(r.ci[0]) else "–",
        "supported": "exploratory" if "exploratory" in r.statement else "yes" if r.supported else "no",
        "p (one-sided)": "–" if r.p_one_sided is None else f"{r.p_one_sided:.4f}",
        "p (Holm)": "–" if r.p_holm is None else f"{r.p_holm:.4f}",
    }


def analyze(b: int = h.B, out: Path = RESULTS) -> dict[str, Any]:
    fig.setup()
    rm = pl.read_parquet(DATA / "aggregated" / "repo_month.parquet")
    tools = pl.read_parquet(DATA / "aggregated" / "repo_month_tool.parquet")
    reverts = pl.read_parquet(DATA / "aggregated" / "reverts.parquet")
    cfg = yaml.safe_load((CONFIGS / "repos.yaml").read_text())
    survival, policy = load_survival(), load_policy()

    results = h.run_all(rm, tools, survival, policy, b=b)
    viol = {r["repo"] for r in cfg["s3"] if r.get("caliper_violated")}
    sens = h.sensitivity(rm, viol, b=b)

    pool, full = h._primary(rm, True), h._primary(rm, False)
    draws = h.Bootstrap(pool, b=b).draws()
    series = monthly_series(pool, draws)
    per_repo = _per_repo_q3(full)
    if policy is not None:
        per_repo = per_repo.join(policy.select("repo", "policy"), on="repo", how="left")

    figs = out / "figures"
    fig.f1(series, figs)
    t = _quarter_col(tools.filter((pl.col("spec") == "primary") & pl.col("dedup")))
    nq = _quarter_col(pool).group_by("stratum", "q").agg(pl.col("n").sum())
    fig.f2(t.group_by("stratum", "q", "tool").agg(pl.col("n_attr").sum()), nq, figs)
    order = [(s, r["repo"]) for s in ("S1", "S2", "S3") for r in cfg[s.lower()]]
    fig.f3(full, order, figs)
    fig.f4(per_repo, figs)
    h6 = next((r for r in results if r.hypothesis == "H6"), None)
    if h6 is not None and h6.detail["n"]:
        fig.f5(h6.detail["by_method"], (h6.detail["k"], h6.detail["n"]), figs)
    if policy is not None:
        fig.f6(per_repo.filter(pl.col("policy").is_not_null()), figs)
    fig.f8(per_repo.filter(pl.col("breadth").is_not_null()), figs)

    tables = out / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    (tables / "hypotheses.md").write_text(
        _md_table([_fmt(r) for r in results], list(_fmt(results[0]))), encoding="utf-8"
    )
    srows = [
        {"analysis": name, **{r.hypothesis: f"{r.estimate:.3f} {'✓' if r.supported else '✗'}" for r in res}}
        for name, res in [("primary", results[:4]), *sens.items()]
    ]
    (tables / "sensitivity.md").write_text(
        _md_table(srows, ["analysis", "H1", "H2", "H3", "H4"]), encoding="utf-8"
    )
    rev = (
        reverts.group_by("stratum", "attr")
        .agg(pl.col("n").sum(), pl.col("n_reverted").sum())
        .sort("stratum", "attr")
    )
    rev_rows = [
        {**r, "rate": f"{r['n_reverted'] / r['n']:.4f}" if r["n"] else "–"} for r in rev.iter_rows(named=True)
    ]
    (tables / "reverts.md").write_text(
        _md_table(rev_rows, ["stratum", "attr", "n", "n_reverted", "rate"]), encoding="utf-8"
    )

    numbers: dict[str, Any] = {
        "bootstrap_draws": b,
        "seed": h.SEED,
        "snapshot": json.loads((DATA / "manifest.json").read_text()).get("snapshot_date"),
        "commits_in_window": {
            s: int(pool.filter(pl.col("stratum") == s)["n"].sum()) for s in ("S1", "S2", "S3")
        },
        "attributed_in_window": {
            s: int(pool.filter(pl.col("stratum") == s)["n_attr"].sum()) for s in ("S1", "S2", "S3")
        },
        "bare_assisted_in_window": {
            s: int(pool.filter(pl.col("stratum") == s)["n_bare_assisted"].sum()) for s in ("S1", "S2", "S3")
        },
        "hypotheses": [asdict(r) for r in results],
        "sensitivity": {k: [asdict(r) for r in v] for k, v in sens.items()},
        "monthly": series.to_dicts(),
        "per_repo_2026q3": per_repo.to_dicts(),
        "reverts": rev_rows,
    }
    numbers = _clean(numbers)
    (out / "numbers.json").write_text(json.dumps(numbers, indent=1, ensure_ascii=False), encoding="utf-8")
    return numbers
