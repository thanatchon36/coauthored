# Phase 9 — adversarial review and resolutions (2026-10-29)

The draft (commit `3c3985c`) was reviewed adversarially by an AI subagent briefed to find overclaims, errors and
missing caveats, without the author's conclusions. Every claim it made was checked against the data or the code
before acting on it; checks are noted. Numbers below are from the revised `results/numbers.json`.

## Blocking

| # | Finding | Check | Resolution |
|---|---|---|---|
| 1 | "Matched non-AI repositories rose just as fast", "same curve", "all of open source" claim equivalence that the data cannot support: the H2 odds-ratio CI runs from about half to almost five. | Confirmed; S3 was above S1 in six consecutive months of 2026 (February–July), and one S3 repository holds about half of S3's attributed commits in 2026-Q3. | Abstract, introduction, results and discussion reframed as *inconclusive*: no evidence of a lead, none of its absence. New post-hoc `robustness` block (month-by-month order, S3 without its largest contributor, repository-weighted shares), DEVIATIONS 10. |
| 2 | Mirror exports from internal monorepos are a fourth leak path, missing from §3, and they dilute S1 (H1 without mirrors 12.2%, CI 6.6–18.5%). | Confirmed: five repositories have mirror-export trailers on at least half their window commits (three in S1). | Added as leak path 3, with the mirror-removed estimate in text and abstract. |
| 3 | The per-commit Hugging Face dataset contradicts PREREGISTRATION §11 ("only repository-month aggregates are published"); `data/survival.csv` and `data/size_sample.csv` carry PR numbers and SHAs. | Confirmed. | Builder now aggregates-only; samples published without identifiers (cache keeps them); DECISIONS D16 revised; DEVIATIONS 13. The committed history still contains the identified samples — **history rewrite to decide at STOP 2**. |
| 4 | Survival mechanism ("GitHub's default squash message lists the messages, trailers included") is not supported by the cited documentation; GitHub also adds `Co-authored-by` for commit authors at squash, an alternative mechanism. | Confirmed against both pages (fetched 2026-10-29): the docs say "title and list of commits" and say nothing about trailers. | Mechanism paragraph rewritten: two candidate mechanisms, not separable here. |
| 5 | Pooled H6 (184/200) mixes an observed rate (squash) with a scoring rule (merge kept by construction; rebase kept unless the last commit lost attribution). | Confirmed in `survival/classify.py`. | Rule stated in the paper and DEVIATIONS 9; squash-only 176/192 reported as the observed result. |
| 6 | Reverts and H7 were computed without shared-history deduplication, unlike every other pooled figure. | Confirmed. | `aggregate` and `h7` now deduplicate (DEVIATIONS 12); S2 revert counts change, S1 and S3 do not. |
| 7 | "Lost to a repository setting, not to a contributor's choice" contradicts the stated loss paths (a person can edit the squash message). | Confirmed. | Sentence removed; recommendation softened. |

## Substantive

| # | Finding | Resolution |
|---|---|---|
| 8 | Validation sample is in-sample (pilot repositories that informed the catalogue), labelled by a Claude subagent, reported without intervals (80/80 has a Wilson lower bound of 95.4%). | Labeller, sample origin and Wilson lower bounds stated in §4 and Limitations. |
| 9 | Attribution conflated with adoption; e.g. `openai/codex` has almost no attributed commits. | "Attribution is not adoption" paragraph in the introduction with the Codex count; Limitations updated. |
| 10 | Gemini Code Assist and Copilot review-suggestion trailers record applied review suggestions, not an agent writing the change. | Described as such; post-hoc spec `no_review_suggestions` (DEVIATIONS 11) reported for H1 and in the sensitivity table. |
| 11 | Repository-weighted shares not reported beside every pooled share (S2 repository-weighted is much higher). | Added for all three strata in 2026-Q3. |
| 12 | Size ratio confounded by time (attributed commits are recent); the S1 2026-only ratio interval includes one. | Year fixed effects added to the within-repository model (post hoc); 2026-only S1 ratio reported. |
| 13 | Revert wording ("no evidence … more or less often") too strong given small counts and detection limited to git's standard revert message; standardisation is post hoc. | Reworded; detection limit stated; labelled post hoc. |
| 14 | "The decisions do not depend on analysis choices" while estimates move substantially; the GLMM flips the sign of the H3 difference and its S2 slope excludes zero. | Rewritten: decisions stable, estimates fragile; GLMM differences stated. |
| 15 | Unlogged post-hoc analyses (revert standardisation, size fixed effects, 2026 restriction). | DEVIATIONS 10; "(post hoc)" in text and sensitivity table. |
| 16 | Survival estimand undefined; PRs truncated at 100 commits. | Estimand defined; truncation stated. |
| 17 | Policy coding checked by Claude after the shares were known (not blind); H7 called "small" while the "mentions" class exceeds "requires disclosure". | Stated in text and the F6 caption; H7 wording changed. |
| 18 | Personal-account repository slugs effectively name a person. | Ethics paragraph; no per-person figures. Raised at STOP 2. |
| 19 | Pre-registration timestamp is self-hosted (git tag in the author's repository). | Raise at STOP 2: a Zenodo release of the tag gives an independent timestamp. |

## Minor

| # | Finding | Resolution |
|---|---|---|
| 20 | OpenHands had a plurality, not "most", in 2025-Q3. | "Plurality through 2025-Q3 (a majority until 2025-Q2)". |
| 21 | F2 hard-codes eight tools; Warp (up to a quarter of a panel's attributions) and OpenCode fall into Other while the caption claims a one-percent rule. Gemini CLI is in the legend with almost no commits. | Palette is now the nine tools with the most attributed commits (Warp, OpenCode in; Gemini CLI out); caption corrected. |
| 22 | "S1 not above S3 in every month" understates: S1 was below S3 in four of the six H2 months. | Count from `robustness` in text. |
| 23 | H6 p-value printed as "0.000". | New `p` format prints "<0.001". |
| 24 | Table caption does not state the null of each p-value. | Nulls stated. |
| 25 | "Overstates" stated as fact for Claude Code's tool share. | "Probably overstates". |
| 26 | F8 caption has the axes backwards; the diagonal is not a natural benchmark. | Caption fixed; text says the line is a visual reference only. |
| 27 | Appendix promises repository lists and exclusions it does not contain. | Repository table added (`scripts/repo_table.py` → `paper/repositories.md`); exclusions pointed to the configs. |
| 28 | F3 never referenced. | Referenced in §5.1. |
| 29 | The ≥100 commits in 2024 inclusion rule (S1, S3) is not stated. | Stated. |
| 30 | Citation nuances: favaro2026 counts lines at one laboratory; horikawa2026 stated too strongly; robbes2026 uses several signals at project level; semianalysis2026 not described as a "floor". | Each reworded. |
| 31 | The title ("Who Writes the Code…") invites the reading the paper disclaims. | Title is the author's choice; raised at STOP 2. |

## Not changed

- The pre-registered decision rules. H1 stays *supported* on its point-estimate rule; the text says the interval
  reaches below the threshold and that it does not survive Holm's correction.
- The catalogue, bot list, strata and S3 match (frozen inputs, §9).
