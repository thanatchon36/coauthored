"""Signature discovery on pilot clones (MISSION §3.4): frequency-ranked candidate identities and markers.

Prints aggregated counts only. Keyword triage is for *discovery*; the catalogue itself uses exact identities.
Human co-authors are excluded by the keyword filter; any that slip through are discarded at triage.

Usage: uv run python scripts/discover_signatures.py work/*.git
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

from coauthored.scan.gitlog import iter_commits
from coauthored.signatures.matcher import coauthor_lines

KEYWORDS = re.compile(
    r"claude|anthropic|copilot|openai|codex|chatgpt|gpt|gemini|jules|google-labs|devin|cursor|aider|openhands|"
    r"all-hands|sweep|windsurf|codeium|cline|roo|kilo|goose|amazon|kiro|replit|qodo|codegen|coderabbit|"
    r"tabnine|cody|sourcegraph|\bai\b|\[bot\]|agent|llm|assistant|bot@|noreply@(?!github\.com)",
    re.I,
)
MARKER = re.compile(
    r"^.*(generated (with|by)|🤖|session:|assisted-by|ai-assisted|co-developed|made with).*$", re.I | re.M
)


def main(paths: list[str]) -> None:
    co: Counter[str] = Counter()
    ident: Counter[str] = Counter()
    marks: Counter[str] = Counter()
    trailer_keys: Counter[str] = Counter()
    for p in paths:
        repo = Path(p).name
        for c in iter_commits(Path(p)):
            for i in coauthor_lines(c.message):
                key = f"{i.name} <{i.email}>"
                if KEYWORDS.search(key):
                    co[key] += 1
            for name, email in ((c.author_name, c.author_email), (c.committer_name, c.committer_email)):
                key = f"{name} <{email}>"
                if KEYWORDS.search(key):
                    ident[key] += 1
            for m in MARKER.finditer(c.message):
                marks[re.sub(r"https?://\S+", "<url>", m.group(0).strip())[:100]] += 1
            for ln in c.message.splitlines():
                k = re.match(r"^([A-Z][A-Za-z-]{2,30}):\s", ln)
                if k:
                    trailer_keys[k.group(1)] += 1
        print(f"# scanned {repo}", file=sys.stderr)
    for title, ctr, n in (
        ("CO-AUTHOR", co, 60),
        ("AUTHOR/COMMITTER", ident, 40),
        ("MARKER", marks, 40),
        ("TRAILER KEYS", trailer_keys, 40),
    ):
        print(f"\n## {title}")
        for k, v in ctr.most_common(n):
            print(f"{v:6d}  {k}")


if __name__ == "__main__":
    main(sys.argv[1:])
