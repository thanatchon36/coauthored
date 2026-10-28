"""First-pass classification of a repository's AI-contribution policy (PREREGISTRATION §6).

Rule-based and deliberately conservative: every non-silent result is checked by hand against the quoted
sentence in docs/policy-review.md. Classes, in precedence order: bans > requires_disclosure > mentions >
silent.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

PolicyClass = Literal["bans", "requires_disclosure", "mentions", "silent"]
POLICY_FILES = (
    "CONTRIBUTING.md",
    ".github/CONTRIBUTING.md",
    "docs/CONTRIBUTING.md",
    "AGENTS.md",
    "CLAUDE.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/pull_request_template.md",
    ".github/copilot-instructions.md",
)
AGENT_CONFIG_FILES = ("AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md")

_AI = r"(?:\bAI\b|artificial intelligence|\bLLMs?\b|large language models?|generative|gen-?AI|ChatGPT|"
_AI += r"Copilot|Claude|Gemini|Codex|Cursor|coding (?:agent|assistant)s?|AI[- ](?:generated|assisted|tools?))"
AI = re.compile(_AI, re.I)
BAN = re.compile(
    r"(?:(?:do not|don't|never|must not|may not|cannot|can't|will not|won't) "
    r"(?:submit|use|accept|contribute|merge|send)[^.\n]{0,80}"
    + _AI
    + r")|(?:"
    + _AI
    + r"[^.\n]{0,60}(?:is|are) (?:not (?:accepted|allowed|permitted|welcome)|"
    r"(?:prohibited|forbidden|banned)))|(?:(?:ban|prohibit|forbid)s? [^.\n]{0,40}" + _AI + r")",
    re.I,
)
_MUST = r"(?:must|should|please|are required to|required to|need to|have to) (?:clearly )?"
_TELL = r"(?:disclose|declare|state|mention|note|indicate|label|mark|tell us)"
_TRAILER = r"(?:Assisted-by|Co-developed-by|Generated-by):"
TRAILER = re.compile(_TRAILER, re.I)
DISCLOSE = re.compile(
    r"(?:" + _MUST + _TELL + r"[^.\n]{0,80}" + _AI + r")|(?:" + _AI + r"[^.\n]{0,80}" + _MUST + _TELL + r")|"
    r"(?:disclos\w+[^.\n]{0,60}" + _AI + r")|(?:" + _AI + r"[^.\n]{0,80}disclos\w+)|"
    r"(?:" + _AI + r"[^.\n]{0,60}(?:must|should) be (?:disclosed|declared|noted|labell?ed))|" + _TRAILER,
    re.I,
)


@dataclass(frozen=True)
class PolicyResult:
    cls: PolicyClass
    quote: str  # the sentence that decided the class; empty when silent
    source: str  # file the quote came from
    agent_config: bool


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n\s*\n|\n[-*] ", text) if s.strip()]


def classify(files: dict[str, str]) -> PolicyResult:
    """``files`` maps repository path -> text for the POLICY_FILES that exist."""
    agent_config = any(f in files for f in AGENT_CONFIG_FILES)
    best: tuple[int, str, str] | None = None
    rank = {"bans": 0, "requires_disclosure": 1, "mentions": 2}
    for path in POLICY_FILES:
        text = files.get(path)
        if not text:
            continue
        # AGENTS.md / CLAUDE.md speak *to* agents; on their own they state no policy for contributors
        if path in AGENT_CONFIG_FILES and path != ".github/copilot-instructions.md":
            continue
        for s in _sentences(text):
            if not (AI.search(s) or TRAILER.search(s)):
                continue
            c = "bans" if BAN.search(s) else "requires_disclosure" if DISCLOSE.search(s) else "mentions"
            if best is None or rank[c] < best[0]:
                best = (rank[c], s[:300], path)
    if best is None:
        return PolicyResult("silent", "", "", agent_config)
    cls: PolicyClass = ("bans", "requires_disclosure", "mentions")[best[0]]
    return PolicyResult(cls, best[1], best[2], agent_config)
