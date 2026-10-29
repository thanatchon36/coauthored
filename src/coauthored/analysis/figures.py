"""Paper figures F1–F6 and F8 (MISSION §7.4), house style shared with the author's other papers.

Libertinus Serif (vendored in ``figures/fonts``), sized so 8 pt prints at 8 pt at a 16 cm text width; no
in-figure titles (panel labels only); legends above the axes, inside an empty corner, or direct labels; one
fixed colour per stratum and per tool (Okabe–Ito). Every figure is written as SVG with text as outlines (PDF
build) and 300-dpi PNG. Every share is a share of *AI-attributed* commits, a lower bound; captions say so.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from matplotlib import font_manager
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from coauthored.analysis.hypotheses import wilson

ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = ROOT / "figures" / "fonts"
INK, MUTED, GRID = "#1a1a1a", "#5a5a5a", "#e3e3e3"
STRATUM = {"S1": "#0072B2", "S2": "#D55E00", "S3": "#6e6e6e"}
STRATUM_NAME = {
    "S1": "S1 model infrastructure",
    "S2": "S2 coding-agent harnesses",
    "S3": "S3 matched controls",
}
# the nine tools with the most attributed commits in 2025-01..2026-09 (all strata); the rest are "Other"
TOOL = {
    "Claude Code": "#D55E00",
    "GitHub Copilot": "#0072B2",
    "OpenHands": "#56B4E9",
    "Qwen Code": "#8C564B",
    "OpenAI Codex": "#009E73",
    "Gemini Code Assist": "#E69F00",
    "Warp": "#F0E442",
    "Cursor": "#CC79A7",
    "OpenCode": "#332288",
}
OTHER = "#bdbdbd"
WIDTH = 16.0 / 2.54
DOT: dict[str, Any] = {"marker": "o", "ms": 3.6, "mec": "white", "mew": 0.6, "ls": "none"}
BAND_ALPHA = 0.13
Q3 = ("2026-07", "2026-09")
DASH = (0, (3, 2))


def setup() -> None:
    for p in sorted(FONT_DIR.glob("LibertinusSerif-*.otf")):
        font_manager.fontManager.addfont(str(p))
    plt.rcParams.update(
        {
            "svg.hashsalt": "coauthored",  # stable element ids: byte-identical SVGs across runs
            "font.family": "Libertinus Serif",
            "font.size": 8.5,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.6,
            "axes.edgecolor": "#3a3a3a",
            "axes.grid": True,
            "axes.grid.axis": "y",
            "grid.color": GRID,
            "grid.linewidth": 0.6,
            "axes.axisbelow": True,
            "xtick.major.size": 2.5,
            "ytick.major.size": 2.5,
            "text.color": INK,
            "axes.labelcolor": INK,
            "legend.frameon": False,
            "legend.handlelength": 1.6,
            "svg.fonttype": "path",
        }
    )


def save(fig: Figure, out: Path, name: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{name}.svg", bbox_inches="tight", pad_inches=0.02, metadata={"Date": None})
    fig.savefig(out / f"{name}.png", dpi=300, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


def panel(ax: Axes, letter: str, text: str | None = None) -> None:
    ax.annotate(
        letter,
        (0, 1),
        xycoords="axes fraction",
        xytext=(0, 12),
        textcoords="offset points",
        ha="left",
        va="top",
        fontsize=9,
        weight="bold",
    )
    if text:
        ax.annotate(
            text,
            (0, 1),
            xycoords="axes fraction",
            xytext=(14, 12),
            textcoords="offset points",
            ha="left",
            va="top",
            fontsize=8,
        )


def _pct(ax: Axes, axis: str = "y") -> None:
    fmt = mpl.ticker.PercentFormatter(1.0, decimals=0)
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(fmt)


def _months(lo: str, hi: str) -> list[str]:
    y, m = map(int, lo.split("-"))
    out = []
    while f"{y}-{m:02d}" <= hi:
        out.append(f"{y}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


MONTH = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _month_ticks(ax: Axes, months: list[str], every: tuple[str, ...] = ("01", "07")) -> None:
    """Ticks at the given months of the year; the year is printed under January (or under the first tick)."""
    idx = [i for i, m in enumerate(months) if m[5:] in every]
    labels = []
    for k, i in enumerate(idx):
        name = MONTH[int(months[i][5:]) - 1]
        labels.append(f"{name}\n{months[i][:4]}" if months[i].endswith("-01") or k == 0 else name)
    ax.set_xticks(idx, labels)
    ax.set_xlim(-0.5, len(months) - 0.5)


def _shade_q3(ax: Axes, months: list[str], label: bool) -> None:
    """Light grey span over 2026-Q3, the quarter of the pre-registered level and difference tests."""
    if Q3[0] not in months:
        return
    lo, hi = months.index(Q3[0]) - 0.5, months.index(min(Q3[1], months[-1])) + 0.5
    ax.axvspan(lo, hi, color="#000000", alpha=0.045, lw=0, zorder=0)
    if label:
        ax.annotate(
            "2026-Q3",
            ((lo + hi) / 2, 1),
            xycoords=("data", "axes fraction"),
            xytext=(0, -2),
            textcoords="offset points",
            ha="center",
            va="top",
            fontsize=7,
            color=MUTED,
        )


def _text_legend(ax: Axes, strata: list[str], note: str | None = None) -> None:
    """Coloured text lines in the empty upper-left corner, in place of a legend box."""
    y = 0.96
    for s in strata:
        ax.annotate(
            STRATUM_NAME[s], (0.02, y), xycoords="axes fraction", color=STRATUM[s], fontsize=8, va="top"
        )
        y -= 0.105
    if note:
        ax.annotate(note, (0.02, y), xycoords="axes fraction", color=MUTED, fontsize=7, va="top")


def _band(ax: Axes, d: pl.DataFrame, x: list[int], colour: str) -> None:
    ax.fill_between(x, d["lo"], d["hi"], color=colour, alpha=BAND_ALPHA, lw=0)
    ax.plot(x, d["share"], color=colour, lw=1.4, solid_capstyle="round")


# --- F1 --------------------------------------------------------------------------------------------------
def f1(series: pl.DataFrame, out: Path, detail: bool = True, name: str = "f1_monthly_share") -> None:
    """``series``: stratum, month, share, lo, hi (pooled, cluster-bootstrap band).

    (a) the three strata over the whole window; (b), when ``detail``, S1 against S3 over 2026 on its own
    scale, where the wide S2 band no longer hides the pre-registered comparison.
    """
    months = _months("2023-01", "2026-09")
    if detail:
        fig = plt.figure(figsize=(WIDTH, 2.7))
        gs = fig.add_gridspec(1, 2, width_ratios=[1.75, 1], wspace=0.3)
        ax = fig.add_subplot(gs[0])
    else:
        fig, ax = plt.subplots(figsize=(WIDTH, 2.6))
    _shade_q3(ax, months, label=True)
    top = 0.0
    for s in ("S2", "S1", "S3"):  # the widest band first, so that it sits behind the other two
        d = series.filter(pl.col("stratum") == s).sort("month")
        if d.is_empty():
            continue
        _band(ax, d, [months.index(m) for m in d["month"]], STRATUM[s])
        top = max(top, float(d["hi"].max()))  # type: ignore[arg-type]
    _text_legend(ax, list(STRATUM), note="shaded: 95% cluster-bootstrap band")
    _pct(ax)
    ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(0.1 if top > 0.2 else 0.05))
    ax.set_ylim(0, max(top, 0.01) * 1.08)
    ax.set_ylabel("AI-attributed share of commits")
    _month_ticks(ax, months)
    if not detail:
        save(fig, out, name)
        return
    panel(ax, "(a)", "All strata, 2023–2026")

    bx = fig.add_subplot(gs[1])
    months_b = _months("2026-01", "2026-09")
    _shade_q3(bx, months_b, label=False)
    top_b = 0.0
    for s in ("S1", "S3"):
        d = series.filter((pl.col("stratum") == s) & pl.col("month").is_in(months_b)).sort("month")
        if d.is_empty():
            continue
        x = [months_b.index(m) for m in d["month"]]
        _band(bx, d, x, STRATUM[s])
        top_b = max(top_b, float(d["hi"].max()))  # type: ignore[arg-type]
        bx.annotate(
            s,
            (x[-1], float(d["share"][-1])),
            xytext=(4, 0),
            textcoords="offset points",
            va="center",
            fontsize=8,
            color=STRATUM[s],
            annotation_clip=False,
        )
    bx.axhline(0.05, color=MUTED, lw=0.7, ls=(0, (1.5, 2)))
    bx.annotate(
        "H1 threshold",
        (0, 0.05),
        xycoords=("axes fraction", "data"),
        xytext=(3, -2),
        textcoords="offset points",
        fontsize=6.5,
        color=MUTED,
        va="top",
    )
    _pct(bx)
    bx.yaxis.set_major_locator(mpl.ticker.MultipleLocator(0.05))
    bx.set_ylim(0, max(top_b, 0.06) * 1.12)
    _month_ticks(bx, months_b, every=("01", "03", "05", "07", "09"))
    panel(bx, "(b)", "2026, S1 against S3")
    save(fig, out, name)


# --- F2 --------------------------------------------------------------------------------------------------
def _quarter_labels(quarters: list[str]) -> list[str]:
    out = []
    for k, q in enumerate(quarters):
        year, qq = q.split("-")
        out.append(f"{qq}\n{year}" if qq == "Q1" or k == 0 else qq)
    return out


def _row_major(handles: list[Any], labels: list[str], ncol: int) -> tuple[list[Any], list[str]]:
    """Reorder legend entries so that they read left to right, row by row (matplotlib fills columns)."""
    rows = -(-len(handles) // ncol)
    idx = [r * ncol + c for c in range(ncol) for r in range(rows) if r * ncol + c < len(handles)]
    return [handles[i] for i in idx], [labels[i] for i in idx]


def f2(tq: pl.DataFrame, nq: pl.DataFrame, out: Path) -> None:
    """``tq``: stratum, q, tool, n_attr; ``nq``: stratum, q, n (all commits) — stacked share by tool."""
    quarters = sorted(nq["q"].unique().to_list())
    quarters = [q for q in quarters if q >= "2025-Q1"]
    fig, axes = plt.subplots(1, 3, figsize=(WIDTH, 2.5), sharey=True)
    peak = 0.0
    for ax, (letter, s) in zip(axes, [("(a)", "S1"), ("(b)", "S2"), ("(c)", "S3")], strict=True):
        n = {r["q"]: r["n"] for r in nq.filter(pl.col("stratum") == s).iter_rows(named=True)}
        bottom = np.zeros(len(quarters))
        d = tq.filter(pl.col("stratum") == s)
        for tool in [*TOOL, "Other"]:
            sel = (
                d.filter(~pl.col("tool").is_in(list(TOOL)))
                if tool == "Other"
                else d.filter(pl.col("tool") == tool)
            )
            v = np.array(
                [float(sel.filter(pl.col("q") == q)["n_attr"].sum()) / n.get(q, 1) for q in quarters]
            )
            ax.bar(
                range(len(quarters)),
                v,
                bottom=bottom,
                color=TOOL.get(tool, OTHER),
                width=0.78,
                lw=0.3,
                edgecolor="white",
                label=tool,
            )
            bottom += v
        for i, total in enumerate(bottom):
            ax.annotate(
                f"{total:.1%}",
                (i, total),
                xytext=(0, 2),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=6,
                color=MUTED,
            )
        peak = max(peak, float(np.max(bottom)) if len(bottom) else 0.0)
        ax.set_xticks(range(len(quarters)), _quarter_labels(quarters), fontsize=7)
        ax.tick_params(axis="x", length=0)
        panel(ax, letter, STRATUM_NAME[s])
    _pct(axes[0])
    axes[0].set_ylim(0, max(peak, 0.01) * 1.16)
    axes[0].set_ylabel("AI-attributed share of commits")
    hs, ls = axes[0].get_legend_handles_labels()
    handles, labels = _row_major(hs, ls, ncol=5)
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=5, fontsize=7.5)
    fig.tight_layout()
    save(fig, out, "f2_tools")


# --- F3 --------------------------------------------------------------------------------------------------
def f3(rm: pl.DataFrame, order: list[tuple[str, str]], out: Path) -> None:
    """Repository × month heatmap of attributed share, 2025-01..2026-09, repositories grouped by stratum."""
    months = _months("2025-01", "2026-09")
    grid = np.full((len(order), len(months)), np.nan)
    look = {(r["repo"], r["month"]): r for r in rm.iter_rows(named=True)}
    for i, (_s, repo) in enumerate(order):
        for j, m in enumerate(months):
            r = look.get((repo, m))
            if r and r["n"] >= 10:
                grid[i, j] = r["n_attr"] / r["n"]
    fig, ax = plt.subplots(figsize=(WIDTH, 0.105 * len(order) + 0.9))
    cmap = plt.get_cmap("Blues").with_extremes(bad="#d9d9d9")
    im = ax.imshow(grid, aspect="auto", cmap=cmap, vmin=0, vmax=0.5, interpolation="nearest")
    ax.set_yticks(range(len(order)), [r for _s, r in order], fontsize=5.2)
    ax.tick_params(axis="y", length=0)
    _month_ticks(ax, months, every=("01", "04", "07", "10"))
    ax.tick_params(axis="x", labelsize=7)
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    edges = [i for i in range(1, len(order)) if order[i][0] != order[i - 1][0]]
    for e in edges:
        ax.axhline(e - 0.5, color=INK, lw=0.8)
    for s in STRATUM:
        rows = [i for i, (t, _r) in enumerate(order) if t == s]
        if rows:
            ax.annotate(
                STRATUM_NAME[s],
                (len(months) - 0.5, (rows[0] + rows[-1]) / 2),
                xytext=(5, 0),
                textcoords="offset points",
                rotation=270,
                va="center",
                ha="left",
                fontsize=7.5,
                weight="bold",
                color=STRATUM[s],
                annotation_clip=False,
            )
    cb = fig.colorbar(im, ax=ax, orientation="horizontal", location="top", fraction=0.02, pad=0.01, aspect=50)
    cb.set_ticks([0, 0.1, 0.2, 0.3, 0.4, 0.5], labels=["0%", "10%", "20%", "30%", "40%", "≥ 50%"])
    cb.ax.tick_params(labelsize=7, length=2)
    cb.outline.set_linewidth(0.4)
    cb.set_label(
        "AI-attributed share of commits (repository-months with ≥ 10 commits; grey: fewer)", fontsize=7.5
    )
    save(fig, out, "f3_heatmap")


# --- F4 --------------------------------------------------------------------------------------------------
def f4(per_repo: pl.DataFrame, out: Path, pooled: dict[str, float] | None = None) -> None:
    """``per_repo``: stratum, repo, n, n_attr for 2026-Q3 — sorted dots with Wilson 95% intervals.

    S1 fills the left column; S2 sits above S3 on the right, rows equally spaced, one shared x scale.
    ``pooled``: the stratum's pooled share, drawn as a dashed reference line.
    """
    count = {s: per_repo.filter(pl.col("stratum") == s).height for s in STRATUM}
    fig = plt.figure(figsize=(WIDTH, 0.105 * (count["S2"] + count["S3"]) + 1.0))
    gs = fig.add_gridspec(2, 2, height_ratios=[count["S2"] + 1, count["S3"] + 1])
    axes = {"S1": fig.add_subplot(gs[:, 0])}
    axes["S3"] = fig.add_subplot(gs[1, 1], sharex=axes["S1"])
    axes["S2"] = fig.add_subplot(gs[0, 1], sharex=axes["S1"])
    for letter, s in [("(a)", "S1"), ("(b)", "S2"), ("(c)", "S3")]:
        ax = axes[s]
        d = per_repo.filter(pl.col("stratum") == s).with_columns((pl.col("n_attr") / pl.col("n")).alias("p"))
        d = d.sort("p")
        y = np.arange(d.height)
        if pooled and s in pooled:
            ax.axvline(pooled[s], color=STRATUM[s], lw=0.8, ls=DASH, alpha=0.9, zorder=1)
            ax.annotate(
                f"pooled {pooled[s]:.1%}",
                (pooled[s], 1),
                xycoords=("data", "axes fraction"),
                xytext=(3, -1),
                textcoords="offset points",
                ha="left",
                va="top",
                fontsize=6.5,
                color=STRATUM[s],
            )
        for i, r in enumerate(d.iter_rows(named=True)):
            lo, hi = wilson(int(r["n_attr"]), int(r["n"]))
            ax.plot([lo, hi], [i, i], color=STRATUM[s], lw=0.9, alpha=0.6)
        ax.plot(d["p"], y, color=STRATUM[s], **DOT)
        ax.set_yticks(y, d["repo"].to_list(), fontsize=5.6)
        ax.set_ylim(-0.8, d.height - 0.2)
        ax.tick_params(axis="y", length=0)
        ax.grid(axis="x", color=GRID, lw=0.6)
        ax.grid(axis="y", visible=False)
        panel(ax, letter, STRATUM_NAME[s])
    _pct(axes["S1"], "x")
    axes["S1"].set_xlim(0, 1)
    axes["S1"].set_xticks([0, 0.25, 0.5, 0.75, 1])
    fig.supxlabel(
        "AI-attributed share of commits, 2026-Q3 (Wilson 95% CI; dashed: pooled share of the stratum)",
        fontsize=8,
    )
    fig.tight_layout(w_pad=0.8, h_pad=0.6)
    save(fig, out, "f4_per_repo")


# --- F5 --------------------------------------------------------------------------------------------------
def f5(
    by_method: dict[str, tuple[int, int, tuple[float, float]]], overall: tuple[int, int], out: Path
) -> None:
    order = [m for m in ("squash", "merge", "rebase", "single-commit-ambiguous") if m in by_method]
    labels = {
        "squash": "Squash",
        "merge": "Merge commit",
        "rebase": "Rebase",
        "single-commit-ambiguous": "Single commit",
    }
    fig, ax = plt.subplots(figsize=(WIDTH * 0.62, 1.9))
    rows = [("All", *overall, wilson(*overall))] + [(labels[m], *by_method[m]) for m in order]
    for i, (_name, k, n, (lo, hi)) in enumerate(rows):
        p = k / n if n else float("nan")
        ax.plot([lo, hi], [i, i], color=STRATUM["S1"], lw=1.2, solid_capstyle="butt")
        ax.plot([p], [i], color=STRATUM["S1"], **DOT)
        ax.annotate(
            f"{p:.0%}  ({k}/{n})",
            (1.0, i),
            xytext=(5, 0),
            textcoords="offset points",
            va="center",
            fontsize=7.5,
            color=MUTED,
            annotation_clip=False,
        )
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
    ax.tick_params(axis="y", length=0)
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    _pct(ax, "x")
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Attribution kept on the default branch (Wilson 95% CI)")
    save(fig, out, "f5_survival")


# --- F6 --------------------------------------------------------------------------------------------------
def f6(per_repo: pl.DataFrame, out: Path) -> None:
    """``per_repo``: stratum, repo, n, n_attr, policy (2026-Q3)."""
    classes = ["bans", "requires_disclosure", "mentions", "silent"]
    names = {
        "bans": "Bans",
        "requires_disclosure": "Requires\ndisclosure",
        "mentions": "Mentions,\nno rule",
        "silent": "Silent",
    }
    rng = np.random.default_rng(20261028)
    fig, ax = plt.subplots(figsize=(WIDTH * 0.72, 2.5))
    for j, c in enumerate(classes):
        d = per_repo.filter(pl.col("policy") == c)
        for s in STRATUM:
            e = d.filter(pl.col("stratum") == s)
            if e.height:
                x = j + rng.uniform(-0.18, 0.18, e.height) + {"S1": -0.08, "S2": 0.0, "S3": 0.08}[s]
                ax.plot(x, e["n_attr"] / e["n"], color=STRATUM[s], **DOT)
        if d.height:
            pooled = float(d["n_attr"].sum()) / float(d["n"].sum())
            ax.plot(
                [j - 0.32, j + 0.32], [pooled, pooled], color=INK, lw=1.3, solid_capstyle="butt", zorder=3
            )
            ax.annotate(
                f"{pooled:.1%}",
                (j + 0.32, pooled),
                xytext=(2, 0),
                textcoords="offset points",
                va="center",
                fontsize=7,
                color=INK,
            )
    ax.set_xticks(range(len(classes)), [names[c] for c in classes])
    ax.tick_params(axis="x", length=0)
    ax.set_xlim(-0.6, len(classes) - 0.4)
    _pct(ax)
    ax.set_ylabel("AI-attributed share of commits, 2026-Q3")
    handles = [mpl.lines.Line2D([], [], color=STRATUM[s], **DOT) for s in STRATUM]
    strata = [STRATUM_NAME[s] for s in STRATUM]
    ax.legend(handles, strata, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, fontsize=7.5)
    save(fig, out, "f6_policy")


# --- F8 --------------------------------------------------------------------------------------------------
def f8(per_repo: pl.DataFrame, out: Path, label_above: float = 0.4) -> None:
    """``per_repo``: stratum, repo, share, breadth (2026-Q3) — breadth vs intensity.

    Repositories with either share above ``label_above`` are named.
    """
    fig, ax = plt.subplots(figsize=(WIDTH * 0.62, 2.9))
    for s in STRATUM:
        d = per_repo.filter(pl.col("stratum") == s)
        ax.plot(d["breadth"], d["share"], color=STRATUM[s], label=STRATUM_NAME[s], **DOT)
    lim = max(float(per_repo["breadth"].max()), float(per_repo["share"].max())) * 1.05  # type: ignore[arg-type]
    ax.plot([0, lim], [0, lim], color=MUTED, lw=0.6, ls=(0, (3, 3)), zorder=1)
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    (x0, y0), (x1, y1) = ax.transData.transform([(0, 0), (lim, lim)])
    ax.annotate(
        "equal shares",
        (lim * 0.8, lim * 0.8),
        xytext=(0, 3),
        textcoords="offset points",
        rotation=float(np.degrees(np.arctan2(y1 - y0, x1 - x0))),
        rotation_mode="anchor",
        ha="center",
        va="bottom",
        fontsize=6.5,
        color=MUTED,
    )
    named = per_repo.filter((pl.col("breadth") >= label_above) | (pl.col("share") >= label_above))
    for r in named.iter_rows(named=True):
        left, above = r["breadth"] > 0.55, r["share"] >= r["breadth"]
        ax.annotate(
            r["repo"],
            (r["breadth"], r["share"]),
            xytext=(-4 if left else 4, 3 if above else -3),
            textcoords="offset points",
            ha="right" if left else "left",
            va="bottom" if above else "top",
            fontsize=5.8,
            color=MUTED,
        )
    _pct(ax)
    _pct(ax, "x")
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_xlabel("Breadth: active authors with ≥ 1 attributed commit")
    ax.set_ylabel("Intensity: attributed share of commits")
    ax.legend(loc="upper left", fontsize=7.5, handletextpad=0.5, borderaxespad=0.4)
    save(fig, out, "f8_breadth")
