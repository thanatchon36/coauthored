"""Paper figures F1–F6 and F8 (MISSION §7.4), house style shared with the author's other papers.

Libertinus Serif (vendored in ``figures/fonts``), sized so 8 pt prints at 8 pt at a 16 cm text width; no
in-figure titles (panel labels only); legends above the axes or direct labels; one fixed colour per stratum
and per tool (Okabe–Ito). Every figure is written as SVG with text as outlines (PDF build) and 300-dpi PNG.
Every share is a share of *AI-attributed* commits, a lower bound; captions say so.
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


def _month_ticks(ax: Axes, months: list[str]) -> None:
    idx = [i for i, m in enumerate(months) if m[5:] in ("01", "07")]
    ax.set_xticks(idx, [("Jan\n" + months[i][:4]) if months[i].endswith("-01") else "Jul" for i in idx])
    ax.set_xlim(-0.5, len(months) - 0.5)


# --- F1 --------------------------------------------------------------------------------------------------
def _spread(ys: dict[str, float], gap: float) -> dict[str, float]:
    """Push end-of-line labels apart vertically so that none are closer than ``gap`` (data units)."""
    order = sorted(ys, key=lambda k: ys[k])
    out = {k: ys[k] for k in order}
    for a, b in zip(order, order[1:], strict=False):
        if out[b] - out[a] < gap:
            out[b] = out[a] + gap
    return out


def f1(series: pl.DataFrame, out: Path) -> None:
    """``series``: stratum, month, share, lo, hi (pooled, cluster-bootstrap band)."""
    months = _months("2023-01", "2026-09")
    fig, ax = plt.subplots(figsize=(WIDTH, 2.6))
    ends: dict[str, float] = {}
    for s, colour in STRATUM.items():
        d = series.filter(pl.col("stratum") == s).sort("month")
        x = [months.index(m) for m in d["month"]]
        ax.fill_between(x, d["lo"], d["hi"], color=colour, alpha=0.15, lw=0)
        ax.plot(x, d["share"], color=colour, lw=1.4)
        ends[s] = float(d["share"][-1])
    top = float(series["hi"].max())  # type: ignore[arg-type]
    for s, y in _spread(ends, gap=0.075 * top).items():
        ax.annotate(
            STRATUM_NAME[s],
            (len(months) - 1, y),
            xytext=(5, 0),
            textcoords="offset points",
            va="center",
            fontsize=8,
            color=STRATUM[s],
            annotation_clip=False,
        )
    _pct(ax)
    ax.set_ylim(0, None)
    ax.set_ylabel("AI-attributed share of commits")
    _month_ticks(ax, months)
    save(fig, out, "f1_monthly_share")


# --- F2 --------------------------------------------------------------------------------------------------
def f2(tq: pl.DataFrame, nq: pl.DataFrame, out: Path) -> None:
    """``tq``: stratum, q, tool, n_attr; ``nq``: stratum, q, n (all commits) — stacked share by tool."""
    quarters = sorted(nq["q"].unique().to_list())
    quarters = [q for q in quarters if q >= "2025-Q1"]
    fig, axes = plt.subplots(1, 3, figsize=(WIDTH, 2.4), sharey=True)
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
                width=0.8,
                lw=0,
                label=tool,
            )
            bottom += v
        ax.set_xticks(range(len(quarters)), [q.replace("-", "\n") for q in quarters], fontsize=7)
        panel(ax, letter, STRATUM_NAME[s])
    _pct(axes[0])
    axes[0].set_ylabel("AI-attributed share of commits")
    handles, labels = axes[0].get_legend_handles_labels()
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
    fig, ax = plt.subplots(figsize=(WIDTH, 0.105 * len(order) + 0.8))
    cmap = plt.get_cmap("Blues").with_extremes(bad="#d9d9d9")
    im = ax.imshow(grid, aspect="auto", cmap=cmap, vmin=0, vmax=0.5, interpolation="nearest")
    ax.set_yticks(range(len(order)), [r for _s, r in order], fontsize=5.2)
    ax.set_xticks(range(0, len(months), 3), [months[i] for i in range(0, len(months), 3)], fontsize=7)
    ax.grid(False)
    edges = [i for i in range(1, len(order)) if order[i][0] != order[i - 1][0]]
    for e in edges:
        ax.axhline(e - 0.5, color=INK, lw=0.8)
    for s in STRATUM:
        rows = [i for i, (t, _r) in enumerate(order) if t == s]
        if rows:
            ax.annotate(
                s,
                (len(months) - 0.5, (rows[0] + rows[-1]) / 2),
                xytext=(6, 0),
                textcoords="offset points",
                va="center",
                fontsize=8,
                weight="bold",
                color=STRATUM[s],
                annotation_clip=False,
            )
    cb = fig.colorbar(im, ax=ax, orientation="horizontal", location="top", fraction=0.02, pad=0.01, aspect=50)
    cb.ax.xaxis.set_major_formatter(mpl.ticker.PercentFormatter(1.0, decimals=0))
    cb.ax.tick_params(labelsize=7)
    cb.set_label("AI-attributed share (repository-months with ≥ 10 commits; grey = fewer)", fontsize=7.5)
    save(fig, out, "f3_heatmap")


# --- F4 --------------------------------------------------------------------------------------------------
def f4(per_repo: pl.DataFrame, out: Path) -> None:
    """``per_repo``: stratum, repo, n, n_attr for 2026-Q3 — sorted dots with Wilson 95% intervals.

    S1 fills the left column; S2 sits above S3 on the right, rows equally spaced, one shared x scale.
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
        for i, r in enumerate(d.iter_rows(named=True)):
            lo, hi = wilson(int(r["n_attr"]), int(r["n"]))
            ax.plot([lo, hi], [i, i], color=STRATUM[s], lw=0.9, alpha=0.6)
        ax.plot(d["p"], y, color=STRATUM[s], **DOT)
        ax.set_yticks(y, d["repo"].to_list(), fontsize=5.6)
        ax.set_ylim(-0.8, d.height - 0.2)
        ax.grid(axis="x", color=GRID, lw=0.6)
        ax.grid(axis="y", visible=False)
        panel(ax, letter, STRATUM_NAME[s])
    _pct(axes["S1"], "x")
    axes["S1"].set_xlim(0, 1)
    axes["S1"].set_xticks([0, 0.25, 0.5, 0.75, 1])
    fig.supxlabel("AI-attributed share of commits, 2026-07..09 (Wilson 95% CI)", fontsize=8)
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
    fig, ax = plt.subplots(figsize=(WIDTH * 0.6, 1.9))
    rows = [("All", *overall, wilson(*overall))] + [(labels[m], *by_method[m]) for m in order]
    for i, (_name, k, n, (lo, hi)) in enumerate(rows):
        p = k / n if n else float("nan")
        ax.plot([lo, hi], [i, i], color=STRATUM["S1"], lw=1.2)
        ax.plot([p], [i], color=STRATUM["S1"], **DOT)
        ax.annotate(
            f"{k}/{n}",
            (1.0, i),
            xytext=(4, 0),
            textcoords="offset points",
            va="center",
            fontsize=7.5,
            color=MUTED,
            annotation_clip=False,
        )
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
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
    fig, ax = plt.subplots(figsize=(WIDTH * 0.7, 2.3))
    for j, c in enumerate(classes):
        d = per_repo.filter(pl.col("policy") == c)
        for s in STRATUM:
            e = d.filter(pl.col("stratum") == s)
            if e.height:
                x = j + rng.uniform(-0.18, 0.18, e.height) + {"S1": -0.08, "S2": 0.0, "S3": 0.08}[s]
                ax.plot(x, e["n_attr"] / e["n"], color=STRATUM[s], **DOT)
        if d.height:
            pooled = float(d["n_attr"].sum()) / float(d["n"].sum())
            ax.plot([j - 0.3, j + 0.3], [pooled, pooled], color=INK, lw=1.2)
    ax.set_xticks(range(len(classes)), [names[c] for c in classes])
    _pct(ax)
    ax.set_ylabel("AI-attributed share, 2026-07..09")
    handles = [mpl.lines.Line2D([], [], color=STRATUM[s], **DOT) for s in STRATUM]
    ax.legend(handles, list(STRATUM), loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3)
    save(fig, out, "f6_policy")


# --- F8 --------------------------------------------------------------------------------------------------
def f8(per_repo: pl.DataFrame, out: Path) -> None:
    """``per_repo``: stratum, repo, share, breadth (2026-Q3) — breadth vs intensity."""
    fig, ax = plt.subplots(figsize=(WIDTH * 0.6, 2.6))
    for s in STRATUM:
        d = per_repo.filter(pl.col("stratum") == s)
        ax.plot(d["breadth"], d["share"], color=STRATUM[s], label=STRATUM_NAME[s], **DOT)
    lim = max(float(per_repo["breadth"].max()), float(per_repo["share"].max())) * 1.05  # type: ignore[arg-type]
    ax.plot([0, lim], [0, lim], color=MUTED, lw=0.6, ls=(0, (3, 3)))
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    _pct(ax)
    _pct(ax, "x")
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_xlabel("Breadth: active authors with ≥ 1 attributed commit")
    ax.set_ylabel("Intensity: attributed share of commits")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=1, fontsize=7.5)
    save(fig, out, "f8_breadth")
