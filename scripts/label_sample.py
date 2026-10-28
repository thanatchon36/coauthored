"""Scanner validation sample on the pilot repos (MISSION §4.5).

`draw`: 200 pilot commits, seeded: 80 the scanner attributes, 70 near-misses (message or identity
mentions an AI
tool word but the scanner does not attribute), 50 random others. Writes a condensed local sheet
(cache/label_sheet.txt: identities, attribution-like lines and keyword lines only) and the sample order
(cache/label_sample.json). Labels are written by a reader who sees the sheet, not the scanner verdict, to
cache/labels.json as {"<sha>": true|false}.
`score`: compare labels with the scanner; write docs/label-sample.csv (repo, sha, label, scanner) — no
identities — and print precision and recall.
"""

from __future__ import annotations

import csv
import json
import random
import re
import sys
from pathlib import Path

from coauthored.scan.gitlog import iter_commits
from coauthored.signatures import catalogue
from coauthored.signatures.matcher import Identity, match_commit

WORDS = re.compile(
    r"claude|anthropic|copilot|openai|codex|gpt|gemini|jules|devin|cursor|aider|openhands|amp|kiro|cline|"
    r"opencode|kilo|letta|codeium|windsurf|\[bot\]|generated|co-authored|assisted-by|session:",
    re.I,
)
SEED = 20261028


def _commits() -> list[tuple[str, object]]:
    out = []
    for p in sorted(Path("work").glob("*__*.git")):
        repo = p.name.removesuffix(".git").replace("__", "/")
        out += [(repo, c) for c in iter_commits(p)]
    return out


def draw() -> None:
    cat = catalogue.load(Path("configs/signatures.yaml"))
    attributed, near, other = [], [], []
    for repo, c in _commits():
        a = Identity(c.author_name, c.author_email)  # type: ignore[attr-defined]
        k = Identity(c.committer_name, c.committer_email)  # type: ignore[attr-defined]
        hit = match_commit(cat, a, k, c.message).attributed  # type: ignore[attr-defined]
        blob = f"{a.name} {a.email} {k.name} {k.email} {c.message}"  # type: ignore[attr-defined]
        (attributed if hit else near if WORDS.search(blob) else other).append((repo, c))
    rng = random.Random(SEED)
    sample = rng.sample(attributed, 80) + rng.sample(near, 70) + rng.sample(other, 50)
    rng.shuffle(sample)
    lines = []
    for i, (repo, c) in enumerate(sample):
        msg = c.message  # type: ignore[attr-defined]
        keep = [
            ln.strip() for ln in msg.splitlines()[1:] if WORDS.search(ln) or re.match(r"^\s*[\w-]+-by:", ln)
        ]
        lines.append(
            f"[{i}] {repo} {c.sha[:12]}\n  author: {c.author_name} <{c.author_email}>\n"  # type: ignore[attr-defined]
            f"  committer: {c.committer_name} <{c.committer_email}>\n"  # type: ignore[attr-defined]
            f"  subject: {msg.splitlines()[0][:100] if msg else ''}\n"
            + "".join(f"  | {ln[:140]}\n" for ln in keep[:12])
        )
    Path("cache/label_sheet.txt").write_text("\n".join(lines))
    Path("cache/label_sample.json").write_text(json.dumps([[r, c.sha] for r, c in sample]))  # type: ignore[attr-defined]
    print(f"attributed={len(attributed)} near={len(near)} other={len(other)}; sheet: cache/label_sheet.txt")


def score() -> None:
    cat = catalogue.load(Path("configs/signatures.yaml"))
    sample = json.loads(Path("cache/label_sample.json").read_text())
    labels = json.loads(Path("cache/labels.json").read_text())
    by_sha = {c.sha: c for _r, c in _commits()}
    tp = fp = fn = tn = 0
    rows = []
    for repo, sha in sample:
        c = by_sha[sha]
        a, k = Identity(c.author_name, c.author_email), Identity(c.committer_name, c.committer_email)
        s = match_commit(cat, a, k, c.message).attributed
        lab = labels[sha[:12]]
        tp += s and lab
        fp += s and not lab
        fn += (not s) and lab
        tn += (not s) and (not lab)
        rows.append({"repo": repo, "sha": sha, "label": int(lab), "scanner": int(s)})
    with open("docs/label-sample.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["repo", "sha", "label", "scanner"])
        w.writeheader()
        w.writerows(rows)
    print(
        f"tp={tp} fp={fp} fn={fn} tn={tn} "
        f"precision={tp / max(tp + fp, 1):.4f} recall={tp / max(tp + fn, 1):.4f}"
    )
    for r in rows:
        if r["label"] != r["scanner"]:
            print("disagree:", r["repo"], r["sha"][:12], "label", r["label"], "scanner", r["scanner"])


if __name__ == "__main__":
    {"draw": draw, "score": score}[sys.argv[1]]()
