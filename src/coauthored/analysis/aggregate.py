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
    exclude_signatures: tuple[str, ...] = ()  # catalogue ids that do not count (post-hoc analyses only)


SENSITIVITY = [
    Spec(),
    Spec(name="author_date", date="author_date"),
    Spec(name="merges_included", merges=True),
    Spec(name="first_parent", first_parent_only=True),
    Spec(name="strict_trailers", strict=True),
    Spec(name="bots_included", drop_maint_bots=False),
]

# Not pre-registered (DEVIATIONS 11): applied review suggestions, where a person clicks "commit suggestion"
# on a review bot's comment and GitHub adds the bot as co-author, are not a coding agent writing the change.
REVIEW_SUGGESTIONS = ("copilot-coauthor", "gemini-code-assist-coauthor")
POST_HOC = [Spec(name="no_review_suggestions", exclude_signatures=REVIEW_SUGGESTIONS)]


def load_commits(path: Path, repo: str) -> pl.DataFrame:
    rows = list(read_records(path))
    if not rows:
        return pl.DataFrame()
    df = pl.DataFrame(rows, infer_schema_length=None)
    if "bare_assisted" not in df.columns:  # records written before the indicator existed
        df = df.with_columns(pl.lit(False).alias("bare_assisted"))
    return df.with_columns(pl.lit(repo).alias("repo"))


def mark_shared(frames: list[pl.DataFrame]) -> list[pl.DataFrame]:
    """Flag commits already seen in an earlier repository of the list (PREREGISTRATION §3, shared history).

    ``frames`` must be ordered by repository creation date; the earliest repository keeps the commit.
    """
    seen: set[str] = set()
    out = []
    for df in frames:
        shas = df["sha"].to_list()
        out.append(df.with_columns(pl.Series("shared", [sha in seen for sha in shas])))
        seen.update(shas)
    return out


def reverts(df: pl.DataFrame, spec: Spec, reverted_sha: pl.Series | None = None) -> pl.DataFrame:
    """Per repository, month and attribution status: window commits and how many were later reverted (RQ6).

    By month so that attributed and unattributed commits can be compared at equal exposure time.
    ``reverted_sha``: the revert targets to look up (default: those in ``df``)."""
    targets = df["reverted_sha"] if reverted_sha is None else reverted_sha
    reverted = {r for r in targets.to_list() if r}
    prefixes = {r[:7] for r in reverted}
    c = filter_commits(df, spec).with_columns(
        pl.col("sha")
        .map_elements(
            lambda sha: sha[:7] in prefixes and any(sha.startswith(r) for r in reverted),
            return_dtype=pl.Boolean,
        )
        .alias("was_reverted")
    )
    return (
        c.group_by("repo", "month", "attr")
        .agg(pl.len().alias("n"), pl.col("was_reverted").sum().alias("n_reverted"))
        .with_columns(pl.lit(spec.name).alias("spec"))
        .sort("repo", "month", "attr")
    )


def month_utc(column: str) -> pl.Expr:
    """UTC calendar month of an ISO-8601 git date."""
    return (
        pl.col(column)
        # newer git writes a UTC offset as "Z" in --date=iso-strict output, older git as "+00:00"
        .str.replace(r"Z$", "+00:00")
        .str.to_datetime("%Y-%m-%dT%H:%M:%S%:z", time_zone="UTC")
        .dt.strftime("%Y-%m")
        .alias("month")
    )


def filter_commits(df: pl.DataFrame, spec: Spec) -> pl.DataFrame:
    out = df.with_columns(month_utc(spec.date))
    if not spec.merges:
        out = out.filter(pl.col("n_parents") <= 1)
    if spec.first_parent_only:
        out = out.filter(pl.col("first_parent"))
    if spec.drop_maint_bots:
        out = out.filter(~pl.col("author_maint_bot"))
    flag = pl.col("attributed_strict" if spec.strict else "attributed")
    if spec.exclude_signatures:
        ids = pl.col("signature_ids").cast(pl.List(pl.String))  # list[null] in repositories with no signature
        others = ids.list.set_difference(list(spec.exclude_signatures)).list.len() > 0
        flag = flag & others
    return out.filter(pl.col("month").is_between(pl.lit(spec.start), pl.lit(spec.end))).with_columns(
        flag.alias("attr"),
        pl.when(flag).then(pl.col("tool")).otherwise(None).alias("attr_tool"),
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
            pl.col("bare_assisted").sum().alias("n_bare_assisted"),
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
