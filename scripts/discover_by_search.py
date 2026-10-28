"""Signature discovery beyond the pilots via GitHub commit search (MISSION §3.4).

For each keyword, read up to 100 matching public commits and count identities (co-author lines, author,
committer) and trailer/marker lines that contain the keyword. Aggregated counts only, written to
cache/discovery_search.json (git-ignored). Uses the user's `gh` login; 30 searches/min limit respected.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

from coauthored.signatures.matcher import coauthor_lines

KEYWORDS = [
    "cursoragent",
    "aider",
    "openhands",
    "all-hands.dev",
    "google-labs-jules",
    "devin-ai-integration",
    "noreply@openai.com",
    "codex@openai.com",
    "chatgpt-codex-connector",
    "gemini-cli",
    "gemini-code-assist",
    "amazon-q-developer",
    "kiro",
    "windsurf",
    "codeium",
    "cline",
    "roo code",
    "kilocode",
    "goose",
    "opencode",
    "ampcode",
    "amp-thread",
    "warp.dev",
    "junie",
    "factory-droid",
    "letta",
    "sweep-ai",
    "qodo",
    "coderabbit",
    "claude[bot]",
    "copilot-swe-agent",
    "Copilot-Session",
    "Claude-Session",
    "noreply@anthropic.com",
    "crush",
    "zed",
    "augment",
    "tabnine",
    "replit",
    "lovable",
    "bolt.new",
    "v0",
    "trae",
    "qwen-code",
    "kimi",
]


def search(q: str) -> list[dict] | None:
    """One search with backoff on the secondary rate limit; None if it keeps failing."""
    for wait in (60, 120, 240, 480):
        out = subprocess.run(
            ["gh", "api", "-X", "GET", "search/commits", "-f", f"q={q}", "-f", "per_page=100"],
            capture_output=True,
            text=True,
        )
        if out.returncode == 0:
            return json.loads(out.stdout).get("items", [])
        print(f"! {q}: {out.stderr.strip()[:80]} (sleep {wait}s)", file=sys.stderr)
        time.sleep(wait)
    return None


def main() -> None:
    cache = Path("cache/discovery_search.json")
    result: dict[str, dict] = json.loads(cache.read_text()) if cache.exists() else {}
    for kw in KEYWORDS:
        if kw in result:
            continue
        kre = re.compile(re.escape(kw), re.I)
        found = search(f'"{kw}"')
        if found is None:
            continue
        items = found
        ids: Counter[str] = Counter()
        lines: Counter[str] = Counter()
        repos = set()
        for it in items:
            c = it["commit"]
            msg = c["message"]
            hit = False
            for i in coauthor_lines(msg):
                k = f"coauthor: {i.name} <{i.email}>"
                if kre.search(k):
                    ids[k] += 1
                    hit = True
            for role in ("author", "committer"):
                k = f"{role}: {c[role]['name']} <{c[role]['email']}>"
                if kre.search(k):
                    ids[k] += 1
                    hit = True
            for ln in msg.splitlines():
                is_coauthor = ln.lower().lstrip("*- ").startswith("co-authored-by")
                is_marker = re.match(r"^\s*([A-Za-z-]+:|🤖|generated|assisted)", ln, re.I)
                if kre.search(ln) and not is_coauthor and is_marker:
                    lines[re.sub(r"https?://\S+", "<url>", ln.strip())[:100]] += 1
                    hit = True
            if hit:
                repos.add(it["repository"]["full_name"])
        result[kw] = {
            "n_items": len(items),
            "n_repos_with_hit": len(repos),
            "identities": ids.most_common(8),
            "lines": lines.most_common(5),
        }
        print(
            f"{kw:28s} items={len(items):3d} repos={len(repos):3d} top={ids.most_common(2)}", file=sys.stderr
        )
        cache.parent.mkdir(exist_ok=True)
        cache.write_text(json.dumps(result, indent=1, ensure_ascii=False))
        time.sleep(8)


if __name__ == "__main__":
    main()
