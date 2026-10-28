# Phase 1 report — instrument, strata, pre-registration

Everything here was built on three pilot repositories (modelcontextprotocol/python-sdk, microsoft/typescript-go,
openai/openai-agents-python) and on GitHub API metadata. No S1, S2 or S3 repository was cloned or scanned before
the `prereg-v1` tag.

## Scanner

Bare, single-branch, `--filter=tree:0` clones; one streaming `git log -z` pass over the default branch; per-commit
records with salted 16-hex identity hashes and flags only (no names, emails or messages), zstd-compressed JSONL.
Pilot throughput: 6,147 commits cloned and scanned in 7.4 s wall time (`data/pilot_manifest.json`).

## Signature catalogue

`configs/signatures.yaml`: 52 entries for 28 tools (31 co-author identities, 16 agent accounts, 5 verbatim markers), every one with three evidence URLs. A first pass searched message text; agent accounts, which appear as authors rather than in messages, were then searched with the `author-email:`/`committer-email:` qualifiers. One candidate (Sweep) stayed below three and was dropped. Each entry carries the GitHub commit-search query used to find it
and up to three evidence URLs (distinct repositories first), each verified by running the matcher on the commit
returned by the API. Rejected candidates and the reason for each: `docs/signatures-rejected.md`.

## Trailer rule

The lenient primary rule counts a co-author line anywhere in the message, optionally inside a Markdown bullet. The
strict sensitivity rule counts only lines in the final trailer block. Our trailer-block rule agrees with
`git interpret-trailers --parse --no-divider` on all 1,565 pilot commits that have a trailer-like final paragraph
(`scripts/validate_trailers.py`). Without `--no-divider`, git stops at a `---` line, which squash-merge messages
often contain; agreement was then 95.4%.

## Validation sample

200 pilot commits drawn with seed 20261028: 80 the scanner attributes, 70 near-misses (an AI tool word in the
message or identity, not attributed) and 50 others. Labels were given by an independent reader who saw a condensed
sheet (people's identities masked) and the written definition, not the scanner verdict or the catalogue.

| | labelled attributed | labelled not |
|---|---:|---:|
| scanner attributed | 80 | 0 |
| scanner not | 0 | 120 |

Precision 1.00, recall 1.00 (`docs/label-sample.csv`, repository and SHA only). The attributed commits in the
sample are Copilot coding-agent commits, Copilot suggestion/Autofix co-authors and Claude co-author trailers; the
sample has no marker-only commit, so markers are covered by unit tests and the evidence URLs instead. Edge case
noted by the reader: a `Co-authored-by: copilot <[email protected]>` line (an address obfuscated by a web copy)
is not attribution by itself; that commit was attributed through its agent author.

## Bot rule

A maintenance bot is an author whose name ends in `[bot]` and is not an AI-agent account in the catalogue, or a
listed automation identity in `configs/bots.yaml` (4 identities, each with three evidence URLs). Committers are ignored.

## Strata

S1 = 42 model-building infrastructure repositories, S2 = 12 coding-agent harnesses, by the inclusion rule in
`PREREGISTRATION.md` §3; 31 candidates excluded with reasons (`configs/repos.yaml`). Full default-branch history:
733,589 commits in S1 and 148,201 in S2 (REST commit counts, `scripts/count_history.py`).

S3: GitHub repository search over 7 languages × 4 star bands gave 802 eligible candidates after the
static and activity rules. The seeded greedy match (seed 20261028, caliper ±50%) matched all 42 S1 repositories.
Every matched control was then screened by hand on metadata and README (DECISIONS D14); six were screened out
(`configs/s3_screen.yaml`: a playlist, two databases, a specification, two with model fitting at their core) and the
match re-run until all 42 passed. 2 matches are outside the caliper (huggingface/transformers→fastapi/fastapi, ollama/ollama→microsoft/TypeScript) and are dropped in a
pre-registered sensitivity analysis. Full S3 history: 1,968,860 commits.

## Pre-registration

`PREREGISTRATION.md`, frozen at tag `prereg-v1` with SHA-256 hashes of the catalogue, bot list, strata and S3 match.
