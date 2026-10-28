"""Command-line interface."""

from __future__ import annotations

import json
from pathlib import Path

import polars as pl
import typer
import yaml

from coauthored import __version__, guard
from coauthored import bots as bots_mod
from coauthored.analysis.aggregate import (
    SENSITIVITY,
    Spec,
    load_commits,
    mark_shared,
    repo_month,
    repo_month_tool,
    reverts,
)
from coauthored.scan.identity import load_salt
from coauthored.scan.run import scan_repo, slug
from coauthored.signatures import catalogue as cat_mod

app = typer.Typer(no_args_is_help=True, help="Count AI-attributed commits in git history.")

CATALOGUE = Path("configs/signatures.yaml")
BOTS = Path("configs/bots.yaml")
WORK = Path("work")
RAW = Path("data/raw")


@app.callback()
def _main() -> None:
    guard.check()


@app.command()
def version() -> None:
    """Print the version."""
    typer.echo(__version__)


@app.command()
def signatures(catalogue: Path = CATALOGUE, verify: bool = False) -> None:
    """List the signature catalogue; with --verify, fail if any entry lacks 3 evidence URLs."""
    cat = cat_mod.load(catalogue)
    for s in cat.signatures:
        pattern = s.text or " ".join(p for p in (s.name, s.email) if p)
        typer.echo(f"{s.id:34s} {s.kind:9s} {s.tool:22s} evidence={len(set(s.evidence))}  {pattern}")
    if verify and (bad := cat.unqualified()):
        typer.echo(f"unqualified: {', '.join(s.id for s in bad)}", err=True)
        raise typer.Exit(1)


def _repos_from(config: Path | None, repos: list[str]) -> list[str]:
    out = list(repos)
    if config:
        cfg = yaml.safe_load(config.read_text(encoding="utf-8"))
        for key in ("pilots", "s1", "s2", "s3"):
            for r in cfg.get(key, []) or []:
                out.append(r if isinstance(r, str) else r["repo"])
    return out


@app.command()
def scan(
    repos: list[str] = typer.Argument(None, help="owner/repo …"),  # noqa: B008
    config: Path | None = typer.Option(None, help="YAML with pilots/s1/s2/s3 lists"),  # noqa: B008
    catalogue: Path = CATALOGUE,
    bots: Path = BOTS,
    manifest: Path = Path("data/manifest.json"),
    workdir: Path = WORK,
    rawdir: Path = RAW,
    url_template: str = typer.Option("https://github.com/{repo}.git", help="clone URL; {repo} = owner/repo"),
) -> None:
    """Clone (commit objects only), match and write hashed per-commit records."""
    cat = cat_mod.load(catalogue)
    botlist = bots_mod.load(bots)
    salt = load_salt()
    entries = json.loads(manifest.read_text()) if manifest.exists() else {"repos": {}}
    for repo in _repos_from(config, repos or []):
        entry = scan_repo(repo, cat, botlist, salt, workdir, rawdir, url=url_template.format(repo=repo))
        entries["repos"][repo] = entry
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps(entries, indent=1, sort_keys=True))
        typer.echo(
            f"{repo:45s} commits={entry['n_commits_all']:>7} attributed={entry['n_attributed_all']:>6}"
        )


