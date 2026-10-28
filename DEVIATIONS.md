# Deviations from the pre-registration

The pre-registration (`PREREGISTRATION.md`) was frozen at tag `prereg-v1` (commit `27a6847`, 2026-10-29).
Every change or clarification after that tag is logged here with date, what changed, why, and its effect on
results. None of the entries below changes the frozen inputs (§9): the catalogue, bot list, strata and S3 match
are byte-identical to the tagged versions.

| # | Date | What | Why | Effect |
|---|---|---|---|---|
| 1 | 2026-10-29 | Month bucketing parses `Z` as a UTC offset (`9eb6991`). | Newer git prints iso-strict UTC dates as `Z`, which the parser rejected on CI. A bug fix, not a change of rule. | None on results; the same months either way. |
| 2 | 2026-10-29 | One-sided p-values for H1–H5 are bootstrap p-values: `(#draws on or below the null + 1) / (B + 1)`, null 5% for H1, log OR 0 for H2, 0 for the differences in H3–H5; H6 uses an exact one-sided binomial test against 0.8. Holm is applied to these six. | §4 asks for Holm across H1–H6 but did not say how the p-values are obtained. The rule uses the same cluster bootstrap (B = 2,000, repositories resampled within stratum) as the confidence intervals, so the decision rule and the p-value agree. | Operationalisation only. Each hypothesis is still decided on its own pre-registered CI rule. |
| 3 | 2026-10-29 | H7 is printed as *exploratory* with its sign, not as *supported*/*not supported*, and carries no CI or p-value. | §4 labels H7 exploratory. | Presentation only. |
| 4 | 2026-10-29 | The GLMM robustness check (§8) is fitted with the package's own Laplace-approximation code (`src/coauthored/analysis/glmm.py`; random intercept and slope per repository, Wald CIs). | R/lme4 is not a dependency and `statsmodels`' mixed GLM needs one row per binary outcome (451,203 commits in the H3 window). The code is tested for recovery on simulated data. | None on the rule; reported as the `glmm` row of the sensitivity table. |
| 5 | 2026-10-29 | Size sample (§7): `git show --shortstat` runs in the snapshot clones, which are treeless; git fetches the trees and blobs each diff needs on demand, instead of from a separate `--filter=blob:none` clone. | Same objects and the same output, without a second clone of 96 repositories. | None. |
| 6 | 2026-10-29 | Survival frame (§5): merged pull requests are listed newest-created first and listing stops at PRs created before 2024-06-01. A PR created before that date but merged 2025-06-01 or later is outside the frame. | Listing every merged PR of the largest repositories since their creation costs thousands of API calls for a handful of very old PRs. | Affects only PRs open for at least a year before merging; not measured. Limitation noted in the paper. |
| 7 | 2026-10-29 | Survival frame (§5): "merged" means GitHub's `MERGED` state. Repositories that land pull requests with a merge bot and close them (pytorch/pytorch: 503 PRs in `MERGED` state in the window) contribute only those PRs. | Closed-and-landed PRs cannot be told apart from rejected PRs without parsing bot comments, which §5 does not specify. | Under-represents bot-landed workflows. Limitation noted in the paper. |
