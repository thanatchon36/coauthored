# Phase 3 report — pilot run and snapshot estimate (STOP 1)

## Pilot run

Fresh clones of the three pilot repositories, one `coauthored scan` call (`data/pilot_manifest.json`):

| repository | commits | attributed (any month) | clone | scan | clone size | records |
|---|---:|---:|---:|---:|---:|---:|
| modelcontextprotocol/python-sdk | 1,109 | 32 | 1.1 s | 0.8 s | 1.0 MB | 43 kB |
| microsoft/typescript-go | 2,491 | 381 | 1.6 s | 1.4 s | 3.8 MB | 96 kB |
| openai/openai-agents-python | 2,547 | 6 | 1.2 s | 1.0 s | 2.3 MB | 98 kB |
| **total** | **6,147** | **419** | | | **7.1 MB** | **237 kB** |

Wall time 7.4 s. Scan throughput about 1,900 commits/s on one core; clone size about 1.2 MB per 1,000 commits
with `--filter=tree:0`; records about 39 bytes per commit after zstd.

Pilot attributions come mostly from the Copilot coding agent in typescript-go. These numbers are for sizing only;
pilot repositories are excluded from every analysis.

## Snapshot estimate

Full default-branch history (REST commit counts, `scripts/count_history.py`):

| stratum | repositories | commits |
|---|---:|---:|
| S1 | 42 | 733,589 |
| S2 | 12 | 148,201 |
| S3 | 42 | 1,968,860 |
| **total** | **96** | **2,850,650** |

S3 is larger than S1 because matching is on stars and recent activity, not on history length; LibreOffice/core
alone has 521,566 commits. Commit-share outcomes are per month, so history length does not bias them.

Extrapolated from the pilot: scan about 25 minutes single-threaded; clones about 3.5 GB and records about 110 MB.
Clone time is dominated by network; the largest histories should take a few minutes each. Disk free: 616 GB.
Expected total: under 2 hours on one machine, one calendar day as pre-registered.

## Phase 6 (GH Archive) estimate

`bq` and `gcloud` are not installed here, so no dry-run estimate was made. Phase 6 needs the user to install the
Google Cloud SDK and authenticate, and stays within the BigQuery free tier only if the query reads the
`githubarchive.month.*` tables for push events with column pruning; the dry run is the first step of Phase 6.

## Asking at STOP 1

Approval to (1) take the S1–S3 snapshot (clone and scan all 96 repositories on one day), (2) run the survival
sampler against the GitHub API and (3) fetch repository policy files. Nothing will be made public.
