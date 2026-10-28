"""End-to-end smoke test of `coauthored analyze` on synthetic aggregates (no network, small bootstrap)."""

import json
from pathlib import Path

import polars as pl
import pytest
import yaml

pytest.importorskip("matplotlib")
pytest.importorskip("statsmodels")

from coauthored.analysis import run  # noqa: E402

MONTHS = [
    f"{y}-{m:02d}" for y in (2023, 2024, 2025, 2026) for m in range(1, 13) if f"{y}-{m:02d}" <= "2026-09"
]
TOOLS = ["Claude Code", "GitHub Copilot", "OpenHands"]


def _inputs(root: Path) -> None:
    shares = {"S1": 0.06, "S2": 0.12, "S3": 0.02}
    rm, tools, rev, policy = [], [], [], []
    cfg: dict[str, list[dict[str, object]]] = {"s1": [], "s2": [], "s3": []}
    for stratum, share in shares.items():
        for r in range(5):
            repo = f"{stratum.lower()}org/repo{r}"
            cfg[stratum.lower()].append({"repo": repo, "created_at": f"201{r}-01-01"})
            policy.append(
                {
                    "repo": repo,
                    "stratum": stratum,
                    "policy": ["silent", "requires_disclosure", "bans"][r % 3],
                    "source": "CONTRIBUTING.md",
                    "agent_config": 0,
                }
            )
            for i, m in enumerate(MONTHS):
                k = round(200 * share * i / len(MONTHS)) + r
                for dedup in (True, False):
                    for spec in ("primary", "strict"):
                        tag = {"repo": repo, "month": m, "spec": spec, "dedup": dedup, "stratum": stratum}
                        rm.append(
                            {
                                **tag,
                                "n": 200,
                                "n_attr": k,
                                "authors": 20,
                                "authors_attr": min(k, 20),
                                "n_mirror": 0,
                                "n_bare_assisted": 0,
                            }
                        )
                        for j, tool in enumerate(TOOLS):
                            tools.append({**tag, "tool": tool, "n_attr": k // (j + 1)})
            for attr in (True, False):
                rev.append(
                    {
                        "repo": repo,
                        "attr": attr,
                        "n": 100,
                        "n_reverted": 2,
                        "spec": "primary",
                        "stratum": stratum,
                    }
                )
    cfg["s3"][0]["caliper_violated"] = True
    agg = root / "data" / "aggregated"
    agg.mkdir(parents=True)
    u32 = {c: pl.UInt32 for c in ("n", "n_attr", "authors", "authors_attr", "n_mirror", "n_bare_assisted")}
    pl.DataFrame(rm).cast(u32).write_parquet(agg / "repo_month.parquet")  # type: ignore[arg-type]
    pl.DataFrame(tools).write_parquet(agg / "repo_month_tool.parquet")
    pl.DataFrame(rev).write_parquet(agg / "reverts.parquet")
    pl.DataFrame(policy).write_csv(root / "data" / "policy.csv")
    survival = [
        {
            "repo": "s1org/repo0",
            "number": i,
            "stratum": "S1",
            "method": ["squash", "merge"][i % 2],
            "head_attributed": True,
            "landed_attributed": i % 3 != 0,
            "survived": i % 3 != 0,
            "head_tools": "Claude Code",
            "n_head": 2,
            "head_truncated": False,
        }
        for i in range(30)
    ]
    pl.DataFrame(survival).write_csv(root / "data" / "survival.csv")
    (root / "data" / "manifest.json").write_text(json.dumps({"snapshot_date": "2026-10-28", "repos": {}}))
    (root / "configs").mkdir()
    (root / "configs" / "repos.yaml").write_text(yaml.safe_dump(cfg))
    overrides = {"repos": [{"repo": "s1org/repo0", "final": "mentions"}]}
    (root / "configs" / "policy_overrides.yaml").write_text(yaml.safe_dump(overrides))


def test_analyze_writes_every_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _inputs(tmp_path)
    monkeypatch.chdir(tmp_path)
    numbers = run.analyze(b=20, out=Path("results"))
    assert {r["hypothesis"] for r in numbers["hypotheses"]} == {f"H{i}" for i in range(1, 8)}
    figs = {p.stem for p in Path("results/figures").glob("*.svg")}
    assert figs >= {
        "f1_monthly_share",
        "f2_tools",
        "f3_heatmap",
        "f4_per_repo",
        "f5_survival",
        "f6_policy",
        "f8_breadth",
    }
    for t in ("hypotheses", "sensitivity", "reverts"):
        assert Path(f"results/tables/{t}.md").read_text().startswith("| ")
    assert "exploratory" in Path("results/tables/hypotheses.md").read_text()
    saved = json.loads(Path("results/numbers.json").read_text())
    assert saved["bootstrap_draws"] == 20
    assert "NaN" not in Path("results/numbers.json").read_text()
    policy = {r["repo"]: r["policy"] for r in saved["per_repo_2026q3"]}
    assert policy["s1org/repo0"] == "mentions"  # override applied


def test_spread_separates_close_labels() -> None:
    from coauthored.analysis.figures import _spread

    out = _spread({"a": 0.10, "b": 0.105, "c": 0.5}, gap=0.02)
    assert out["b"] - out["a"] >= 0.02 and out["c"] == 0.5


def test_clean_handles_nan_and_numpy() -> None:
    import numpy as np

    assert run._clean({"x": float("nan"), "y": (np.float64(1.5), np.int64(2))}) == {"x": None, "y": [1.5, 2]}
