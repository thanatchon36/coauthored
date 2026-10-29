# Status

**STOP 2 — partly decided (2026-10-29).** Phases 9–11 done; decisions below.

## Done
- Phase 0 — scoping (2026-10-28): environment, names, skeleton, private repository.
- Phase 1 — instrument and pre-registration (2026-10-29): scanner on three pilot repositories; signature catalogue
  (52 entries, 28 tools, three evidence URLs each); bot list (4); trailer rule validated against
  `git interpret-trailers` (1,565/1,565); blind validation sample of 200 pilot commits (precision 1.00, recall
  1.00); S1 = 42, S2 = 12 by rule; S3 = 42 matched and hand-screened controls; literature review (35 sources);
  `PREREGISTRATION.md` frozen at tag `prereg-v1`. Report: `docs/phase-1-report.md`.
- Phase 2 — scanner: CLI (`scan`, `aggregate`, `report`, `signatures --verify`, `analyze`, `paper`, `dashboard`),
  manifest with head SHAs, timings and sizes; policy classifier; survival classifier.
- Phase 3 — pilot run and snapshot estimate. Report: `docs/phase-3-report.md`. STOP 1 approved 2026-10-29.
- Phase 4 — snapshot of all 96 repositories on 2026-10-28 (UTC): 2.85M commits, 25,561 attributed (all
  history), 632 s, 1.32 GB of clones; aggregates in `data/aggregated/`; policy files fetched and hand-checked;
  Hugging Face dataset built in `dist/hf/` (not pushed). Report: `docs/phase-4-report.md`.
- Phase 5 — survival sample (2,542 PRs inspected, 200 attributed, 184 kept attribution); size sample (2,000
  commits). Report: `docs/phase-5-report.md`.
- Phase 6 — skipped: GH Archive needs BigQuery (`bq`, `gcloud` not installed; not approved). F7 omitted.
- Phase 7 — `coauthored analyze --draws 2000`: `results/numbers.json`, tables, figures F1–F6 and F8,
  byte-reproducible; sensitivity analyses including the GLMM for H3; 8 deviations logged.
  H1 supported (point estimate; CI reaches below 5%), H2–H5 not supported, H6 supported, H7 exploratory positive.
- Phase 8 — `paper/paper.md` → `paper/coauthored.pdf` (8 pages + references and appendix) and
  `docs/site/paper/index.html`; every number filled from `numbers.json`, hand-typed numbers fail the build.
- Phase 9 — adversarial review (`docs/review.md`): 31 findings, each checked and resolved; S1 vs S3 reframed as
  inconclusive, mirror exports added as a leak path, aggregates-only release, survival scoring rule stated,
  deduplicated reverts and H7, post-hoc robustness block; DEVIATIONS 9–13.
- Phase 11 — `announce/`: three LinkedIn drafts, 150-word abstract, figure card (drafts only, not posted).
- Phase 10 (partial) — `REPRODUCE.md`, `RESPONSIBLE_USE.md`, README with results, `coauthored dashboard` and
  `.github/workflows/monthly.yml` (runs only once the repository is public).

## Next — STOP 2 (the author decides)
Decided 2026-10-29: public (history rewritten), aggregates-only Hugging Face dataset, Claude colophon removed from
the web paper, retitled *How Much of the Code That Trains the Models Declares AI Help?* (DEVIATIONS 14),
personal-account repository slugs kept. Open: a release with a Zenodo DOI (also an independent timestamp for
`prereg-v1`), Pages (the monthly workflow is disabled until then), PyPI (not needed: `pip install` works from
the git URL).

## Open issues
- Survival frame excludes PRs landed by merge bots that close instead of merging (pytorch/pytorch), and PRs
  created before 2024-06-01 (`DEVIATIONS.md` 6–7).
