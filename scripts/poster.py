"""Write announce/poster.png: a 1200×1500 (4:5) LinkedIn poster of the headline result.

Every number is read from results/numbers.json; the chart is the paper's F1 series in the figure house style
(Libertinus Serif, Okabe–Ito stratum colours). Nothing here is typed by hand.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch

from coauthored.analysis import figures as fig

W, H, DPI = 1200, 1500, 150  # pixels; LinkedIn shows 4:5 at full height in the feed
M = 72  # margin, px
R = W - M  # right edge of the text column
TILE = "#f1f2f4"
FROM = "2024-01"  # the chart starts where the curve is still flat: the take-off is the point
NAME = {
    "S1": "AI model infrastructure",
    "S2": "Coding-agent harnesses",
    "S3": "Matched non-AI projects",
}


def _canvas() -> tuple[Figure, Axes]:
    """A figure with one pixel-addressed overlay axes: x right, y down, 1 unit = 1 px."""
    f = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI, facecolor="white")
    ax = f.add_axes((0, 0, 1, 1), facecolor="none")
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_axis_off()
    return f, ax


def _t(ax: Axes, x: float, y: float, s: str, size: float, **kw: Any) -> Any:
    kw = {"color": fig.INK, "ha": "left", "va": "top", **kw}
    return ax.text(x, y, s, fontsize=size, **kw)


def _chain(
    f: Figure, ax: Axes, x: float, y: float, parts: list[tuple[str, float, str]], gap: float = 7
) -> None:
    """Pieces of one line in different sizes and weights, laid left to right on a shared baseline."""
    r = f.canvas.get_renderer()  # type: ignore[attr-defined]
    for s, size, weight in parts:
        t = _t(ax, x, y, s, size, weight=weight, va="baseline")
        x = t.get_window_extent(r).x1 + gap


def _tile(ax: Axes, x: float, y: float, w: float, h: float, accent: str | None = None) -> None:
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=14", fc=TILE, ec="none"))
    if accent:
        ax.add_patch(
            FancyBboxPatch(
                (x + 28, y + 26), 44, 6, boxstyle="round,pad=0,rounding_size=3", fc=accent, ec="none"
            )
        )


def _chart(f: Figure, monthly: list[dict[str, Any]], box: tuple[float, float, float, float]) -> None:
    x0, y0, x1, y1 = box
    ax = f.add_axes((x0 / W, 1 - y1 / H, (x1 - x0) / W, (y1 - y0) / H))
    months = sorted({r["month"] for r in monthly if r["month"] >= FROM})
    by = {s: {r["month"]: r for r in monthly if r["stratum"] == s} for s in fig.STRATUM}
    xs = list(range(len(months)))
    top = 0.0
    for s in (
        "S3",
        "S1",
    ):  # bands for the pair the headline compares; the S2 band is far wider (see the paper)
        lo = [by[s][m]["lo"] for m in months]
        hi = [by[s][m]["hi"] for m in months]
        ax.fill_between(xs, lo, hi, color=fig.STRATUM[s], alpha=0.12, lw=0)
        top = max(top, max(hi))
    for s in ("S2", "S3", "S1"):
        ys = [by[s][m]["share"] for m in months]
        ax.plot(xs, ys, color=fig.STRATUM[s], lw=2.6, solid_capstyle="round", zorder=3)
        top = max(top, max(ys))
    fig._shade_q3(ax, months, label=False)
    lo_q3 = months.index(fig.Q3[0]) - 0.5
    ax.annotate(
        "Jul–Sep 2026",
        ((lo_q3 + len(months) - 0.5) / 2, 1),
        xycoords=("data", "axes fraction"),
        xytext=(0, -4),
        textcoords="offset points",
        ha="center",
        va="top",
        fontsize=10,
        color=fig.MUTED,
    )
    for i, s in enumerate(("S1", "S2", "S3")):
        ax.annotate(
            NAME[s],
            (0.02, 0.97),
            xycoords="axes fraction",
            xytext=(0, -21 * i),
            textcoords="offset points",
            ha="left",
            va="top",
            fontsize=12.5,
            color=fig.STRATUM[s],
            weight="semibold",
        )
    fig._month_ticks(ax, months)
    fig._pct(ax)
    ax.set_ylim(0, 0.05 * (int(top / 0.05) + 1))
    ax.tick_params(labelsize=10.5, length=0)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_visible(False)
    ax.grid(True, axis="y", color=fig.GRID, lw=0.8)


def main() -> None:
    fig.setup()
    n = json.loads(Path("results/numbers.json").read_text())
    q = {(r["stratum"], r["q"]): r for r in n["summary"]["quarterly"]}
    year = {(r["stratum"], r["year"]): r for r in n["summary"]["year"]}
    h6 = next(h for h in n["hypotheses"] if h["hypothesis"] == "H6")
    size = next(r for r in n["size"] if r["stratum"] == "S1" and r["period"] == "all")
    within = next(r for r in n["size_within_repo"] if r["stratum"] == "S1")
    pol = n["summary"]["policy"]
    repos = {r["stratum"]: r for r in n["summary"]["repos"]}
    strata = n["summary"]["strata"]
    snap = n["summary"]["snapshot"]
    s1, s2, s3 = (q[(s, "2026-Q3")] for s in ("S1", "S2", "S3"))
    zero = year[("S1", "2024")]
    assert zero["n_attr"] == 0, "the 2024 line of the poster assumes no attributed S1 commit that year"
    one_in = round(1 / s1["share"])

    f, ax = _canvas()
    # header
    _t(
        ax,
        M,
        60,
        f"PRE-REGISTERED · {snap['repositories']} OPEN-SOURCE REPOSITORIES · {snap['commits_all']:,} COMMITS"
        f" · ONE-DAY SNAPSHOT {n['snapshot'][:10]}",
        10,
        color=fig.MUTED,
    )
    _t(ax, M, 90, "How much of the code that trains the models declares AI help?", 20, weight="semibold")
    # hero
    _t(ax, M - 4, 142, f"1 in {one_in}", 76, color=fig.STRATUM["S1"], weight="bold")
    _t(
        ax,
        590,
        168,
        "commits to the open-source code that\ntrains and serves AI models declared\n"
        "AI help in July–September 2026.",
        15.5,
        linespacing=1.3,
    )
    _t(
        ax,
        590,
        308,
        f"{100 * s1['share']:.1f}% of {s1['n']:,} commits in {strata['S1']} repositories · "
        f"95% CI {100 * s1['lo']:.1f}–{100 * s1['hi']:.1f}%",
        10,
        color=fig.MUTED,
    )
    _chain(
        f,
        ax,
        M,
        378,
        [
            ("In 2024,", 15, "normal"),
            (f"0 of {zero['n']:,}", 22, "bold"),
            ("commits to the same repositories declared AI help.", 15, "normal"),
        ],
    )
    # chart
    _t(
        ax,
        M,
        418,
        "AI-attributed share of commits by month, pooled over repositories",
        12.5,
        weight="semibold",
    )
    _chart(f, n["monthly"], (M + 16, 452, R, 704))
    _t(
        ax,
        M,
        772,
        "Shaded: 95% cluster-bootstrap bands for the two groups the headline compares "
        "(the harnesses' band is wider and omitted).\n"
        "Grey column: July–September 2026, the pre-registered test window.",
        9.5,
        color=fig.MUTED,
        linespacing=1.35,
    )
    # the three shares
    tw, th, gap = (R - M - 2 * 20) / 3, 150, 20
    for i, (s, r) in enumerate((("S1", s1), ("S3", s3), ("S2", s2))):
        x, y = M + i * (tw + gap), 836
        _tile(ax, x, y, tw, th, accent=fig.STRATUM[s])
        _t(ax, x + 28, y + 36, f"{100 * r['share']:.1f}%", 32, weight="bold")
        _t(ax, x + 28, y + 102, NAME[s], 11)
        ci = f"{strata[s]} repos · 95% CI {100 * r['lo']:.1f}–{100 * r['hi']:.1f}%"
        _t(ax, x + 28, y + 126, ci, 9.5, color=fig.MUTED)
    _t(
        ax,
        M,
        996,
        "The intervals overlap: no evidence that the people building AI declare more AI help\n"
        "than everyone else, and no proof that they don't.",
        13,
        style="italic",
        linespacing=1.3,
    )
    # four more facts, one row each
    facts = [
        (
            f"{100 * h6['estimate']:.0f}%",
            "of sampled pull requests with an attributed commit still carried the attribution\n"
            f"on the main branch after the merge ({h6['detail']['k']} of {h6['detail']['n']})",
        ),
        (
            f"{size['ratio']:.1f}×",
            f"lines changed per attributed commit (median {size['median_attr']:.0f} vs "
            f"{size['median_unattr']:.0f}); mostly which repositories\n"
            f"and when: {within['ratio']:.1f}× within a repository and year",
        ),
        (
            f"{pol['bans']} of {snap['repositories']}",
            f"repositories bans AI contributions; {pol['requires_disclosure']} require disclosure, "
            f"{pol['agent_config']} ship instructions\nfor coding agents (AGENTS.md, CLAUDE.md)",
        ),
        (
            f"{round(10 * repos['S1']['max_share_q3'])} in 10",
            "commits attributed in the most AI-attributed repository in July–September 2026;\n"
            f"{repos['S1']['share_ge_10pct_q3']} of the {strata['S1']} AI-infrastructure repositories "
            "were at 1 in 10 or more",
        ),
    ]
    fh = 62
    for i, (num, text) in enumerate(facts):
        y = 1076 + i * (fh + 8)
        _tile(ax, M, y, R - M, fh)
        _t(ax, M + 24, y + 13, num, 21, weight="bold")
        _t(ax, M + 210, y + 10, text, 10, linespacing=1.35)
    # footer
    _t(
        ax,
        M,
        1370,
        "Every number is a lower bound. "
        "An attributed commit says a tool took part, not that AI wrote the code.",
        11.5,
        weight="semibold",
    )
    _t(
        ax,
        M,
        1400,
        "github.com/thanatchon36/coauthored   ·   pip install coauthored   ·   "
        "doi.org/10.5281/zenodo.23752989",
        10.5,
    )
    _t(
        ax,
        M,
        1428,
        "Independent personal research. Public data only. "
        "Does not represent the views of any employer or institution.",
        9.5,
        color=fig.MUTED,
    )
    out = Path("announce/poster.png")
    f.savefig(out, dpi=DPI, facecolor="white", metadata={"Software": None})
    print(out)


if __name__ == "__main__":
    main()
