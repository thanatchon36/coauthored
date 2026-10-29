"""Living dashboard (MISSION §6): the paper's monthly series, extended past the pre-registered window.

Reads per-commit records from a fresh scan of the frozen repository lists, counts them with the paper's
primary specification (``Spec``) up to the last complete month, and writes one self-contained page with
an inline SVG chart and a table. It is labelled *post-registration, not part of the paper*: nothing here
feeds ``results/numbers.json``.
"""

from __future__ import annotations

import html
import io
from datetime import date
from pathlib import Path
from typing import Any

import polars as pl

from coauthored.analysis.aggregate import Spec, load_commits, mark_shared, repo_month
from coauthored.scan.run import slug

WINDOW_END = "2026-09"  # last month of the pre-registered window


def last_complete_month(today: date) -> str:
    y, m = (today.year, today.month - 1) if today.month > 1 else (today.year - 1, 12)
    return f"{y}-{m:02d}"


def series(strata: dict[str, list[str]], rawdir: Path, end: str) -> pl.DataFrame:
    """Pooled monthly share per stratum: stratum, month, n, n_attr, share (shared history counted once)."""
    spec = Spec(end=end)
    parts = []
    for stratum, members in strata.items():
        frames = [load_commits(rawdir / slug(r) / "commits.jsonl.zst", r) for r in members]
        for df in mark_shared(frames):
            if not df.is_empty():
                rm = repo_month(df.filter(~pl.col("shared")), spec)
                parts.append(rm.with_columns(stratum=pl.lit(stratum)))
    return (
        pl.concat(parts)
        .group_by("stratum", "month")
        .agg(pl.col("n").sum(), pl.col("n_attr").sum())
        .with_columns((pl.col("n_attr") / pl.col("n")).alias("share"))
        .sort("stratum", "month")
    )


def chart(s: pl.DataFrame, start: str = "2024-01") -> str:
    """Inline SVG of the monthly share per stratum, with the end of the pre-registered window marked."""
    import matplotlib.pyplot as plt

    from coauthored.analysis import figures as fg

    fg.setup()
    d = s.filter(pl.col("month") >= start)
    months = sorted(d["month"].unique().to_list())
    fig, ax = plt.subplots(figsize=(fg.WIDTH, 2.6))
    for st, colour in fg.STRATUM.items():
        g = d.filter(pl.col("stratum") == st).sort("month")
        if g.is_empty():
            continue
        x = [months.index(m) for m in g["month"]]
        ax.plot(x, g["share"], color=colour, lw=1.4, label=fg.STRATUM_NAME[st])
    if WINDOW_END in months and months[-1] > WINDOW_END:
        edge = months.index(WINDOW_END) + 0.5
        ax.axvline(edge, color=fg.MUTED, lw=0.6, ls="--")
        ax.annotate(
            "end of pre-registered window",
            (edge, 1),
            xycoords=("data", "axes fraction"),
            xytext=(-3, -3),
            textcoords="offset points",
            ha="right",
            va="top",
            fontsize=7,
            color=fg.MUTED,
        )
    fg._pct(ax)
    ax.set_ylim(0, None)
    ax.set_ylabel("AI-attributed share of commits")
    fg._month_ticks(ax, months)
    ax.legend(loc="upper left", frameon=False, fontsize=7)
    buf = io.StringIO()
    fig.savefig(buf, format="svg", bbox_inches="tight", pad_inches=0.02, metadata={"Date": None})
    plt.close(fig)
    svg = buf.getvalue()
    return svg[svg.index("<svg") :]


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>coauthored dashboard</title>
<style>
:root {{ --paper: #fbfbf9; --ink: #17191c; --ink-2: #4c5058; --rule: #dcdcd6; --plate: #ffffff;
  --warn-soft: #f6eedd; --warn: #8a5a12; color-scheme: light; }}
@media (prefers-color-scheme: dark) {{ :root {{ --paper: #15171a; --ink: #e8e9ec; --ink-2: #a6abb4;
  --rule: #30343a; --plate: #f4f4f2; --warn-soft: #33291a; --warn: #e7bd73; color-scheme: dark; }} }}
body {{ margin: 0; background: var(--paper); color: var(--ink);
  font: 17px/1.55 "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif; }}
main {{ max-width: 46rem; margin: 0 auto; padding: 32px 16px 56px; }}
h1 {{ font-size: 1.6rem; line-height: 1.25; margin: 0 0 8px; }}
.label {{ background: var(--warn-soft); border-left: 3px solid var(--warn); padding: 10px 14px;
  margin: 16px 0; }}
.plate {{ background: var(--plate); border-radius: 6px; padding: 8px; }}
.plate svg {{ width: 100%; height: auto; display: block; }}
table {{ border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; font-size: 0.95rem; }}
th, td {{ padding: 4px 8px; border-bottom: 1px solid var(--rule); text-align: right; }}
th:first-child, td:first-child {{ text-align: left; }}
.wrap {{ overflow-x: auto; }}
footer, .note {{ color: var(--ink-2); font-size: 0.9rem; }}
a {{ color: inherit; }}
</style>
</head>
<body>
<main>
<h1>AI-attributed commits, month by month</h1>
<p class="note">Updated {updated} · data to {end} · <a href="../paper/">the paper</a> ·
<a href="https://github.com/thanatchon36/coauthored">code</a></p>
<p class="label"><b>Post-registration, not part of the paper.</b> The same repositories, signature catalogue
and counting rules as the paper, re-scanned every month. Months after {window_end} were not pre-registered,
and later commits can change earlier months slightly.</p>
<div class="plate">{svg}</div>
<h2>Last twelve months</h2>
<div class="wrap"><table>
<thead><tr><th>month</th>{heads}</tr></thead>
<tbody>
{rows}
</tbody></table></div>
<p class="note">Pooled share of non-merge commits on the default branch that carry an AI co-author trailer,
are made by an AI-agent account, or carry a tool's marker. AI-attributed commits are a lower bound on AI
involvement: an attributed commit is not a commit "written by AI".</p>
<footer>Independent personal research. Public data only. Does not represent the views of any employer or
institution.</footer>
</main>
</body>
</html>
"""


def _cell(r: dict[str, Any] | None) -> str:
    if r is None:
        return "<td>–</td>"
    return f"<td>{100 * r['share']:.1f}%<br><small>{r['n_attr']:,} of {r['n']:,}</small></td>"


def page(s: pl.DataFrame, end: str, updated: str) -> str:
    from coauthored.analysis.figures import STRATUM_NAME

    strata = [k for k in STRATUM_NAME if k in set(s["stratum"])]
    months = sorted(s["month"].unique().to_list())[-12:]
    cell = {(r["stratum"], r["month"]): r for r in s.iter_rows(named=True)}
    rows = []
    for m in reversed(months):
        tds = "".join(_cell(cell.get((k, m))) for k in strata)
        rows.append(f"<tr><td>{m}</td>{tds}</tr>")
    return PAGE.format(
        updated=html.escape(updated),
        end=html.escape(end),
        window_end=WINDOW_END,
        svg=chart(s),
        heads="".join(f"<th>{html.escape(STRATUM_NAME[k])}</th>" for k in strata),
        rows="\n".join(rows),
    )


def write(strata: dict[str, list[str]], rawdir: Path, out: Path, today: date) -> Path:
    end = last_complete_month(today)
    out.mkdir(parents=True, exist_ok=True)
    s = series(strata, rawdir, end)
    s.write_csv(out / "monthly.csv")
    (out / "index.html").write_text(page(s, end, today.isoformat()), encoding="utf-8")
    return out / "index.html"
