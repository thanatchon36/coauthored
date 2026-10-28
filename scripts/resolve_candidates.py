"""Resolve candidate repositories to canonical names and fetch the metadata the inclusion rule needs.

Core GitHub API only (no clone, no commit messages read). Commit counts come from the default-branch commits
endpoint over a date window, read from the `Link` header with per_page=1. Output: cache/candidates_meta.json.
Usage: uv run python scripts/resolve_candidates.py configs/candidates.yaml [extra.yaml ...]
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

WINDOWS = {
    "commits_2024": ("2024-01-01T00:00:00Z", "2025-01-01T00:00:00Z"),
    "commits_12m": ("2025-10-01T00:00:00Z", "2026-10-01T00:00:00Z"),
}


def api(path: str, include_headers: bool = False) -> tuple[str, str]:
    args = ["gh", "api", "-X", "GET", path] + (["-i"] if include_headers else [])
    out = subprocess.run(args, capture_output=True, text=True)
    if out.returncode != 0:
        return "", out.stderr.strip()[:200]
    return out.stdout, ""


def commit_count(full: str, branch: str, since: str, until: str) -> int:
    raw, err = api(f"repos/{full}/commits?sha={branch}&since={since}&until={until}&per_page=1", True)
    if err:
        return -1
    head, _, body = raw.partition("\r\n\r\n") if "\r\n\r\n" in raw else raw.partition("\n\n")
    m = re.search(r'[?&]page=(\d+)>; rel="last"', head)
    if m:
        return int(m.group(1))
    return len(json.loads(body or "[]"))


def main(paths: list[str]) -> None:
    out_path = Path("cache/candidates_meta.json")
    meta: dict[str, dict] = json.loads(out_path.read_text()) if out_path.exists() else {}
    for p in paths:
        cfg = yaml.safe_load(Path(p).read_text())
        for stratum, groups in cfg.items():
            for layer, repos in groups.items():
                for name in repos:
                    if name in meta:
                        continue
                    raw, err = api(f"repos/{name}")
                    if err:
                        meta[name] = {"query": name, "stratum": stratum, "layer": layer, "error": err}
                        print(f"! {name}: {err[:80]}", file=sys.stderr)
                        continue
                    r = json.loads(raw)
                    rec = {
                        "query": name,
                        "stratum": stratum,
                        "layer": layer,
                        "full_name": r["full_name"],
                        "stars": r["stargazers_count"],
                        "archived": r["archived"],
                        "fork": r["fork"],
                        "language": r["language"],
                        "topics": r.get("topics", []),
                        "description": r.get("description") or "",
                        "default_branch": r["default_branch"],
                        "created_at": r["created_at"],
                        "pushed_at": r["pushed_at"],
                    }
                    for key, (since, until) in WINDOWS.items():
                        rec[key] = commit_count(r["full_name"], r["default_branch"], since, until)
                    meta[name] = rec
                    print(
                        f"{stratum} {r['full_name']:45s} *{rec['stars']:>7} c24={rec['commits_2024']:>6} "
                        f"c12m={rec['commits_12m']:>6} {rec['language']}",
                        file=sys.stderr,
                    )
                    out_path.parent.mkdir(exist_ok=True)
                    out_path.write_text(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main(sys.argv[1:])
