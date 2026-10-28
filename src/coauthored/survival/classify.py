"""Does an attribution in a pull request's commits reach the default branch? (PREREGISTRATION §5)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from coauthored.signatures.catalogue import Catalogue
from coauthored.signatures.matcher import Identity, match_commit

Method = Literal["merge", "rebase", "squash", "single-commit-ambiguous"]


@dataclass(frozen=True)
class ApiCommit:
    """The fields of a REST API commit object that the classification needs."""

    sha: str
    message: str
    author: Identity
    committer: Identity
    n_parents: int


@dataclass(frozen=True)
class Survival:
    method: Method
    head_attributed: bool
    landed_attributed: bool
    survived: bool | None  # None when no head commit was attributed
    head_tools: tuple[str, ...]


def _attributed(cat: Catalogue, c: ApiCommit) -> tuple[bool, list[str]]:
    m = match_commit(cat, c.author, c.committer, c.message)
    return m.attributed, m.tools


def merge_method(head: list[ApiCommit], landed: ApiCommit) -> Method:
    if landed.n_parents >= 2:
        return "merge"
    if len(head) > 1:
        return "rebase" if landed.message.strip() == head[-1].message.strip() else "squash"
    if head and landed.message.strip() == head[0].message.strip():
        return "single-commit-ambiguous"
    return "squash"


def classify(cat: Catalogue, head: list[ApiCommit], landed: ApiCommit) -> Survival:
    tools: set[str] = set()
    head_attr = False
    for c in head:
        a, t = _attributed(cat, c)
        head_attr |= a
        tools.update(t)
    landed_attr, _ = _attributed(cat, landed)
    method = merge_method(head, landed)
    survived: bool | None
    if not head_attr:
        survived = None
    elif method in ("merge", "rebase"):
        # PR commits keep their messages on the default branch; for rebase, a rewritten message would show in
        # the landed (last) commit, so require it there when the last head commit itself was attributed
        last_attr, _ = _attributed(cat, head[-1])
        survived = landed_attr or method == "merge" or not last_attr
    else:
        survived = landed_attr
    return Survival(method, head_attr, landed_attr, survived, tuple(sorted(tools)))
