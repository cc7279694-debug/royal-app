# Module 2A1 — Partial Verification

Date: 2026-10-03. **In progress, not Module 2A1 complete.**

## Authorization and Git

The user approved planning commit 35653db. The clean original main e30ca01
was verified against origin, planning ancestry and documentation scope checked,
47 baseline tests rerun successfully, then planning fast-forwarded and pushed
to main. Planning branch retained. Implementation starts from 35653db on
feat/module-2a1-current-recording-evidence; never merged back into main.

Task commits:

- Task 1: 53f772d — strict simplified evidence contract and synthetic fixtures.
- Task 2: 59462f4 — safe local preparation, index/contact pages and CLI.
- Task 3: f0c43e1 — box helpers, interval review, gaps/counts/insufficiency.
- Task 4: partial verification/documentation; not a completed task.

## Implementation and Test-First Evidence

New code: evidence_contract.py (strict JSON/structural/PTS/reference validation),
evidence_prepare.py (source integrity, exact default sampling, ignored exclusive
outputs, stable identities, checked index/image references and contacts),
evidence_review.py (manual full-image box helpers and conservative review),
evidence_cli.py (prepare/validate/review only).
New tests: evidence_fixtures.py, test_evidence_contract.py,
test_evidence_prepare.py, test_evidence_review.py, test_evidence_cli.py.
No source change to Module 1 pipeline or CLI, dependency installation,
configuration/database/migration/app stack change, third-party data or model.

- Task 1 RED: expected missing contract module after fixing a test syntax typo.
  GREEN: 42 tests; full regression 89 passed.
- Task 2 RED: expected missing preparation module. GREEN: 17 passed, one skipped;
  full regression 106 passed, one skipped.
- Task 3 RED: expected missing review module. GREEN: 29 passed;
  full regression 132 passed, one skipped.
- Task 4 pre-work regressions: 67 passed. These already implemented behaviors
  did not fail; no fabricated RED claim for documentation/manual work.
- Synthetic contact preview actually opened: full original aspect and PTS label.
- Symlink test skipped because Windows denied creating a symlink. This is not
  claimed as a passing real symlink-permission test.

## Current Recording — Mechanical Verification Only

Read only the exact original recording previously supplied by the user; no
private-directory search, source copy, upload or other recording processing.
There was no local_data/recordings directory despite the attachment's expectation;
the explicitly provided original remained available and was used directly.

- prepare exit **0**, source SHA before/after unchanged (value stays private).
- Original PNGs/index/contact pages created only in a new Git-ignored run.
- validate exit **0** for structurally valid **unreviewed** six-entity evidence.
- review exit **3**, status **insufficient**, experiment_gate **false**.
- candidate_gate **false**: zero verified deployments/key boxes; this is not
  evidence that the candidate card is absent or that four preliminary appearances
  were disproved. Inferno Dragon remains pending review.
- Unknown timeline is reported as gaps; no inferred negatives, match boundaries,
  variant/owner or deployment claims were inserted.
- CLI tests used real encoded synthetic MP4s, including prepare/validate/review
  exit 0/0/3 for valid synthetic evidence; unsupported freeze rejected.
- PNGs, indexes, actual JSON/reports and contacts confirmed ignored by Git.

## Blocking Acceptance Item

Available inspection tools provide static images, not full continuous local
video playback to the executor. Contact pages do not substitute for watching the
complete match. Full playback, all candidate ownership/variant/absence/spawn/
visibility review, complete positive/negative intervals and reviewed key boxes
have **not been performed**. Consequently Task 4 and Module 2A1 cannot be marked
complete. An available local playback/manual reviewer must supply this evidence
before acceptance. No second recording is required to finish 2A1.

This distinction is separate from the correct one-recording **insufficient for
2B** result. 2A2 / 2B / Module 3 / Android / live assistance were not entered.

## Final Checks and Independent Review

