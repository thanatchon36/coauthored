---
license: cc-by-4.0
pretty_name: "coauthored: AI-attributed commits in AI infrastructure repositories, 2023–2026"
language:
  - en
size_categories:
  - 10K<n<100K
tags:
  - software-engineering
  - mining-software-repositories
  - git
  - ai-assisted-programming
  - provenance
configs:
  - config_name: repo_month
    data_files: aggregated/repo_month.parquet
  - config_name: repo_month_tool
    data_files: aggregated/repo_month_tool.parquet
---

# coauthored: AI-attributed commits in AI infrastructure repositories, 2023–2026

Monthly counts of AI-attributed commits from the default-branch history of 96 public GitHub repositories,
cloned on one UTC day (2026-10-28): 42 repositories that train, fine-tune, evaluate and serve AI models (S1), 12
open-source coding-agent harnesses (S2), and 42 popular non-AI repositories matched on stars and activity (S3).
Non-merge commits in the study window (2023-01 to 2026-09, primary
specification, before shared-history deduplication): {{COUNTS}}.

A commit is **AI-attributed** when its message carries a co-author trailer naming an AI tool, its author or
committer is an AI-agent account, or it carries a tool's generated-with marker, as listed in the pre-registered
signature catalogue (`configs/signatures.yaml`, three public evidence URLs per entry). Attribution is a
**lower bound** on AI involvement: tools can be configured not to attribute, attribution can be lost at merge,
and some tools never attribute. An attributed commit is not a commit "written by AI".

Paper: *How Much of the Code That Trains the Models Declares AI Help?*
([PDF](https://github.com/thanatchon36/coauthored/blob/main/paper/coauthored.pdf)).
Code: <https://github.com/thanatchon36/coauthored>.

*Independent personal research. Public data only. Does not represent the views of any employer or institution.*

## Privacy

As pre-registered (§11), only aggregates are released: **no per-commit records, no names, no e-mail
addresses, no commit messages and no identity hashes**. Author and committer identities were salted and hashed
at ingest only to count distinct authors per repository-month. The survival and size samples are one row per
sampled pull request or commit, with the repository and month but **no PR number and no commit SHA**. Do not use
this dataset to profile individual developers.

## Files

| path | content |
|---|---|
| `aggregated/repo_month.parquet` | commits, attributed commits, active and attributing authors per repository-month, six specifications, with and without shared-history deduplication |
| `aggregated/repo_month_tool.parquet` | attributed commits per repository-month and tool |
| `aggregated/reverts.parquet` | window commits and later reverts per repository-month and attribution status |
| `data/survival.csv` | sampled merged pull requests (no PR numbers): merge method, attribution on head commits and on the landed commit |
| `data/size_sample.csv` | 2,000 sampled commits (no SHAs): month, attribution, files changed, insertions, deletions |
| `data/policy.csv`, `configs/policy_overrides.yaml` | AI-contribution policy class per repository, with hand corrections |
| `data/manifest.json` | snapshot date, head SHA, default branch, commit counts, git version per repository |
| `configs/` | frozen signature catalogue, bot list, repository lists; `data/s3_match.json` matching output |
| `SHA256SUMS` | checksums of every file above |

## Method

Pre-registered (`PREREGISTRATION.md`, tag `prereg-v1`); deviations in `DEVIATIONS.md`. Code: the `coauthored`
package (Apache-2.0). The paper's tables and figures rebuild from these files; the aggregates themselves rebuild
from a fresh scan of the public repositories (`REPRODUCE.md`).

## Licence

CC BY 4.0. Commit metadata derives from public repositories under their own licences.
