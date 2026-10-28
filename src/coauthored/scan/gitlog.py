"""Clone a repository with commit objects only and stream its log (MISSION §3.6)."""

from __future__ import annotations

import subprocess
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

_FIELDS = ("sha", "parents", "an", "ae", "cn", "ce", "ad", "cd", "body")
_FORMAT = "%x1f".join(("%H", "%P", "%an", "%ae", "%cn", "%ce", "%aI", "%cI", "%B"))


@dataclass(frozen=True)
class RawCommit:
    sha: str
    parents: tuple[str, ...]
    author_name: str
    author_email: str
    committer_name: str
    committer_email: str
    author_date: str
    committer_date: str
    message: str


def _git(*args: str, cwd: Path | None = None) -> str:
    out = subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)
    return out.stdout.decode("utf-8", errors="replace")


def clone(url: str, dest: Path, blob_filter: str = "tree:0") -> Path:
    """Bare, single-branch, partial clone of the default branch; fetch if it already exists."""
    if (dest / "HEAD").exists():
        _git("fetch", "--quiet", "--filter=" + blob_filter, "origin", cwd=dest)
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    _git("clone", "--quiet", "--bare", "--single-branch", "--filter=" + blob_filter, url, str(dest))
    return dest


def default_branch(repo: Path) -> str:
    return _git("symbolic-ref", "--short", "HEAD", cwd=repo).strip()


def head_sha(repo: Path, ref: str = "HEAD") -> str:
    return _git("rev-parse", ref, cwd=repo).strip()


def first_parent_shas(repo: Path, ref: str = "HEAD") -> set[str]:
    return set(_git("rev-list", "--first-parent", ref, cwd=repo).split())


def git_version() -> str:
    return _git("--version").strip()


def iter_commits(repo: Path, ref: str = "HEAD") -> Iterator[RawCommit]:
    """Every commit reachable from ``ref``, merges included (flagged downstream), streamed."""
    cmd = ["git", "log", "-z", "--no-color", "--encoding=UTF-8", f"--format={_FORMAT}", ref]
    proc = subprocess.Popen(cmd, cwd=repo, stdout=subprocess.PIPE)
    assert proc.stdout is not None
    buf = b""
    try:
        while chunk := proc.stdout.read(1 << 20):
            buf += chunk
            *records, buf = buf.split(b"\x00")
            for rec in records:
                yield _parse(rec)
        if buf.strip():
            yield _parse(buf)
    finally:
        proc.stdout.close()
        if proc.wait() != 0:
            raise subprocess.CalledProcessError(proc.returncode, cmd)


def _parse(record: bytes) -> RawCommit:
    parts = record.decode("utf-8", errors="replace").lstrip("\n").split("\x1f", len(_FIELDS) - 1)
    if len(parts) != len(_FIELDS):
        raise ValueError(f"malformed log record: {record[:80]!r}")
    sha, parents, an, ae, cn, ce, ad, cd, body = parts
    return RawCommit(sha, tuple(parents.split()), an, ae, cn, ce, ad, cd, body)
