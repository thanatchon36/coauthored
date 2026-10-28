"""Per-commit records → repository-month aggregates (MISSION §4.2). The only shape that leaves the machine.

Primary specification (MISSION §3.1–3.3, DECISIONS D7): non-merge commits, author not a maintenance bot,
month of the committer date in UTC, lenient attribution. Every sensitivity analysis is a keyword argument.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import polars as pl

from coauthored.scan.run import read_records


@dataclass(frozen=True)
class Spec:
    name: str = "primary"
    date: str = "committer_date"  # or "author_date"
    merges: bool = False  # include merge commits
    first_parent_only: bool = False
    strict: bool = False  # strict trailer position for co-author signatures
    drop_maint_bots: bool = True
    start: str = "2023-01"
    end: str = "2026-09"


SENSITIVITY = [
    Spec(),
    Spec(name="author_date", date="author_date"),
    Spec(name="merges_included", merges=True),
    Spec(name="first_parent", first_parent_only=True),
    Spec(name="strict_trailers", strict=True),
    Spec(name="bots_included", drop_maint_bots=False),
]


def load_commits(path: Path, repo: str) -> pl.DataFrame:
    rows = list(read_records(path))
    if not rows:
        return pl.DataFrame()
    df = pl.DataFrame(rows, infer_schema_length=None)
    return df.with_columns(pl.lit(repo).alias("repo"))


def filter_commits(df: pl.DataFrame, spec: Spec) -> pl.DataFrame:
    month = (
        pl.col(spec.date)
        .str.to_datetime("%Y-%m-%dT%H:%M:%S%:z", time_zone="UTC")
        .dt.strftime("%Y-%m")
        .alias("month")
    )
    out = df.with_columns(month)
    if not spec.merges:
        out = out.filter(pl.col("n_parents") <= 1)
    if spec.first_parent_only:
        out = out.filter(pl.col("first_parent"))
    if spec.drop_maint_bots:
        out = out.filter(~pl.col("author_maint_bot"))
    flag = "attributed_strict" if spec.strict else "attributed"
    return out.filter(pl.col("month").is_between(pl.lit(spec.start), pl.lit(spec.end))).with_columns(
        pl.col(flag).alias("attr"),
        pl.when(pl.col(flag)).then(pl.col("tool")).otherwise(None).alias("attr_tool"),
    )


def repo_month(df: pl.DataFrame, spec: Spec) -> pl.DataFrame:
    """One row per repo-month: commits, attributed commits, active and attributing authors, mirror share."""
    c = filter_commits(df, spec)
    return (
        c.group_by("repo", "month")
        .agg(
            pl.len().alias("n"),
            pl.col("attr").sum().alias("n_attr"),
            pl.col("author_h").n_unique().alias("authors"),
            pl.col("author_h").filter(pl.col("attr")).n_unique().alias("authors_attr"),
            pl.col("mirror_export").sum().alias("n_mirror"),
        )
        .sort("repo", "month")
        .with_columns(pl.lit(spec.name).alias("spec"))
    )


def repo_month_tool(df: pl.DataFrame, spec: Spec) -> pl.DataFrame:
    c = filter_commits(df, spec).filter(pl.col("attr"))
    return (
        c.group_by("repo", "month", "attr_tool")
        .agg(pl.len().alias("n_attr"))
        .rename({"attr_tool": "tool"})
        .sort("repo", "month", "tool")
        .with_columns(pl.lit(spec.name).alias("spec"))
    )


def spec_dict(spec: Spec) -> dict[str, object]:
    return asdict(spec)
