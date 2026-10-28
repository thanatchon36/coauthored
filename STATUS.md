# Status

**Phase 7 — analysis: in progress (2026-10-29). Survival and size samples running; final run with B = 2,000
follows.**

## Done
- Phase 0 — scoping (2026-10-28): environment, names, skeleton, private repository.
- Phase 1 — instrument and pre-registration (2026-10-29): scanner on three pilot repositories; signature catalogue
  (52 entries, 28 tools, three evidence URLs each); bot list (4); trailer rule validated against
  `git interpret-trailers` (1,565/1,565); blind validation sample of 200 pilot commits (precision 1.00, recall
  1.00); S1 = 42, S2 = 12 by rule; S3 = 42 matched and hand-screened controls; literature review (35 sources);
  `PREREGISTRATION.md` frozen at tag `prereg-v1`. Report: `docs/phase-1-report.md`.
- Phase 2 — scanner: CLI (`scan`, `aggregate`, `report`, `signatures --verify`, `analyze`), manifest with head
  SHAs, timings and sizes; policy classifier; survival classifier.
- Phase 3 — pilot run and snapshot estimate. Report: `docs/phase-3-report.md`. STOP 1 approved 2026-10-29.
- Phase 4 — snapshot of all 96 repositories on 2026-10-28 (UTC): 2.85M commits, 25,561 attributed (all
  history), 632 s, 1.32 GB of clones; aggregates in `data/aggregated/`; policy files fetched and hand-checked.
  Report: `docs/phase-4-report.md`.
- Phase 7 (partial) — `coauthored analyze` writes `results/numbers.json`, `results/tables/`, `results/figures/`
  (F1–F6, F8) from committed aggregates, byte-reproducibly; sensitivity analyses including the GLMM for H3;
  repository-month-standardised revert rates; deviations logged in `DEVIATIONS.md` (7). 76 tests.

## Running
- Phase 5 survival sampler (`scripts/survival_sample.py`): listing merged PRs of S1 ∪ S2, then up to 4,000 PRs
  until 200 with an attributed head commit. Output `data/survival.csv` → H6, F5.
- RQ6 size sample (`scripts/size_sample.py`): 2,000 commits, `git show --shortstat`. Output
  `data/size_sample.csv` → `results/tables/size.md`.

## Next
Final `coauthored analyze --draws 2000`; Phase 5 report; paper draft (Phase 8); adversarial review (Phase 9);
reproducibility, README and dashboard (Phase 10); announcement drafts (Phase 11). STOP 2 before anything public.

## Open issues
- Phase 6 (GH Archive, F7) needs the Google Cloud SDK (`bq`, `gcloud`), which is not installed, and the user's
  approval of BigQuery costs. Skipped unless the user installs it; F7 is optional.
- Survival frame excludes PRs landed by merge bots that close instead of merging (pytorch/pytorch), and PRs
  created before 2024-06-01 (`DEVIATIONS.md` 6–7).
