from pathlib import Path

from conftest import COMMITS, FIXTURES

from coauthored import bots as bots_mod
from coauthored.scan.run import read_records, scan_repo
from coauthored.signatures import catalogue as cat_mod


def _scan(fixture_repo: Path, tmp_path: Path) -> tuple[dict, list[dict]]:
    cat = cat_mod.load(FIXTURES / "catalogue.yaml")
    bots = bots_mod.load(FIXTURES / "bots.yaml")
    entry = scan_repo(
        "fixture/repo", cat, bots, "salt", tmp_path / "work", tmp_path / "raw", url=str(fixture_repo)
    )
    return entry, list(read_records(tmp_path / "raw" / "fixture__repo" / "commits.jsonl.zst"))


def test_counts_and_flags(fixture_repo: Path, tmp_path: Path) -> None:
    entry, recs = _scan(fixture_repo, tmp_path)
    assert entry["n_commits_all"] == len(COMMITS) + 3  # + revert, side commit, merge
    assert entry["n_attributed_all"] == sum(c[3] for c in COMMITS)
    assert entry["default_branch"] == "main"
    assert sum(r["n_parents"] > 1 for r in recs) == 1
    assert sum(r["is_revert"] for r in recs) == 1
    revert = next(r for r in recs if r["is_revert"])
    assert revert["reverted_sha"] is not None
    assert next(r for r in recs if r["n_parents"] == 0)["first_parent"] is True
    side = [r for r in recs if not r["first_parent"]]
    assert len(side) == 1  # only the side-branch commit is off the first-parent chain


def test_per_commit_expectations(fixture_repo: Path, tmp_path: Path) -> None:
    _, recs = _scan(fixture_repo, tmp_path)
    by_date = {r["author_date"][:7]: r for r in recs}
    for i, (label, _author, _msg, lenient, strict, tool) in enumerate(COMMITS):
        rec = by_date[f"2025-{1 + i % 12:02d}"]
        assert rec["attributed"] is lenient, label
        assert rec["attributed_strict"] is strict, label
        assert rec["tool"] == tool, label
    assert by_date["2025-06"]["author_maint_bot"] is True


def test_no_identities_stored(fixture_repo: Path, tmp_path: Path) -> None:
    _scan(fixture_repo, tmp_path)
    blob = (tmp_path / "raw" / "fixture__repo" / "commits.jsonl.zst").read_bytes()
    import zstandard

    text = zstandard.ZstdDecompressor().stream_reader(blob).read().decode()
    for needle in ("ada@example.org", "Ada Human", "bob@example.org", "Pair work"):
        assert needle not in text
