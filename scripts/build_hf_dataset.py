"""Prepare the Hugging Face dataset (MISSION Phase 4; pushed only after STOP 2, by the user's decision).

Writes dist/hf/ with one parquet file of per-commit records per stratum, the aggregates, the samples, the
policy sheet, the manifest and the frozen configs, plus a dataset card. Per-commit records carry no identities
at all: the salted author and committer hashes are dropped (DECISIONS D16), and dates are converted to UTC so
that time-zone offsets, which are personal, are not published. Nothing here contacts the network.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import polars as pl
import yaml

from coauthored.analysis.aggregate import load_commits, mark_shared
from coauthored.scan.run import slug

OUT = Path("dist/hf")
DROP = ["author_h", "committer_h"]


def utc(column: str) -> pl.Expr:
    return (
        pl.col(column)
        .str.replace(r"Z$", "+00:00")
        .str.to_datetime("%Y-%m-%dT%H:%M:%S%:z", time_zone="UTC")
        .alias(column)
    )


def commits(cfg: dict[str, list[dict[str, str]]], key: str) -> pl.DataFrame:
    members = [
        r["repo"] for r in sorted(cfg[key], key=lambda r: (str(r.get("created_at", "9999")), r["repo"]))
    ]
    frames = [load_commits(Path("data/raw") / slug(r) / "commits.jsonl.zst", r) for r in members]
    out = []
    for df in mark_shared(frames):
        if df.is_empty():
            continue
        out.append(
            df.drop([c for c in DROP if c in df.columns])
            .with_columns(utc("author_date"), utc("committer_date"), pl.lit(key.upper()).alias("stratum"))
            .rename({"shared": "shared_with_earlier_repo"})
        )
    return pl.concat(out, how="diagonal_relaxed").sort("repo", "committer_date", "sha")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "commits").mkdir(parents=True)
    cfg = yaml.safe_load(Path("configs/repos.yaml").read_text())
    counts = {}
    for key in ("s1", "s2", "s3"):
        df = commits(cfg, key)
        assert not set(DROP) & set(df.columns)
        df.write_parquet(OUT / "commits" / f"{key}.parquet", compression="zstd")
        counts[key.upper()] = df.height
    for src in [
        *sorted(Path("data/aggregated").glob("*.parquet")),
        Path("data/survival.csv"),
        Path("data/size_sample.csv"),
        Path("data/policy.csv"),
        Path("data/manifest.json"),
        Path("data/s3_match.json"),
        Path("configs/signatures.yaml"),
        Path("configs/bots.yaml"),
        Path("configs/repos.yaml"),
        Path("configs/policy_overrides.yaml"),
    ]:
        if src.exists():
            dest = OUT / src.parent.name / src.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
    shutil.copy2("LICENSE-DATA", OUT / "LICENSE")
    files = sorted(p for p in OUT.rglob("*") if p.is_file())
    (OUT / "SHA256SUMS").write_text("".join(f"{sha256(p)}  {p.relative_to(OUT)}\n" for p in files))
    card = (
        Path("docs/dataset-card.md")
        .read_text()
        .replace("{{COUNTS}}", ", ".join(f"{k} {v:,}" for k, v in counts.items()))
    )
    (OUT / "README.md").write_text(card)
    size = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(json.dumps({"commits": counts, "files": len(files) + 2, "bytes": size}))


if __name__ == "__main__":
    main()