@app.command()
def aggregate(
    repos: list[str] = typer.Argument(None),  # noqa: B008
    config: Path | None = typer.Option(None),  # noqa: B008
    rawdir: Path = RAW,
    out: Path = Path("data/aggregated"),
) -> None:
    """Repo-month aggregates for every pre-registered specification (parquet).

    Each stratum's repositories are read in creation order; ``dedup`` rows drop commits already present in an
    earlier repository of the same stratum (pooled figures), ``dedup = false`` rows keep full histories.
    """
    out.mkdir(parents=True, exist_ok=True)
    rm, tools, rev = [], [], []
    for stratum, members in _strata_from(config, repos or []).items():
        frames = [load_commits(rawdir / slug(r) / "commits.jsonl.zst", r) for r in members]
        for df in mark_shared(frames):
            if df.is_empty():
                continue
            for spec in SENSITIVITY:
                for dedup, part in ((False, df), (True, df.filter(~pl.col("shared")))):
                    tag = {"dedup": pl.lit(dedup), "stratum": pl.lit(stratum)}
                    rm.append(repo_month(part, spec).with_columns(**tag))
                    tools.append(repo_month_tool(part, spec).with_columns(**tag))
            rev.append(reverts(df, SENSITIVITY[0]).with_columns(stratum=pl.lit(stratum)))
    pl.concat(rm).write_parquet(out / "repo_month.parquet")
    pl.concat(tools).write_parquet(out / "repo_month_tool.parquet")
    pl.concat(rev).write_parquet(out / "reverts.parquet")
    typer.echo(f"wrote {out}/repo_month.parquet, repo_month_tool.parquet and reverts.parquet")


def _strata_from(config: Path | None, repos: list[str]) -> dict[str, list[str]]:
    """Stratum -> repositories ordered by creation date (unknown dates last, then by name)."""
    out: dict[str, list[str]] = {}
    if repos:
        out["adhoc"] = list(repos)
    if config:
        cfg = yaml.safe_load(config.read_text(encoding="utf-8"))
        for key in ("pilots", "s1", "s2", "s3"):
            entries = cfg.get(key) or []
            rows = [
                (r, "9999") if isinstance(r, str) else (r["repo"], str(r.get("created_at", "9999")))
                for r in entries
            ]
            if rows:
                out[key.upper()] = [r for r, _ in sorted(rows, key=lambda x: (x[1], x[0]))]
    return out


@app.command()
def report(
    repos: list[str] = typer.Argument(None, help="owner/repo …"),  # noqa: B008
    org: str | None = typer.Option(None, help="every public, non-fork, non-archived repo of an org"),
    since: str = "2024-01",
    rawdir: Path = RAW,
) -> None:
    """Scan and print a Markdown monthly table of attributed share for your own repos or organisation."""
    targets = list(repos or [])
    if org:
        import subprocess

        listing = subprocess.run(
            [
                "gh",
                "repo",
                "list",
                org,
                "--limit",
                "1000",
                "--no-archived",
                "--source",
                "--visibility",
                "public",
                "--json",
                "nameWithOwner",
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        targets += [r["nameWithOwner"] for r in json.loads(listing)]
    cat = cat_mod.load(CATALOGUE)
    botlist = bots_mod.load(BOTS)
    salt = load_salt()
    frames = []
    for repo in targets:
        scan_repo(repo, cat, botlist, salt, WORK, rawdir)
        df = load_commits(rawdir / slug(repo) / "commits.jsonl.zst", repo)
        frames.append(repo_month(df, Spec(start=since, end="9999-12")))
    t = pl.concat(frames).group_by("month").agg(pl.col("n").sum(), pl.col("n_attr").sum()).sort("month")
    typer.echo("| month | commits | AI-attributed | share |\n|---|---:|---:|---:|")
    for row in t.iter_rows(named=True):
        typer.echo(f"| {row['month']} | {row['n']} | {row['n_attr']} | {row['n_attr'] / row['n']:.1%} |")
    typer.echo("\nAttributed commits are a lower bound: tools can be configured not to attribute.")


@app.command()
def analyze(draws: int = 2000) -> None:
    """Every table, figure and number in the paper, from committed aggregates (no network)."""
    from coauthored.analysis.run import analyze as run

    numbers = run(b=draws)
    for r in numbers["hypotheses"]:
        verdict = "supported" if r["supported"] else "not supported"
        if "exploratory" in r["statement"]:
            verdict = "exploratory, " + ("positive" if r["supported"] else "not positive")
        typer.echo(f"{r['hypothesis']}: {verdict} (estimate {r['estimate']})")


@app.command()
def paper() -> None:
    """Fill paper/paper.md from results/numbers.json and build paper/coauthored.pdf (pandoc + typst)."""
    from coauthored.paper import build

    typer.echo(f"wrote {build()}")
