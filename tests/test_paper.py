import pytest

from coauthored.paper import check, fill, fmt, lookup

DATA = {
    "summary": {
        "quarterly": [
            {"stratum": "S1", "q": "2026-Q3", "share": 0.08704},
            {"stratum": "S2", "q": "2026-Q3", "share": 0.1},
        ]
    },
    "n": 1234567,
    "ci": [0.04, 0.15],
    "missing": None,
}


def test_lookup_with_selectors() -> None:
    assert lookup(DATA, "summary.quarterly[stratum=S1,q=2026-Q3].share") == 0.08704
    assert lookup(DATA, "ci[1]") == 0.15
    with pytest.raises(KeyError):
        lookup(DATA, "summary.quarterly[q=2026-Q3].share")  # two rows match


def test_fmt() -> None:
    assert fmt(0.08704, "pct1") == "8.7%"
    assert fmt(0.08704, "pct2") == "8.70%"
    assert fmt(1234567, ",") == "1,234,567"
    assert fmt(1.234, "x2") == "1.23×"
    assert fmt(None, ".2f") == "n/a"
    assert fmt(0.087, "inv") == "11"
    assert fmt(False, "verdict") == "not supported"


def test_fill_and_missing_key() -> None:
    assert (
        fill("S1 reached {{summary.quarterly[stratum=S1,q=2026-Q3].share|pct1}}.", DATA) == "S1 reached 8.7%."
    )
    with pytest.raises(SystemExit, match="nope"):
        fill("{{nope}}", DATA)


def test_check_flags_hand_typed_numbers_only() -> None:
    text = """---
title: x
fontsize: 10pt
---
In 2026-Q3 S1 reached {{n|,}} commits across H1–H4 (§4.2) [@robbes2026], see `--draws 2000`.
The share was 8.7% in 2026.
Threshold of 5% <!-- numbers-ok: pre-registered -->
![Caption with 12 repos](results/figures/f1.svg){#fig:f1 width=100%}
1. A list item with a 95% CI, under Apache-2.0, and 95% of something else.
"""
    assert check(text) == [(6, "8.7"), (8, "12"), (9, "95")]
