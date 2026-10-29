# Phase 5 report — survival of attribution through the merge (H6)

## Sample

`scripts/survival_sample.py` (PREREGISTRATION §5; frame clarified in `DEVIATIONS.md` 6–7) listed merged pull
requests of every S1 and S2 repository through the GitHub GraphQL API (merged 2025-06-01 to 2026-09-30, listing
stopped at PRs created before 2024-06-01), shuffled each repository's list with seed 20261028, and visited the
repositories in turn, ten pull requests at a time, until 200 pull requests with at least one attributed head
commit had been found (cap 4,000 inspected). It stopped after **2,542 inspected** (S1 1,978, S2 564) with
**200 attributed** (S1 120, S2 80) from 41 repositories. 15 pull requests had more than 100 commits; only their first 100
were read (`head_truncated`), which can only miss attribution, not add it.

Only flags are kept: `cache/survival/` (git-ignored) holds repository, PR number, merge method, attribution
flags, tool names and commit counts; the published `data/survival.csv` has the same columns without the PR
number (DEVIATIONS 13). Commit authors and messages are read in memory by the
pre-registered matcher and never written.

| merge method | inspected | attributed head | attribution survived |
|---|---:|---:|---:|
| squash | 2,177 | 192 | 176 |
| merge commit | 150 | 6 | 6 |
| rebase | 32 | 2 | 2 |
| single commit, method ambiguous | 183 | 0 | – |
| **all** | **2,542** | **200** | **184** |

## Result

**H6 supported.** 184 of 200 (92.0%; Wilson 95% CI 87.4–95.0%; exact one-sided binomial test against 80%,
p = 2.5 × 10⁻⁶). Resampling repositories rather than pull requests (not pre-registered, `DEVIATIONS.md` 8)
gives 87.3–96.2%. All 16 losses were squash merges, spread over 10 repositories (at most 3 in one), so they look
like per-merge message edits or title-and-description squash settings rather than one repository's policy.

## Bug found and fixed on the way

The first full analysis reported H6 as 0 of 200: `load_survival` compared polars' lowercase booleans with
`"True"`/`"False"` and turned every flag into null. The synthetic test had written the CSV with polars, which
hid the bug. Fixed in `41c39d5`; the fixture now writes the CSV the way the sampler does and the smoke test
asserts k and n.

## Consequence for the paper

Little attribution is lost at the merge in these repositories. The other two leaks (attribution switched off,
tools that never attribute) cannot be measured from git metadata, so the size of the undercount stays unknown.
The paper says this in §6 and in the discussion.
