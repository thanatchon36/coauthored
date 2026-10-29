import pytest

from coauthored.paper import check, crossref, fill, fmt, lookup, number_captions, results

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


def test_fill_accepts_escaped_pipe_in_tables() -> None:
    assert fill("| {{a.b\\|pct1}} |", {"a": {"b": 0.087}}) == "| 8.7% |"


def test_crossref_numbers_in_order_of_appearance() -> None:
    text = """# Intro
See Figure @fig:b, Table @tbl:t and Section @sec:m.
# Method {#sec:m}
## Detail {#sec:d}
![x](a.svg){#fig:a width=50%}
![y](b.svg){#fig:b}
: cap {#tbl:t}
# References {-}
"""
    out = crossref(text)
    assert "See Figure 2, Table 1 and Section 2." in out
    assert crossref("@sec:d\n" + text).startswith("2.1\n")
    with pytest.raises(SystemExit):
        crossref("@fig:missing")


def test_number_captions_matches_typst_order() -> None:
    body = "![A](a.svg){#fig:a}\n\n: Hyp {#tbl:h}\n\n![B\nwrapped](b.svg){#fig:b width=50%}\n"
    out = number_captions(body)
    assert "![Figure 1. A](a.svg)" in out and "![Figure 2. B\nwrapped]" in out
    assert "**Table 1.** Hyp" in out


def test_results_strip_kinds() -> None:
    data = {
        "hypotheses": [
            {
                "hypothesis": "H1",
                "statement": "s",
                "estimate": 0.087,
                "ci": [0.05, 0.15],
                "supported": True,
                "p_holm": 0.4,
            },
            {
                "hypothesis": "H3",
                "statement": "s",
                "estimate": 0.025,
                "ci": [-0.08, 0.07],
                "supported": False,
                "p_holm": 1.0,
            },
            {"hypothesis": "H7", "statement": "s", "estimate": 0.03, "ci": [None, None], "supported": True},
        ]
    }
    rows = results(data)
    assert [r[1] for r in rows] == ["pos", "ref", "nf"]
    assert rows[0][3] == "estimate 8.7%, 95% CI 5.0% to 15.0%, Holm p 0.400"
    assert rows[1][3].startswith("estimate 0.025, 95% CI −0.080")


def test_fmt_percentage_points() -> None:
    assert fmt(0.01614, "pp1") == "1.6" and fmt(-0.758, "pp1") == "−75.8"
    assert fmt(2e-6, "p") == "<0.001" and fmt(0.0812, "p") == "0.081"
