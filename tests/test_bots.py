from conftest import FIXTURES

from coauthored import bots
from coauthored.scan.gitlog import RawCommit
from coauthored.scan.records import build
from coauthored.signatures import catalogue

B = bots.load(FIXTURES / "bots.yaml")
CAT = catalogue.load(FIXTURES / "catalogue.yaml")


def test_suffix_rule() -> None:
    assert B.is_bot("dependabot[bot]", "49699333+dependabot[bot]@users.noreply.github.com")
    assert B.is_bot("snyk-bot", "snyk-bot@snyk.io")
    assert not B.is_bot("GitHub", "noreply@github.com")
    assert not B.is_bot("Ada", "ada@example.org")


def test_agent_with_bot_suffix_is_not_maintenance() -> None:
    cat = catalogue.Catalogue(
        version="t",
        signatures=[
            catalogue.Signature(id="jules", tool="Jules", kind="identity", name=r"google-labs-jules\[bot\]")
        ],
    )
    raw = RawCommit(
        "a" * 40, (), "google-labs-jules[bot]", "x@y", "GitHub", "noreply@github.com", "", "", "m"
    )
    rec = build(raw, cat, B, "s", set())
    assert rec["attributed"] and not rec["author_maint_bot"]


def test_bot_committer_human_author_counts() -> None:
    raw = RawCommit("b" * 40, (), "Ada", "ada@example.org", "pytorchmergebot[bot]", "x@y", "", "", "m")
    rec = build(raw, CAT, B, "s", set())
    assert not rec["author_maint_bot"] and rec["committer_maint_bot"]


def test_mirror_flag() -> None:
    raw = RawCommit("c" * 40, (), "Ada", "a@b", "Ada", "a@b", "", "", "Fix\n\nPiperOrigin-RevId: 123")
    assert build(raw, CAT, B, "s", set())["mirror_export"]
    raw2 = RawCommit(
        "d" * 40, (), "Ada", "a@b", "Ada", "a@b", "", "", "Fix\n\nmentions PiperOrigin-RevId: inline"
    )
    assert not build(raw2, CAT, B, "s", set())["mirror_export"]
