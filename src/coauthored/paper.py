"""`coauthored paper`: fill paper/paper.md from results/numbers.json and build the PDF (pandoc → Typst).

Placeholders: ``{{dotted.path}}`` or ``{{dotted.path|fmt}}``. List elements are addressed by ``key=value``
selectors, e.g. ``{{summary.quarterly[stratum=S1,q=2026-Q3].share|pct1}}``, or by index (``ci[0]``).
``fmt`` is a Python format spec (``.2f``, ``,``, ``d``) or one of ``pct`` / ``pct1`` / ``pct2``
(percentages), ``pp1`` (percentage points), ``x2`` (ratio as ``1.23×``), ``inv`` (``N`` in "one in N") and
``verdict``; negative numbers get a typographic minus. A missing key fails the build, and so does a number
typed by hand in the prose (``check``): every result in the paper comes from numbers.json (MISSION §7.3). A
line may opt out with ``<!-- numbers-ok: reason -->``, for pre-registered thresholds and design constants.
``<!-- include: path -->`` on its own line inserts a generated table.
``@fig:x``, ``@tbl:x`` and ``@sec:x`` become the number of the figure, table or numbered section labelled
``{#fig:x}`` etc., counted in order of appearance as Typst numbers them (``crossref``); citeproc would
otherwise read them as citations. ``reader`` writes the same text as a standalone web page.
"""

from __future__ import annotations

import html
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
FRONT = re.compile(r"\A---\n(.*?)\n---\n", re.S)
IMAGE = re.compile(r"^(!\[)(.*?)(\]\([^)]*\)\{#fig:[^}]*\})", re.M | re.S)
TABLE = re.compile(r"^: (.+?) \{#tbl:[^}]*\}$", re.M)
REPO_URL = "https://github.com/thanatchon36/coauthored"
TAGS = {"pos": "supported", "ref": "not supported", "nf": "exploratory"}


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
    out = _fmt(value, spec)
    return "−" + out[1:] if out.startswith("-") else out  # typographic minus


def _fmt(value: Any, spec: str | None) -> str:
    if value is None:
        return "n/a"
    if spec in ("pct", "pct1", "pct2"):
        digits = {"pct": 0, "pct1": 1, "pct2": 2}[spec]
        return f"{100 * float(value):.{digits}f}%"
    if spec == "pp1":  # a difference of shares, in percentage points
        return f"{100 * float(value):.1f}"
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


def number_captions(body: str) -> str:
    """Prefix figure and table captions with "Figure n." / "Table n.", as Typst does in the PDF."""
    fig, tab = iter(range(1, 1000)), iter(range(1, 1000))
    body = IMAGE.sub(lambda m: f"{m.group(1)}Figure {next(fig)}. {m.group(2)}{m.group(3)}", body)
    return TABLE.sub(lambda m: f"**Table {next(tab)}.** {m.group(1)}", body)


def results(data: dict[str, Any]) -> list[tuple[str, str, str, str]]:
    """(id, kind, statement, detail) per hypothesis for the web page's results strip."""
    out = []
    for r in data["hypotheses"]:
        h = r["hypothesis"]
        kind = "nf" if h == "H7" else ("pos" if r["supported"] else "ref")
        pct = h in ("H1", "H4", "H5", "H6", "H7")
        est = fmt(r["estimate"], "pct1" if pct else ".3f")
        detail = f"estimate {est}"
        if r["ci"][0] is not None and h != "H7":
            spec = "pct1" if pct else ".3f"
            detail += f", 95% CI {fmt(r['ci'][0], spec)} to {fmt(r['ci'][1], spec)}"
        if r.get("p_holm") is not None:
            detail += f", Holm p {r['p_holm']:.3f}"
        out.append((h, kind, str(r["statement"]), detail))
    return out


