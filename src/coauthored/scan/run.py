"""Scan one repository end to end: clone, stream, match, hash, write (MISSION §3.6)."""

from __future__ import annotations

import io
import json
import time
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import zstandard

from coauthored.bots import BotList
from coauthored.scan import gitlog
from coauthored.scan.records import build
from coauthored.signatures.catalogue import Catalogue


def slug(owner_repo: str) -> str:
    return owner_repo.replace("/", "__")


def scan_repo(
    owner_repo: str,
    catalogue: Catalogue,
    bots: BotList,
    salt: str,
    workdir: Path,
    rawdir: Path,
    url: str | None = None,
    ref: str = "HEAD",
) -> dict[str, Any]:
    t0 = time.monotonic()
    repo = gitlog.clone(url or f"https://github.com/{owner_repo}.git", workdir / (slug(owner_repo) + ".git"))
    t1 = time.monotonic()
    sha = gitlog.head_sha(repo, ref)
    first_parent = gitlog.first_parent_shas(repo, sha)
    out = rawdir / slug(owner_repo) / "commits.jsonl.zst"
    out.parent.mkdir(parents=True, exist_ok=True)
    n = n_attr = 0
    with out.open("wb") as fh, zstandard.ZstdCompressor(level=10).stream_writer(fh) as zw:
        text = io.TextIOWrapper(zw, encoding="utf-8")
        for raw in gitlog.iter_commits(repo, sha):
            rec = build(raw, catalogue, bots, salt, first_parent)
            n += 1
            n_attr += rec["attributed"]
            text.write(json.dumps(rec, separators=(",", ":")) + "\n")
        text.flush()
        text.detach()
    return {
        "repo": owner_repo,
        "default_branch": gitlog.default_branch(repo),
        "head_sha": sha,
        "n_commits_all": n,
        "n_attributed_all": n_attr,
        "catalogue_version": catalogue.version,
        "bots_version": bots.version,
        "git_version": gitlog.git_version(),
        # pilot throughput for the Phase 3 estimate; the clone is reused when it already exists
        "clone_seconds": round(t1 - t0, 1),
        "scan_seconds": round(time.monotonic() - t1, 1),
        "clone_bytes": _du(repo),
        "raw_bytes": out.stat().st_size,
        "scanned_at": datetime.now(UTC).isoformat(timespec="seconds"),
    }


def _du(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def read_records(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("rb") as fh, zstandard.ZstdDecompressor().stream_reader(fh) as zr:
        for line in io.TextIOWrapper(zr, encoding="utf-8"):
            yield json.loads(line)
