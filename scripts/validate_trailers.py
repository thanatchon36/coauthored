"""Agreement between matcher.trailer_block and `git interpret-trailers --parse` on pilot commits.

For every commit with a co-author line: is each co-author line in the strict trailer block, by our rule and
by git's? Prints a 2x2 table over (commit, co-author line) pairs and up to 5 disagreeing SHAs.
"""

from __future__ import annotations

import subprocess
import sys
from collections import Counter
from pathlib import Path

from coauthored.scan.gitlog import iter_commits
from coauthored.signatures.matcher import COAUTHOR_RE, trailer_block


def git_trailers(message: str) -> set[str]:
    out = subprocess.run(
        ["git", "interpret-trailers", "--parse", "--no-divider"],
        input=message,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return {ln.strip().lower() for ln in out.splitlines() if ln.strip()}


def main(paths: list[str]) -> None:
    table: Counter[tuple[bool, bool]] = Counter()
    bad: list[str] = []
    for p in paths:
        for c in iter_commits(Path(p)):
            lines = [m.group(0).strip() for m in COAUTHOR_RE.finditer(c.message)]
            if not lines:
                continue
            ours = {ln.strip().lower() for ln in trailer_block(c.message)}
            theirs = git_trailers(c.message)
            for ln in lines:
                key = (ln.lower() in ours, ln.lower() in theirs)
                table[key] += 1
                if key[0] != key[1] and len(bad) < 5:
                    bad.append(f"{Path(p).name} {c.sha[:10]} ours={key[0]} git={key[1]}")
    n = sum(table.values())
    agree = table[(True, True)] + table[(False, False)]
    print(f"pairs={n} agree={agree} ({agree / n:.4f})")
    for k, v in sorted(table.items()):
        print(f"  ours={k[0]!s:5} git={k[1]!s:5} {v}")
    print("\n".join(bad))


if __name__ == "__main__":
    main(sys.argv[1:])
