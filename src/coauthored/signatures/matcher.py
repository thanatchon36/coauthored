"""Apply a catalogue to one commit."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from coauthored.signatures.catalogue import Catalogue

# Lenient primary rule (MISSION §3.3, DECISIONS D13): a co-author line anywhere in the message, optionally
# inside a Markdown bullet as squash merges produce ("* Co-authored-by: ..."). `Assisted-by` and
# `Co-developed-by` carry the same attribution in some tools and in the Linux kernel's guidance;
# `Signed-off-by` (a DCO certification) does not.
COAUTHOR_KEYS = ("co-authored-by", "assisted-by", "co-developed-by")
COAUTHOR_RE = re.compile(
    r"^[ \t]*(?:[-*][ \t]+)?(?:" + "|".join(COAUTHOR_KEYS) + r"):[ \t]*(.*?)[ \t]*<([^<>\n]*)>", re.I | re.M
)
_TRAILER_LINE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]*:[ \t]*\S")
_KIND_RANK = {"coauthor": 0, "identity": 1, "marker": 2}


@dataclass(frozen=True)
class Identity:
    name: str
    email: str


@dataclass
class Match:
    signature_ids: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    tool: str | None = None
    strict: bool = False  # attributed using strict trailer position only (sensitivity rule)
    coauthors: list[Identity] = field(default_factory=list)

    @property
    def attributed(self) -> bool:
        return bool(self.signature_ids)


def coauthor_lines(message: str) -> list[Identity]:
    return [Identity(m.group(1), m.group(2)) for m in COAUTHOR_RE.finditer(message)]


def trailer_block(message: str) -> list[str]:
    """Lines of the final paragraph if every line there is a ``Key: value`` trailer or a continuation.

    A simplification of git's own rule, validated against ``git interpret-trailers --parse`` on the
    pilot repositories (docs/phase-1-report.md). The subject line is never a trailer block.
    """
    paragraphs = [p for p in re.split(r"\n[ \t]*\n", message.strip()) if p.strip()]
    if len(paragraphs) < 2:
        return []
    lines = paragraphs[-1].splitlines()
    if not lines or not _TRAILER_LINE_RE.match(lines[0]):
        return []
    for line in lines[1:]:
        if not (_TRAILER_LINE_RE.match(line) or line[:1] in (" ", "\t")):
            return []
    return lines


def match_commit(catalogue: Catalogue, author: Identity, committer: Identity, message: str) -> Match:
    result = Match(coauthors=coauthor_lines(message))
    strict_lines = {ln.strip().lower() for ln in trailer_block(message)}
    hits: list[tuple[int, str, str, bool]] = []  # (kind rank, id, tool, strict)

    for sig in catalogue.of_kind("coauthor"):
        for line in COAUTHOR_RE.finditer(message):
            if sig.matches_identity(line.group(1), line.group(2)):
                in_block = line.group(0).strip().lower() in strict_lines
                hits.append((0, sig.id, sig.tool, in_block))
                break
    for sig in catalogue.of_kind("identity"):
        if any(sig.matches_identity(i.name, i.email) for i in (author, committer)):
            hits.append((1, sig.id, sig.tool, True))
    for sig in catalogue.of_kind("marker"):
        assert sig.text is not None
        if sig.text.lower() in message.lower():
            hits.append((2, sig.id, sig.tool, True))

    if hits:
        hits.sort()
        result.signature_ids = [h[1] for h in hits]
        result.tools = sorted({h[2] for h in hits})
        result.tool = hits[0][2]  # precedence trailer > identity > marker (MISSION §3.3)
        result.strict = any(h[3] for h in hits)
    return result
