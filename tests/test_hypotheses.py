import math

import polars as pl
import pytest

from coauthored.analysis import hypotheses as h


def _rm(
    shares: dict[str, float], months: list[str], n: int = 200, repos: int = 4, grow: bool = True
) -> pl.DataFrame:
    """Synthetic repo-month rows: every repository of a stratum has the same share each month."""
    rows = []
    for stratum, share in shares.items():
        for r in range(repos):
            for i, m in enumerate(months):
                s = share * (1 + i / len(months)) if grow and stratum != "S3" else share
                rows.append(
                    {
                        "repo": f"{stratum}/{r}",
                        "month": m,
                        "n": n,
                        "n_attr": round(n * min(s, 0.9)),
                        "stratum": stratum,
                        "spec": "primary",
                        "dedup": True,
                    }
                )
    df = pl.DataFrame(rows)
    return pl.concat([df, df.with_columns(pl.lit(False).alias("dedup"))])


MONTHS = [f"{y}-{m:02d}" for y in (2025, 2026) for m in range(1, 13) if f"{y}-{m:02d}" <= "2026-09"]


def test_pooled_and_odds_ratio() -> None:
    a = pl.DataFrame({"n": [100], "n_attr": [20]})
    b = pl.DataFrame({"n": [100], "n_attr": [10]})
    assert h.pooled(a) == 0.2
    assert h.odds_ratio(a, b) == pytest.approx((20 / 80) / (10 / 90))
    assert math.isfinite(h.odds_ratio(a, pl.DataFrame({"n": [100], "n_attr": [0]})))


def test_clear_signal_supports_h1_to_h4() -> None:
    rm = _rm({"S1": 0.06, "S2": 0.15, "S3": 0.01}, MONTHS)
    pool, full = h._primary(rm, True), h._primary(rm, False)
    draws = h.Bootstrap(pool, b=50).draws()
    r1, r2, r3, r4 = h.h1(pool, draws, full), h.h2(pool, draws), h.h3(pool, draws), h.h4(pool, draws)
    assert r1.supported and r1.estimate > 0.05
    assert r2.supported and r2.detail["every_month"]
    assert r3.supported and r3.detail["slopes"]["S1"] > 0
    assert r4.supported and r4.ci[0] > 0


def test_null_signal_rejects() -> None:
    rm = _rm({"S1": 0.01, "S2": 0.01, "S3": 0.01}, MONTHS, grow=False)
    pool, full = h._primary(rm, True), h._primary(rm, False)
    draws = h.Bootstrap(pool, b=30).draws()
    assert not h.h1(pool, draws, full).supported
    assert not h.h2(pool, draws).supported


def test_bootstrap_resamples_within_stratum() -> None:
    rm = h._primary(_rm({"S1": 0.1, "S3": 0.0}, ["2026-07"]), True)
    for d in h.Bootstrap(rm, b=5).draws():
        assert d.filter(pl.col("stratum") == "S1")["repo"].n_unique() == 4
        assert set(d.filter(pl.col("stratum") == "S1")["repo"].str.split("#").list.first()) <= {
            f"S1/{i}" for i in range(4)
        }


def test_h5_margin_and_quarters() -> None:
    rows = [
        {"repo": "a", "month": m, "tool": t, "n_attr": k, "stratum": "S1"}
        for m in MONTHS
        for t, k in (("Claude Code", 10), ("GitHub Copilot", 4))
    ]
    t = pl.DataFrame(rows)
    assert h.quarter("2026-09") == "2026-Q3"
    assert h.h5_margin(t) == pytest.approx(6 / 14)


def test_wilson_and_h6() -> None:
    lo, hi = h.wilson(80, 100)
    assert 0.70 < lo < 0.8 < hi < 0.88
    s = pl.DataFrame(
        {
            "head_attributed": [True] * 10 + [False] * 5,
            "survived": [True] * 9 + [False] + [None] * 5,
            "method": ["squash"] * 15,
            "repo": ["a", "b", "c"] * 5,
            "head_tools": ["Claude Code;Codex"] * 2 + ["Claude Code"] * 13,
        }
    )
    r = h.h6(s, b=200)
    assert r.estimate == 0.9 and r.supported and r.detail["n"] == 10
    assert r.detail["repos"] == 3 and r.detail["repos_with_loss"] == 1
    lo, hi = r.detail["ci_cluster_repo"]
    assert lo <= 0.9 <= hi
    assert r.detail["by_tool"] == {"Claude Code": (9, 10), "Codex": (2, 2)}


def test_holm_is_monotone() -> None:
    rs = [h.Result(f"H{i}", "", 0, (0, 0), True, p) for i, p in enumerate([0.01, 0.04, 0.03, None])]
    h.holm(rs)
    assert rs[0].p_holm == pytest.approx(0.03)
    assert rs[2].p_holm == pytest.approx(0.06) and rs[1].p_holm == pytest.approx(0.06)
    assert rs[3].p_holm is None
