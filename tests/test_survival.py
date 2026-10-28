from conftest import FIXTURES

from coauthored.signatures import catalogue
from coauthored.signatures.matcher import Identity
from coauthored.survival.classify import ApiCommit, classify

CAT = catalogue.load(FIXTURES / "catalogue.yaml")
H = Identity("Ada", "ada@example.org")
GH = Identity("GitHub", "noreply@github.com")
TRAILER = "\n\nCo-Authored-By: Claude <noreply@anthropic.com>"


def c(sha: str, msg: str, parents: int = 1, committer: Identity = H) -> ApiCommit:
    return ApiCommit(sha, msg, H, committer, parents)


def test_squash_keeps_trailer() -> None:
    head = [c("a", "wip" + TRAILER), c("b", "fix")]
    landed = c("s", "Feature (#1)\n\n* wip" + TRAILER + "\n\n* fix", committer=GH)
    s = classify(CAT, head, landed)
    assert s.method == "squash" and s.survived is True and s.head_tools == ("Claude Code",)


def test_squash_title_only_loses_trailer() -> None:
    head = [c("a", "wip" + TRAILER), c("b", "fix")]
    s = classify(CAT, head, c("s", "Feature (#1)", committer=GH))
    assert s.method == "squash" and s.survived is False


def test_merge_commit_preserves() -> None:
    head = [c("a", "wip" + TRAILER), c("b", "fix")]
    s = classify(CAT, head, c("m", "Merge pull request #1", parents=2))
    assert s.method == "merge" and s.survived is True


def test_rebase_and_ambiguous() -> None:
    head = [c("a", "one"), c("b", "two" + TRAILER)]
    assert classify(CAT, head, c("r", "two" + TRAILER)).method == "rebase"
    single = [c("a", "only" + TRAILER)]
    s = classify(CAT, single, c("x", "only" + TRAILER))
    assert s.method == "single-commit-ambiguous" and s.survived is True


def test_unattributed_pr_is_not_in_denominator() -> None:
    s = classify(CAT, [c("a", "plain")], c("s", "Plain (#2)"))
    assert s.survived is None
