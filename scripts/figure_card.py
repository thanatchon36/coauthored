"""Write announce/figure_card.png: F1 on a 1200×627 social card with a title and the lower-bound note."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

from coauthored.analysis import figures as fig


def main() -> None:
    fig.setup()
    n = json.loads(Path("results/numbers.json").read_text())
    q = {(r["stratum"], r["q"]): r["share"] for r in n["summary"]["quarterly"]}
    s1, s3 = q[("S1", "2026-Q3")], q[("S3", "2026-Q3")]
    img = mpimg.imread("results/figures/f1_monthly_share.png")
    card = plt.figure(figsize=(12, 6.27), dpi=100, facecolor="white")
    title = "How much of the code that trains the models declares AI help?"
    card.text(0.04, 0.93, title, fontsize=26, color=fig.INK, va="top")
    card.text(
        0.04,
        0.84,
        f"AI-attributed share of commits, 2026-Q3: {100 * s1:.1f}% in AI-infrastructure repositories, "
        f"{100 * s3:.1f}% in matched non-AI repositories",
        fontsize=15,
        color=fig.MUTED,
        va="top",
    )
    ax = card.add_axes((0.04, 0.09, 0.92, 0.70))
    ax.imshow(img, interpolation="lanczos")
    ax.set_axis_off()
    card.text(
        0.04,
        0.035,
        "A lower bound on AI involvement, not a share of code written by AI. "
        "Pre-registered; 96 repositories.",
        fontsize=12,
        color=fig.MUTED,
    )
    card.text(0.96, 0.035, "coauthored", fontsize=12, color=fig.INK, ha="right")
    out = Path("announce/figure_card.png")
    card.savefig(out, dpi=100, facecolor="white", metadata={"Software": None})
    print(out)


if __name__ == "__main__":
    main()