Actual final commands:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --tb=short
.\.venv\Scripts\python.exe -m pip check
git diff --check
```

Results: **145 passed, 1 skipped**; no broken requirements; whitespace checks
passed. Windows junction creation and ancestor-escape regression actually passed.
The separate symlink-creation test remains skipped due OS permission.
README three-command behavior tested against synthetic encoded MP4s and current
unreviewed recording evidence. Relative documentation links and targeted private
identifier/secret scans passed. Tracked media/model/actual annotation JSON scan
empty; Module 1 pipeline/CLI and requirements/config unchanged. Local final report
and ledger ignored. Original hash rechecked against pre-preparation value after
fixes; still unchanged. Real validate/review repeated: **0 / 3**.

One independent fresh-context reviewer examined the complete branch range
35653db..e4e7013 plus spec/plan/ledger. No private media was opened by reviewer.
No Critical findings. Three Important findings were reproduced with failing tests
and fixed in one RED/GREEN pass:

1. Malformed status/oversized numbers could crash validators/CLI. Direct and
   subprocess tests reproduced TypeError/OverflowError; now path-free rejection.
   Numeric-exponent overflow is also rejected by the strict JSON loader.
2. Valid right/bottom pixel-edge boxes could normalize outside the strict decimal
   contract. Exact pixel bounds and conservative one-ULP representation fixed it.
   A skinny fractional boundary also exposed an iterative-rounding timeout during
   this same fix pass; conversion is now bounded and the regression passes.
3. Duplicate-image content hashes ignored alpha. A same-RGB/different-alpha
   regression failed first; canonical RGBA comparison now detects the conflict.

Deferred Minor: stored advisory preparation_report.coverage_gaps validates the
list but not every nested gap object's fields. It cannot override recomputed
counts, gates or gaps; stricter nested advisory validation remains a known debt.
No second reviewer or independently certified actual footage is claimed.

Not Run: full continuous playback/manual card annotations (acceptance blocker),
TypeScript/ESLint (Python experiment only), Android build/device test, recognition
accuracy, external data/model evaluation, 2A2 splits/freeze and 2B (out of scope).

## Implementation Rulings and Costs

- Current explicit approval supersedes old document-only handoff; only 2A1
  executed. Cost if mistaken: unwanted scope; direct authorization is on record.
- Keep this plan's ignored ledger rather than deleting scratch/user files.
  Cost: small local scratch retained for the unfinished task.
- Four contact thumbnails at three columns need two rows; corrected the test's
  height expectation, not implementation. Cost: preview assertion only.
- Merge same frame across requests/runs/filenames only with agreeing PTS/base,
  dimensions/time and full pixel content; retain checked aliases. Cost: aliases
  remain trusted only after supplied-run integrity checks.
- Human evidence may set perspective while measured index stays unknown.
  Cost: perspective requires actual manual review, never software inference.
- Uncovered last actual timestamp is a singleton gap, not a closed positive.
  Cost: clients must retain zero-duration endpoint gaps.
- Task 4 pre-work regressions were already green; no invented RED for manual/doc
  steps. Cost: no separate failing test for a non-production step.
- Use only the explicitly supplied original when expected checkout recording
  directory was absent. Cost: none to original; no search/copy performed.
- Treat exponent overflow as part of Important malformed/nonfinite handling.
  Cost: invalid numeric data are rejected earlier.
- Represent valid exact ratios with at most one adjacent inward float when
  needed; never clip invalid pixels. Cost: at most one-ULP representation change.
- Reviewer excluded actual identity/owner/variant/count/interval/boxes/full-match
  eligibility; they remain unverified. Cost: Task 4/module cannot be accepted.
- Reviewer did not independently rerun source integrity/real CLI; executor
  repeated these after fixes. Cost: one source-specific verifier.
- Reviewer excluded OS link probes; native junction test added, symlink permission
  skip retained. Cost: real symlink creation still not certified here.
- Reviewer excluded model/data/split/Android/live/ban and module acceptance
  guarantees. Cost: future gates and current partial status remain unchanged.

Implementation branch is authorized for push only; no PR, implementation merge,
branch deletion or release. Full-playback evidence must be supplied by an
available local manual reviewer before completing Task 4.
