"""Size of attributed vs. unattributed commits (PREREGISTRATION §7, RQ6, exploratory).

A random sample of 2,000 window commits (primary specification, shared history removed), stratified by stratum
(S1, S2, S3) and attribution, 333 or 334 per cell, seed 20261028. Lines changed come from
`git show --shortstat` in the snapshot clones; the clones are treeless, so git fetches the trees and blobs
each diff needs from GitHub on demand (the same objects a `--filter=blob:none` clone holds).
Writes data/size_sample.csv (stratum, repository, month, attributed, files, insertions,
deletions).
Resumable: results are cached in cache/size/results.jsonl.
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import polars as pl
import yaml

from coauthored.analysis.aggregate import SENSITIVITY, filter_commits, load_commits, mark_shared
from coauthored.scan.run import slug

SEED = 20261028
TOTAL = 2000
CACHE = Path("cache/size/results.jsonl")
STAT = re.compile(r"(\d+) files? changed(?:, (\d+) insertions?\(\+\))?(?:, (\d+) deletions?\(-\))?")


def population() -> pl.DataFrame:
    cfg = yaml.safe_load(Path("configs/repos.yaml").read_text())
    out = []
    for key in ("s1", "s2", "s3"):
        members = [
            r["repo"] for r in sorted(cfg[key], key=lambda r: (str(r.get("created_at", "9999")), r["repo"]))
        ]
        frames = [load_commits(Path("data/raw") / slug(r) / "commits.jsonl.zst", r) for r in members]
        for df in mark_shared(frames):
            if df.is_empty():
                continue
            c = filter_commits(df.filter(~pl.col("shared")), SENSITIVITY[0])
            out.append(
                c.select("repo", "sha", "month", "attr").with_columns(pl.lit(key.upper()).alias("stratum"))
            )
    return pl.concat(out)


def sample(pop: pl.DataFrame) -> pl.DataFrame:
    cells = sorted(pop.select("stratum", "attr").unique().rows())
    base, extra = divmod(TOTAL, len(cells))
    parts = []
    for i, (stratum, attr) in enumerate(cells):
        cell = pop.filter((pl.col("stratum") == stratum) & (pl.col("attr") == attr)).sort("repo", "sha")
        k = min(base + (i < extra), cell.height)
        parts.append(cell.sample(k, seed=SEED + i))
    return pl.concat(parts)


def shortstat(repo: str, sha: str) -> dict[str, int | None]:
    proc = subprocess.run(
        ["git", "-C", f"work/{slug(repo)}.git", "show", "--shortstat", "--format=", "--no-renames", sha],
        capture_output=True,
        text=True,
        timeout=600,
    )
    if proc.returncode != 0:
        return {"files": None, "insertions": None, "deletions": None}
    m = STAT.search(proc.stdout)
    if not m:  # empty commit
        return {"files": 0, "insertions": 0, "deletions": 0}
    return {"files": int(m[1]), "insertions": int(m[2] or 0), "deletions": int(m[3] or 0)}


def main() -> None:
    picked = sample(population())
    done = {}
    if CACHE.exists():
        for line in CACHE.read_text().splitlines():
            row = json.loads(line)
            done[(row["repo"], row["sha"])] = row
    todo = [r for r in picked.iter_rows(named=True) if (r["repo"], r["sha"]) not in done]
    print(f"sample {picked.height}, cached {len(done)}, to fetch {len(todo)}", file=sys.stderr)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    # one worker per repository at a time: concurrent lazy fetches into the same clone contend on its lock
    by_repo: dict[str, list[dict[str, object]]] = {}
    for r in todo:
        by_repo.setdefault(str(r["repo"]), []).append(r)

    def work(rows: list[dict[str, object]]) -> list[dict[str, object]]:
        return [{**r, **shortstat(str(r["repo"]), str(r["sha"]))} for r in rows]

    with CACHE.open("a") as fh, ThreadPoolExecutor(max_workers=8) as pool:
        for n, rows in enumerate(pool.map(work, by_repo.values()), 1):
            for row in rows:
                fh.write(json.dumps(row) + "\n")
                done[(row["repo"], row["sha"])] = row
            fh.flush()
            print(f"repositories done {n}/{len(by_repo)}", file=sys.stderr)
    # the published file carries no commit SHA (PREREGISTRATION §11); cache/ keeps the identified rows
    fields = ["stratum", "repo", "month", "attr", "files", "insertions", "deletions"]
    with open("data/size_sample.csv", "w", newline="") as out:
        w = csv.DictWriter(out, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in picked.iter_rows(named=True):
            w.writerow(done[(r["repo"], r["sha"])])
    failed = sum(done[(r["repo"], r["sha"])]["files"] is None for r in picked.iter_rows(named=True))
    print(f"done: {picked.height} commits, {failed} failed", file=sys.stderr)


if __name__ == "__main__":
    main()
