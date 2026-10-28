---
license: cc-by-4.0
pretty_name: "coauthored: AI-attributed commits in AI infrastructure repositories, 2023–2026"
language:
  - en
size_categories:
  - 1M<n<10M
tags:
  - software-engineering
  - mining-software-repositories
  - git
  - ai-assisted-programming
  - provenance
configs:
  - config_name: commits
    data_files:
      - split: s1_model_infrastructure
        path: commits/s1.parquet
      - split: s2_coding_agent_harnesses
        path: commits/s2.parquet
      - split: s3_matched_controls
        path: commits/s3.parquet
  - config_name: repo_month
    data_files: aggregated/repo_month.parquet
  - config_name: repo_month_tool
    data_files: aggregated/repo_month_tool.parquet
---

# coauthored: AI-attributed commits in AI infrastructure repositories, 2023–2026

Per-commit attribution flags for the full default-branch history of 96 public GitHub repositories, cloned on
one UTC day (2026-10-28): 42 repositories that train, fine-tune, evaluate and serve AI models (S1), 12
open-source coding-agent harnesses (S2), and 42 popular non-AI repositories matched on stars and activity (S3).
Commits: {{COUNTS}}.

A commit is **AI-attributed** when its message carries a co-author trailer naming an AI tool, its author or
committer is an AI-agent account, or it carries a tool's generated-with marker, as listed in the pre-registered
signature catalogue (`configs/signatures.yaml`, three public evidence URLs per entry). Attribution is a
**lower bound** on AI involvement: tools can be configured not to attribute, attribution can be lost at merge,
and some tools never attribute. An attributed commit is not a commit "written by AI".

## Privacy

The records hold **no names, no e-mail addresses, no commit messages and no identity hashes**. Author and
committer identities were salted and hashed at ingest for counting distinct authors; those hashes are not part
of this release, and distinct-author counts are published only as repository-month aggregates. Dates are
given in UTC, so time-zone offsets are not published. Do not use this dataset to profile individual developers.

## Files

| path | content |
|---|---|
| `commits/s{1,2,3}.parquet` | one row per commit on the default branch at the snapshot head (fields below) |
| `aggregated/repo_month.parquet` | commits, attributed commits, active and attributing authors per repository-month, six specifications, with and without shared-history deduplication |
| `aggregated/repo_month_tool.parquet` | attributed commits per repository-month and tool |
| `aggregated/reverts.parquet` | window commits and later reverts per repository-month and attribution status |
| `data/survival.csv` | sampled merged pull requests: merge method, attribution on head commits and on the landed commit |
| `data/size_sample.csv` | 2,000 sampled commits: files changed, insertions, deletions |
| `data/policy.csv`, `configs/policy_overrides.yaml` | AI-contribution policy class per repository, with hand corrections |
| `data/manifest.json` | snapshot date, head SHA, default branch, commit counts, git version per repository |
| `configs/` | frozen signature catalogue, bot list, repository lists; `data/s3_match.json` matching output |
| `SHA256SUMS` | checksums of every file above |

## Commit fields

| field | meaning |
|---|---|
| `repo`, `stratum` | repository (`owner/name`) and stratum (S1, S2, S3) |
| `sha` | commit SHA |
| `n_parents`, `first_parent` | number of parents; on the first-parent chain of the default branch |
| `author_date`, `committer_date` | UTC timestamps |
| `author_maint_bot`, `committer_maint_bot` | maintenance bot (dependency updates, releases; `configs/bots.yaml`), not an AI agent |
| `attributed`, `attributed_strict` | AI-attributed under the lenient rule / with co-author trailers only in the final trailer block |
| `signature_ids`, `tool` | matched catalogue entries and the tool they belong to |
| `n_coauthor_lines` | number of co-author trailer lines of any kind |
| `bare_assisted` | kernel-style `Assisted-by: AGENT:MODEL` line (separate indicator, not counted as attributed) |
| `is_revert`, `reverted_sha` | revert commit and the SHA it reverts |
| `mirror_export` | carries a mirror-export trailer (`PiperOrigin-RevId`, `fbshipit-source-id`, …) |
| `shared_with_earlier_repo` | the same commit appears in an earlier-created repository of the stratum (forks, vendored history); pooled figures drop these |

## Method

Pre-registered (`PREREGISTRATION.md`, tag `prereg-v1`); deviations in `DEVIATIONS.md`. Code: the `coauthored`
package (Apache-2.0), which rebuilds every aggregate, table and figure of the paper from these files.

## Licence

CC BY 4.0. Commit metadata derives from public repositories under their own licences.
