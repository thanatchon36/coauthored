from pathlib import Path

from conftest import COMMITS
from test_scan import _scan

from coauthored.analysis.aggregate import SENSITIVITY, Spec, load_commits, repo_month, repo_month_tool


def _df(fixture_repo: Path, tmp_path: Path):  # type: ignore[no-untyped-def]
    _scan(fixture_repo, tmp_path)
    return load_commits(tmp_path / "raw" / "fixture__repo" / "commits.jsonl.zst", "fixture/repo")


def test_primary_excludes_merges_and_bots(fixture_repo: Path, tmp_path: Path) -> None:
    rm = repo_month(_df(fixture_repo, tmp_path), Spec())
    # all commits minus the merge and the dependabot commit
    assert rm["n"].sum() == len(COMMITS) + 3 - 1 - 1
    assert rm["n_attr"].sum() == sum(c[3] for c in COMMITS)


def test_sensitivities(fixture_repo: Path, tmp_path: Path) -> None:
    df = _df(fixture_repo, tmp_path)
    n = {s.name: int(repo_month(df, s)["n"].sum()) for s in SENSITIVITY}
    assert n["merges_included"] == n["primary"] + 1
    assert n["bots_included"] == n["primary"] + 1
    assert n["first_parent"] == n["primary"] - 1  # the side-branch commit
    strict = repo_month(df, Spec(name="s", strict=True))["n_attr"].sum()
    assert strict == sum(c[4] for c in COMMITS)


def test_window_and_tools(fixture_repo: Path, tmp_path: Path) -> None:
    df = _df(fixture_repo, tmp_path)
    assert repo_month(df, Spec(start="2025-03", end="2025-04"))["n"].sum() == 2
    tools = repo_month_tool(df, Spec())
    assert set(tools["tool"]) == {"Claude Code", "Cursor", "GitHub Copilot"}


def test_zulu_and_offset_dates_agree() -> None:
    import polars as pl

    from coauthored.analysis.aggregate import month_utc

    df = pl.DataFrame(
        {"d": ["2025-03-31T23:30:00Z", "2025-04-01T06:30:00+07:00", "2025-04-01T00:00:00+00:00"]}
    )
    assert df.select(month_utc("d"))["month"].to_list() == ["2025-03", "2025-03", "2025-04"]
