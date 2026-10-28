# Pre-registration — *Who Writes the Code That Trains the Models? AI Co-Authorship Trailers in AI Infrastructure Repositories, 2023–2026*

- **Author:** Thanatchon Chongmankhong (independent research; public data only; does not represent the views of
  any employer or institution)
- **Frozen at:** git tag `prereg-v1` (this file and the files hashed in §9)
- **Status at freezing:** no repository in S1, S2 or S3 has been cloned or scanned. Strata were selected from
  GitHub API metadata and commit *counts* only; no commit message, trailer or author of any S1–S3 repository was
  read. Signatures, the bot rule, the scanner and the trailer rule were developed on three pilot repositories
  (§3.5) that are excluded from every analysis.

Changes after freezing are logged in [`DEVIATIONS.md`](DEVIATIONS.md) with date, reason and effect.

## 1. Research questions

- **RQ1 (level).** What share of non-bot commits to model-building infrastructure (S1) carries an explicit AI
  attribution, by month, 2023-01 to 2026-09?
- **RQ2 (difference).** Is that share higher than in matched non-AI repositories (S3)?
- **RQ3 (recursion).** Is it higher still in open-source coding-agent harnesses (S2), and which tools attribute
  in which harness repository?
- **RQ4 (tools).** Which tools account for the attributions, and how has the mix changed?
- **RQ5 (undercount).** How much does the signal miss: attribution lost at merge, repository AI-contribution
  policies, tools that do not attribute?
- **RQ6 (exploratory).** Do attributed commits differ in size or revert rate, and how broad is adoption (share of
  active authors with at least one attributed commit)?

**Relation to prior work.** Co-author trailers and agent accounts have already been counted at scale:
Robbes et al. (2026, *TOSEM*) estimate project-level coding-agent adoption on 128,018 GitHub projects from
trailers, configuration files, branch names and labels, and Horikawa et al. (2026) label agent commits by
signature on 7.8M commits and show that signature-based counts are a lower bound. This study does not claim the
signal as new. What it adds is a pre-registered monthly commit-share series for model-building infrastructure
against matched non-AI controls and coding-agent harnesses, a published signature catalogue with evidence for
every entry, a direct measurement of how often attribution survives the merge, and the link to repository
policies. Full review: `docs/literature/REVIEW.md`.

## 2. Definitions

**Unit.** A commit reachable from the default branch at the snapshot. **Primary:** non-merge commits (≤ 1 parent),
month = committer date in UTC, window 2023-01 to 2026-09.

**Denominator.** Commits whose *author* is not a maintenance bot: an author name ending in `[bot]` that is not an
AI-agent account in the signature catalogue, or a listed automation identity (`configs/bots.yaml`). Committers are
ignored (merge and export bots commit human work).

**Numerator — AI-attributed commit.** A commit with any of: (a) a `Co-authored-by:` line, anywhere in the message,
optionally inside a Markdown bullet, whose identity matches a catalogue entry; (b) an author or committer identity
matching an AI-agent account in the catalogue; (c) a verbatim marker from the catalogue. Identity patterns are
full matches on lower-cased email and/or name; no free-text keyword is a signature. Tool label precedence:
co-author trailer > identity > marker. `Assisted-by:` and `Co-developed-by:` lines count like `Co-authored-by:`
when their identity matches; `Signed-off-by:` (a DCO certification) never counts. Rejected candidates and the
reason for each: `docs/signatures-rejected.md`.

