# Phase 4 report — snapshot, aggregates and policy files

## Snapshot

All 96 repositories (S1 42, S2 12, S3 42) were cloned and scanned on one UTC calendar day, 2026-10-28
(2026-10-29 local), as pre-registered. Head SHAs, default branches, commit counts, timings and sizes are in
`data/manifest.json`.

| stratum | repositories | commits (all history) | attributed (all history) | clone + scan | clone size |
|---|---:|---:|---:|---:|---:|
| S1 model infrastructure | 42 | 733,731 | 9,786 | 235 s | 0.42 GB |
| S2 coding-agent harnesses | 12 | 148,274 | 8,640 | 57 s | 0.12 GB |
| S3 matched controls | 42 | 1,968,946 | 7,135 | 340 s | 0.78 GB |
| **total** | **96** | **2,850,951** | **25,561** | **632 s** | **1.32 GB** |

The snapshot counts are within 0.02% of the REST estimates taken before STOP 1 (2,850,650), the difference being
commits landed between the two dates. Raw per-commit records (hashed identities, flags, matched signature ids; no
names or e-mail addresses) total 110.7 MB and stay out of git (`data/raw/`, for the dataset release).

## Aggregates

`coauthored aggregate --config configs/repos.yaml` writes `data/aggregated/` (124 kB):

- `repo_month.parquet` — commits, attributed commits, active and attributing authors (hashed), mirror-export and
  bare-`Assisted-by` counts per repository-month, for each of the six specifications (primary and five
  sensitivity variants), with and without shared-history deduplication.
- `repo_month_tool.parquet` — attributed commits per repository-month and tool.
- `reverts.parquet` — window commits and later reverts per repository-month and attribution status.

Rebuilding the aggregates from the raw records reproduces `repo_month` and `repo_month_tool` byte-for-byte.

Window commits (primary specification, 2023-01..2026-09, shared history removed within stratum):

| stratum | commits | attributed | bare `Assisted-by: AGENT:MODEL` lines |
|---|---:|---:|---:|
| S1 | 407,527 | 6,785 | 140 |
| S2 | 93,359 | 6,889 | 62 |
| S3 | 374,109 | 5,220 | 0 |

Shared history matters only in S2 (forks such as Kilo-Org/kilocode of cline/cline): 118,672 commits without
deduplication against 93,359 with it.

## Policy files

`scripts/fetch_policies.py` read the pre-registered policy files at each repository's snapshot head SHA
(GraphQL, one query per repository). The rule-based first pass and a hand check of every non-silent case are in
`docs/policy-review.md`; corrections are in `configs/policy_overrides.yaml`.

| class | repositories |
|---|---:|
| bans | 1 |
| requires disclosure | 20 |
| mentions without a rule | 16 |
| silent | 59 |

55 of 96 repositories carry an agent-configuration file (`AGENTS.md`, `CLAUDE.md` or
`.github/copilot-instructions.md`). Six repositories point to a policy outside the pre-registered files; they
are coded on the pre-registered files only (limitation, `docs/policy-review.md`).

## First results (interim, B = 100)

The full run with B = 2,000 follows once the survival sample is complete; point estimates below do not depend on
B.

- 2026-Q3 pooled attributed share: S1 8.70%, S2 10.32%, S3 7.12%. In 2024: S1 0.00%, S2 1.10%, S3 0.01%.
- H1 (S1 ≥ 5%) supported; H2 (S1 > S3), H3 (S1 grows faster than S3), H4 (S2 > S1) and H5 (Claude Code
  plurality in every quarter) not supported. H1 holds and H2–H4 fail in every sensitivity analysis, including the
  GLMM for H3 (S1−S3 slope −0.024 per month, Wald CI −0.105..0.058).
- Tool mix: OpenHands leads 2025-Q1..Q3, Gemini Code Assist 2025-Q4, Claude Code from 2026-Q1 (34%, 42%, 52%).
- Reverts: the crude revert rate of attributed commits is lower in every stratum, but this is composition. At the
  unattributed rate of the same repository and month (commits to 2026-06), observed/expected is S1 1.17
  [0.78, 1.68], S2 0.78 [0.29, 1.70], S3 0.35 [0.01, 1.92].

Headline so far: AI-infrastructure repositories carry AI attribution at about the same rate as matched popular
repositories; the rise since 2025 is general, not specific to the projects that build AI.
