# Status

**Phase 3 — pilot run: done (2026-10-29). Waiting at STOP 1 for approval to take the S1–S3 snapshot.**

## Done
- Phase 0 — scoping (2026-10-28): environment, names, skeleton, private repository.
- Phase 1 — instrument and pre-registration (2026-10-29): scanner on three pilot repositories; signature catalogue
  (52 entries, 28 tools, three evidence URLs each); bot list (4); trailer rule validated against
  `git interpret-trailers` (1,565/1,565); blind validation sample of 200 pilot commits (precision 1.00, recall
  1.00); S1 = 42, S2 = 12 by rule; S3 = 42 matched and hand-screened controls; literature review (35 sources);
  `PREREGISTRATION.md` frozen at tag `prereg-v1`. Report: `docs/phase-1-report.md`.
- Phase 2 — scanner: CLI (`scan`, `aggregate`, `report`, `signatures --verify`), manifest with head SHAs, timings
  and sizes; policy classifier; survival classifier; 60 tests, coverage 95% (CI gate 85%).
- Phase 3 — pilot run: 6,147 commits in 7.4 s; snapshot estimate 2.85M commits, about 2 hours, about 3.5 GB.
  Report: `docs/phase-3-report.md`.

## Next (after STOP 1 approval)
Phase 4: snapshot of all 96 repositories on one day → aggregates → policy files. Phase 5: survival sampler.
Phase 6 (GH Archive) needs the Google Cloud SDK, which is not installed.

## Open issues
- `bq`/`gcloud` not installed: no BigQuery dry-run estimate yet.
