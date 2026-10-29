"""Prepare the Hugging Face dataset (MISSION Phase 4; pushed only after STOP 2, by the user's decision).

Writes dist/hf/ with the repository-month aggregates, the survival and size samples (no PR numbers, no
commit SHAs), the policy sheet, the manifest and the frozen configs, plus a dataset card. PREREGISTRATION §11
says only repository-month aggregates are published, so no per-commit records are released (DECISIONS D16);
the aggregates rebuild every table and figure of the paper. Nothing here contacts the network.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import polars as pl

OUT = Path("dist/hf")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
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
    month = pl.read_parquet(OUT / "aggregated" / "repo_month.parquet")
    primary = month.filter((pl.col("spec") == "primary") & ~pl.col("dedup"))
    commits = primary.group_by("stratum").agg(pl.col("n").sum())
    counts = {r["stratum"]: int(r["n"]) for r in commits.sort("stratum").iter_rows(named=True)}
    card = (
        Path("docs/dataset-card.md")
        .read_text()
        .replace("{{COUNTS}}", ", ".join(f"{k} {v:,}" for k, v in counts.items()))
    )
    (OUT / "README.md").write_text(card)
    size = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(json.dumps({"window_commits": counts, "files": len(files) + 2, "bytes": size}))


if __name__ == "__main__":
    main()
