# Reproducing the paper

Three levels, from cheapest to most complete. Each needs Python ≥ 3.11 and [`uv`](https://docs.astral.sh/uv/).
None needs an API key or a paid service.

```bash
git clone https://github.com/thanatchon36/coauthored && cd coauthored
uv sync --all-extras
```

## 1. Every table, figure and number, from the committed aggregates (about 15 minutes, no network)

```bash
uv run coauthored analyze --draws 2000   # results/numbers.json, results/tables/, results/figures/
git diff --stat results/                 # empty: the output is byte-identical
```

Inputs are `data/aggregated/*.parquet`, `data/survival.csv`, `data/size_sample.csv`, `data/policy.csv`,
`configs/policy_overrides.yaml` and the frozen `configs/`. The bootstrap seed is 20261028. `--draws 100` runs in
about a minute and changes only the confidence intervals.

## 2. The PDF

Needs pandoc ≥ 3.8 and Typst ≥ 0.13 on the `PATH`; fonts are vendored in `paper/fonts/`.

```bash
uv run coauthored paper    # paper/coauthored.pdf
```

The build fills every number from `results/numbers.json` and fails if a number in `paper/paper.md` is typed by hand
(`src/coauthored/paper.py`).

## 3. The aggregates, from the repositories (about 15 minutes and 1.4 GB of disk on a fast connection)

```bash
uv run coauthored scan --config configs/repos.yaml     # clones with commit objects only, writes data/raw/
uv run coauthored aggregate --config configs/repos.yaml
```

`data/manifest.json` records the head SHA of every repository at the 2026-10-28 snapshot. A scan today reads the
current default branch, so its aggregates differ slightly from the committed ones: branches merged after the
snapshot can bring in commits dated inside the window (which ends 2026-09-30), and rewritten history can drop
some. The committed aggregates are the ones the paper uses. Identities are hashed with a salt that `scan` creates in a git-ignored `.env` on first
use; a new salt gives different hashes and the same counts.

The survival sample and the policy files come from the GitHub API through your own `gh` login, at no cost; the
size sample reads the clones:

```bash
uv run python scripts/survival_sample.py   # data/survival.csv (H6); a few thousand GraphQL calls
uv run python scripts/size_sample.py       # data/size_sample.csv (RQ6), from the clones
uv run python scripts/fetch_policies.py    # data/policy.csv (H7), then hand corrections in configs/policy_overrides.yaml
```

Merged pull requests and contribution guidelines change over time, so a fresh survival sample or policy fetch will
not be identical; the committed files are the ones the paper uses.

## Your own organisation

```bash
uv run coauthored report --org <your-org>     # Markdown table of monthly attributed share since 2024-01
```

Read `RESPONSIBLE_USE.md` first.

## What is frozen

The pre-registration is tagged `prereg-v1` (commit `27a6847`). `git diff prereg-v1 -- configs/signatures.yaml
configs/bots.yaml configs/repos.yaml data/s3_match.json` is empty. Every later change to the analysis is listed in
`DEVIATIONS.md`.
