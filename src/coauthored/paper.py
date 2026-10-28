"""`coauthored paper`: fill paper/paper.md from results/numbers.json and build the PDF (pandoc → Typst).

Placeholders: ``{{dotted.path}}`` or ``{{dotted.path|fmt}}``. List elements are addressed by ``key=value``
selectors, e.g. ``{{summary.quarterly[stratum=S1,q=2026-Q3].share|pct1}}``, or by index (``ci[0]``).
``fmt`` is a Python format spec (``.2f``, ``,``, ``d``) or one of ``pct`` / ``pct1`` / ``pct2``
(percentages), ``x2`` (ratio as ``1.23×``), ``inv`` (``N`` in "one in N") and ``verdict``. A missing key
fails the build, and so does a number typed by hand in the prose (``check``): every result in the paper comes
from numbers.json (MISSION §7.3). A line may opt out with ``<!-- numbers-ok: reason -->``, for pre-registered
thresholds and design constants. ``<!-- include: path -->`` on its own line inserts a generated table.
``@fig:x``, ``@tbl:x`` and ``@sec:x`` become the number of the figure, table or numbered section labelled
``{#fig:x}`` etc., counted in order of appearance as Typst numbers them (``crossref``); citeproc would
otherwise read them as citations.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

TOKEN = re.compile(r"\{\{\s*([^}|\\]+?)\s*(?:\\?\|\s*([^}]+?)\s*)?\}\}")  # `\|` inside tables
STEP = re.compile(r"([^.\[]+)(?:\[([^\]]+)\])?")
PRAGMA = "<!-- numbers-ok:"
INCLUDE = re.compile(r"^<!-- include: (\S+) -->$", re.M)  # generated tables, inserted verbatim

# Stripped before looking for hand-typed numbers: things that contain digits but are not results.
NOT_PROSE = [
    re.compile(r"\A---\n.*?\n---\n", re.S),  # YAML front matter
    re.compile(r"```.*?```", re.S),  # code blocks
    re.compile(r"`[^`]*`"),  # code spans
    re.compile(r"<!--.*?-->", re.S),  # comments
    TOKEN,  # placeholders
    re.compile(r"\[@[^\]]*\]|@[\w:-]+"),  # citations
    re.compile(r"\]\([^)]*\)(\{[^}]*\})?"),  # link and image targets (captions stay and are checked)
    re.compile(r"https?://\S+"),
    re.compile(r"\{#[^}]*\}"),  # anchors
    re.compile(r"\b(?:19|20)\d\d-(?:Q[1-4]|\d\d)(?:-\d\d)?\b"),  # dates and quarters
    re.compile(r"\b(?:19|20)\d\d\b"),  # years
    re.compile(r"(?<![\w.])[A-Z][A-Za-z]*\d+[a-z]?\b"),  # labels: H1, S2, RQ6, F4, D16, Q3, SHA256
    re.compile(r"§\s*\d+(?:\.\d+)*"),  # section references
    re.compile(r"^\d+\. ", re.M),  # numbered-list markers
    re.compile(r"\b95% (?=CI|confidence|cluster|interval|Wilson|band)"),  # the confidence level
    re.compile(r"\b(?:Apache|CC BY|CC-BY) ?-?\d+\.\d+"),  # licence names
]
NUMBER = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)*")
LABEL = re.compile(r"\{#(fig|tbl|sec):([\w-]+)[^}]*\}")
REF = re.compile(r"@(fig|tbl|sec):([\w-]+)")
HEADING = re.compile(r"^(#+) .*$", re.M)


def lookup(data: Any, path: str) -> Any:
    cur = data
    for part in path.split("."):
        m = STEP.fullmatch(part)
        if m is None:
            raise KeyError(path)
        key, sel = m.groups()
        cur = cur[key]
        if sel is not None and sel.isdigit():
            cur = cur[int(sel)]
        elif sel is not None:
            conds = [c.split("=", 1) for c in sel.split(",")]
            matches = [x for x in cur if all(str(x.get(k)) == v for k, v in conds)]
            if len(matches) != 1:
                raise KeyError(f"{path}: {len(matches)} rows match [{sel}]")
            cur = matches[0]
    return cur


def fmt(value: Any, spec: str | None) -> str:
    if value is None:
        return "n/a"
    if spec in ("pct", "pct1", "pct2"):
        digits = {"pct": 0, "pct1": 1, "pct2": 2}[spec]
        return f"{100 * float(value):.{digits}f}%"
    if spec == "x2":
        return f"{float(value):.2f}×"
    if spec == "inv":  # "one in N"
        return f"{1 / float(value):.0f}"
    if spec == "verdict":
        return "supported" if value else "not supported"
    if spec:
        return format(value, spec)
    return str(value)


def fill(text: str, data: Any) -> str:
    missing: list[str] = []

    def sub(m: re.Match[str]) -> str:
        try:
            return fmt(lookup(data, m.group(1)), m.group(2))
        except (KeyError, IndexError, TypeError, ValueError) as e:
            missing.append(f"{m.group(1)} ({e})")
            return "??"

    out = TOKEN.sub(sub, text)
    if missing:
        raise SystemExit("missing numbers.json keys:\n  " + "\n  ".join(missing))
    return out


def check(text: str) -> list[tuple[int, str]]:
    """(line, literal) for every number typed by hand in the prose of ``text``."""
    found = []
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        if PRAGMA in line:
            lines[i - 1] = ""
    body = "\n".join(lines)
    # strip while keeping line numbers: replace stripped spans by the same number of newlines
    for rx in NOT_PROSE:
        body = rx.sub(lambda m: "\n" * m.group(0).count("\n"), body)
    for i, line in enumerate(body.splitlines(), 1):
        found += [(i, n) for n in NUMBER.findall(line)]
    return found


def crossref(text: str) -> str:
    """Replace ``@fig:x`` / ``@tbl:x`` / ``@sec:x`` by numbers; an unknown label fails the build."""
    labels: dict[tuple[str, str], str] = {}
    counts = {"fig": 0, "tbl": 0}
    sections: list[int] = []
    body = re.sub(r"```.*?```", "", text, flags=re.S)
    for line in body.splitlines():
        h = HEADING.match(line)
        if h and "{-}" not in line and "{.unnumbered" not in line:
            level = len(h.group(1))
            sections = (sections + [0] * level)[:level]
            sections[-1] += 1
        for m in LABEL.finditer(line):
            kind, name = m.groups()
            if kind == "sec":
                labels[kind, name] = ".".join(map(str, sections))
            else:
                counts[kind] += 1
                labels[kind, name] = str(counts[kind])
    unknown = sorted({m.group(0) for m in REF.finditer(text) if m.groups() not in labels})
    if unknown:
        raise SystemExit("unknown cross-references: " + ", ".join(unknown))
    return REF.sub(lambda m: labels[m.group(1), m.group(2)], text)


def build(root: Path = Path(".")) -> Path:
    src, numbers = root / "paper" / "paper.md", root / "results" / "numbers.json"
    text = src.read_text(encoding="utf-8")
    hand = check(text)
    if hand:
        raise SystemExit(
            "numbers typed by hand in paper/paper.md:\n  " + "\n  ".join(f"line {i}: {n}" for i, n in hand)
        )
    filled = fill(text, json.loads(numbers.read_text()))
    filled = INCLUDE.sub(lambda m: (root / m.group(1)).read_text(encoding="utf-8").strip(), filled)
    filled = crossref(filled)
    out_md, out_pdf = root / "paper" / "paper.filled.md", root / "paper" / "coauthored.pdf"
    out_md.write_text(filled, encoding="utf-8")
    if shutil.which("pandoc") is None or shutil.which("typst") is None:
        raise SystemExit(f"pandoc and typst are needed for the PDF; wrote {out_md}")
    env = {**os.environ, "TYPST_FONT_PATHS": str((root / "paper" / "fonts").resolve())}
    subprocess.run(
        [
            "pandoc",
            str(out_md),
            "-o",
            str(out_pdf),
            "--resource-path",
            str(root),
            "--citeproc",
            "--pdf-engine",
            "typst",
            "--template",
            str(root / "paper" / "templates" / "default.typst"),
        ],
        check=True,
        cwd=root,
        env=env,
    )
    return out_pdf