**Separate indicator, not in the numerator.** `Assisted-by: AGENT:MODEL` lines without an email (the Linux
kernel's coding-assistant format) cannot be matched to a vendor identity; their monthly count is reported beside
the main series.

**Lower bound.** The paper reports *attributed* commits. It makes no claim about how much code in unattributed
commits was produced with AI assistance.

## 3. Strata and sampling

Inclusion rule, applied to GitHub REST API metadata on 2026-10-28 and not revisited after scanning: public,
not archived, not a fork, ≥ 2,000 stars, ≥ 200 default-branch commits 2025-10-01..2026-10-01; for S1 and S3 also
≥ 100 in 2024. Commit counts include bots and merges.

- **S1 — model-building infrastructure (42 repositories).** README describes training, fine-tuning, evaluating or
  serving models. Layers: training frameworks, model libraries, distributed training, fine-tuning/RL, inference
  and serving, kernels and compilers, evaluation and data. List, layer and rationale: `configs/repos.yaml`.
- **S2 — open-source coding-agent harnesses (12).** Self-description names a coding agent (or agentic development
  environment) as the primary product, and the harness source is in the repository.
- **S3 — matched non-AI controls (one per S1 repository).** From a pool built by GitHub repository search
  (7 languages × 4 star bands, pushed since 2026-09-01), excluding AI/ML topics and AI terms in name or
  description, non-software repositories and every S1/S2/pilot/excluded candidate. Seeded greedy nearest-neighbour
  match within the same language group, caliper ±50% on stars and on last-12-month commits, distance
  `|log stars ratio| + |log commits ratio|`, seed 20261028; outside-caliper matches are flagged. Each matched
  control was then screened by hand on metadata and README (software project; no model training or ML inference
  at its core); six were screened out with reasons (`configs/s3_screen.yaml`) and the match re-run until all
  passed. Output: `data/s3_match.json`.
- **Pilot repositories (excluded):** modelcontextprotocol/python-sdk, microsoft/typescript-go,
  openai/openai-agents-python.

Exclusions with reasons are listed in `configs/repos.yaml` (`excluded`).

**Snapshot.** All S1–S3 repositories are cloned on one calendar day; head SHAs are recorded in
`data/manifest.json`; all counting is from those SHAs.

**Shared history.** Pooled stratum figures deduplicate commits by SHA across repositories, keeping the
earliest-created repository. Per-repository figures use each repository's full history.

## 4. Hypotheses and decision rules

All shares are commit-pooled unless stated; repo-weighted shares (mean of per-repository shares, repository-months
with ≥ 10 commits) are reported beside every pooled share. Confidence intervals are percentile intervals from
2,000 cluster-bootstrap resamples of repositories within stratum (seed 20261028).

- **H1 (level).** The pooled attributed share in S1 for 2026-07..2026-09 is ≥ 5%. *Supported* if the point
  estimate is ≥ 5%; the 95% CI is reported.
- **H2 (difference).** The pooled S1 share exceeds the pooled S3 share in each month 2026-04..2026-09, **and** the
  pooled 2026-Q3 odds ratio S1:S3 is ≥ 2 with a 95% CI excluding 1. *Supported* only if all three hold.
- **H3 (growth).** On repository-month counts 2025-03..2026-09, a binomial GLM
  `logit(share) ~ month × stratum` (S1, S2, S3) has a positive month slope in S1 and in S2 (CIs exclude 0) and an
  S1 slope greater than the S3 slope (CI of the difference excludes 0). *Supported* only if all three hold.
- **H4 (recursion).** The pooled 2026-Q3 share in S2 exceeds that in S1 (CI of the difference excludes 0).
- **H5 (tools).** Claude Code accounts for the plurality of attributed commits in S1 ∪ S2 in every quarter from
  2025-Q2 to 2026-Q3. *Note:* Claude Code adds a co-author trailer by default, so H5 tests the instrument as much
  as tool usage.
- **H6 (survival).** Among sampled merged pull requests with ≥ 1 attributed head commit, ≥ 80% have the attribution
  on the default branch after merge (§5).
- **H7 (policy, exploratory).** Repositories whose AI-contribution policy requires disclosure have a higher
  attributed share than those that ban AI contributions or are silent (§6).

Holm correction across H1–H6 for the family-wise claim; each hypothesis is also reported on its own rule.

## 5. Survival study (RQ5, H6)

Merged pull requests in S1 ∪ S2 with merge date 2025-06-01..2026-09-30, sampled uniformly at random within each
repository (seed 20261028), repositories visited round-robin. For each, fetch the PR's commits and its landed
commit (`merge_commit_sha`). Classify merge method: *merge* (landed commit has two parents), *rebase* (more than one
PR commit and the landed commit's message equals the last PR commit's message), *squash* (otherwise; single-commit
PRs whose landed message differs from the PR commit's message are squash, identical messages are
*single-commit-ambiguous*). Survival: for squash and single-commit cases, the landed commit is attributed; for merge
and rebase, the landed commit or the PR's commits on the default branch are attributed. Stop when 200 PRs with an
attributed head commit are found or 4,000 PRs have been inspected. Report survival overall and by merge method,
with Wilson CIs.

## 6. Policy coding (RQ5, H7)

At the snapshot, fetch `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`, `.github/CONTRIBUTING.md`,
`.github/PULL_REQUEST_TEMPLATE*`, `.github/copilot-instructions.md` for every S1–S3 repository. Classify into
**bans**, **requires disclosure**, **mentions without a rule**, **silent**. Rule-based first pass
(`src/coauthored/policy/classify.py`): sentences that name AI or an AI tool are matched against prohibition and
disclosure phrasings; a request for an `Assisted-by:`-style trailer counts as disclosure; the strongest class
found wins (bans > requires disclosure > mentions). `AGENTS.md` and `CLAUDE.md` address agents, not contributors,
and are not read for policy. Every non-silent classification is checked by hand with the quoted sentence in
`docs/policy-review.md`; hand corrections are recorded there. The presence of `AGENTS.md`, `CLAUDE.md` or
`.github/copilot-instructions.md` is reported separately as an *agent-configuration* indicator.

## 7. Exploratory (RQ6)

Size: a random sample of 2,000 window commits, stratified by attributed/not and stratum, lines changed via
`git show --shortstat` on blob-fetched clones. Reverts: commits whose message starts with `Revert "` and reference
a reverted SHA; revert rate of attributed vs. unattributed commits. Breadth: per repository-month, distinct hashed
authors with ≥ 1 attributed commit ÷ distinct active authors.

## 8. Sensitivity analyses

Author date instead of committer date; merges included; first-parent commits only; strict trailer position
(final trailer block, as `git interpret-trailers --parse --no-divider`); maintenance bots included; the three
largest repositories of each stratum removed; mirror-exported repositories removed (≥ 50% of window commits carry
`PiperOrigin-RevId`, `fbshipit-source-id`, `GitOrigin-RevId` or `MODULAR_ORIG_COMMIT_REV_ID`); outside-caliper
S3 matches removed; a binomial GLMM with a random intercept and slope per repository instead of the GLM in H3.

## 9. Frozen inputs

| File | SHA-256 |
|---|---|
| `configs/signatures.yaml` | `0b3094d666c465c652150a2aa15b86e796e3e2cfc4347fe3484c439c16a736f7` |
| `configs/bots.yaml` | `349e42668b3a4ed7d76f0103aca7985f244fba516c3c9ed9c99ae57125df1210` |
| `configs/repos.yaml` | `36f50a3f7534e7ad627a5777681f8e9aaa103bc49af71eca200e6723c5337d9d` |
| `configs/s3_screen.yaml` | `b595c0c3a6409171210b22a983970df187868a0a7e9e749c7c964cca1078ede7` |
| `data/s3_match.json` | `ee18d2cd605679b1ce49587f7d7924f63a79633be6e068c2a5cfb51f33863f39` |

A signature found after freezing may be added only as a logged deviation, after which every number is recomputed
and both versions are reported.

## 10. Negative results

Every hypothesis is reported as supported or not supported on its rule. If attributed shares are near zero, the
paper reports that the recursion is invisible in the commit log and quantifies how much the lower bound can hide.

## 11. Ethics

Public data only. Author and committer identities are replaced by salted hashes at ingest; no names, emails or
commit messages are stored. Only repository-month aggregates are published. No individual developer is named.