def reader(root: Path, filled: str, data: dict[str, Any], pdf: Path) -> Path:
    """Standalone web page docs/site/paper/index.html with the same text as the PDF."""
    m = FRONT.match(filled)
    head, body = (filled[: m.end()], filled[m.end() :]) if m else ("", filled)
    site = root / "docs" / "site" / "paper"
    site.mkdir(parents=True, exist_ok=True)
    out = site / "index.html"
    subprocess.run(
        [
            "pandoc",
            "--from=markdown+smart",
            "--to=html5",
            f"--template={root / 'paper' / 'reader.html'}",
            "--standalone",
            "--citeproc",
            "--number-sections",
            "--toc",
            "--toc-depth=1",
            "--wrap=none",
            "--metadata=pagetitle:coauthored — paper",
            "-o",
            str(out),
        ],
        input=head + number_captions(re.sub(r"<!--.*?-->", "", body, flags=re.S)),
        text=True,
        check=True,
        cwd=root,
    )
    snap = data["summary"]["snapshot"]
    meta = (
        f"<b>coauthored</b> · {snap['repositories']} repositories · "
        f"{snap['commits_all']:,} commits read on 2026-10-28 · pre-registered at tag <code>prereg-v1</code>"
    )
    actions = (
        '<li><a href="paper.pdf">Download PDF</a></li>'
        f'<li><a href="{REPO_URL}">Source code</a></li>'
        f'<li><a href="{REPO_URL}/blob/main/PREREGISTRATION.md">Pre-registration</a></li>'
        f'<li><a href="{REPO_URL}/blob/main/REPRODUCE.md">Reproduce</a></li>'
    )
    note = (
        "Pre-registered hypotheses and their decisions at the frozen thresholds, generated from "
        "<code>results/numbers.json</code>. Shares are of AI-attributed commits, a lower bound."
    )
    items = "\n".join(
        f'<li class="r r-{k}"><span class="r-id">{html.escape(i)}</span>'
        f'<span class="r-text">{html.escape(t)}<small>{html.escape(x)}</small></span>'
        f'<span class="r-tag">{TAGS[k]}</span></li>'
        for i, k, t, x in results(data)
    )
    cite = (
        "<h2>How to cite</h2><pre><code>"
        + html.escape(
            "@misc{chongmankhong2026coauthored,\n"
            "  author = {Chongmankhong, Thanatchon},\n"
            "  title  = {Who Writes the Code That Trains the Models? AI Co-Authorship Trailers in AI\n"
            "            Infrastructure Repositories, 2023--2026},\n"
            "  year   = {2026},\n"
            f"  url    = {{{REPO_URL}}}\n}}"
        )
        + "</code></pre>"
    )
    colophon = (
        "<p>Code, analysis and manuscript draft by Claude (Anthropic) under the author's specification; the "
        "author is responsible for the content. Independent personal research. Public data only. Does not "
        "represent the views of any employer or institution.</p>"
        "<p>Rendered from <code>paper/paper.md</code> by <code>coauthored paper</code>. Every number is "
        "filled from <code>results/numbers.json</code>; <code>coauthored analyze</code> regenerates it from "
        "the committed aggregates.</p>"
    )
    page = out.read_text(encoding="utf-8").replace('src="results/figures/', 'src="figures/')
    for marker, value in (
        ("<!--META-->", meta),
        ("<!--ACTIONS-->", actions),
        ("<!--RESULTS-NOTE-->", note),
        ("<!--RESULTS-->", items),
        ("<!--CITE-->", cite),
        ("<!--COLOPHON-->", colophon),
    ):
        if marker not in page:
            raise SystemExit(f"paper/reader.html lacks {marker}")
        page = page.replace(marker, value)
    out.write_text(page, encoding="utf-8")
    shutil.copyfile(pdf, site / "paper.pdf")
    (site / "figures").mkdir(exist_ok=True)
    for name in sorted(set(re.findall(r'src="figures/([\w.-]+)"', page))):
        shutil.copyfile(root / "results" / "figures" / name, site / "figures" / name)
    return out


def build(root: Path = Path(".")) -> Path:
    src, numbers = root / "paper" / "paper.md", root / "results" / "numbers.json"
    text = src.read_text(encoding="utf-8")
    hand = check(text)
    if hand:
        raise SystemExit(
            "numbers typed by hand in paper/paper.md:\n  " + "\n  ".join(f"line {i}: {n}" for i, n in hand)
        )
    data = json.loads(numbers.read_text())
    filled = fill(text, data)
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
    reader(root, filled, data, out_pdf)
    return out_pdf
