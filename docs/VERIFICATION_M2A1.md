# Module 2A1 — Verification

Original verification: 2026-10-03. **Module 2A1 formally user accepted on
2026-10-04 at `98037ceba81683ad1a2c214bada30a10f2f3f69e`.
Not ready for Module 2B.**

## Formal Acceptance and Integration Authorization — 2026-10-04

The user supplied the formal acceptance verdict for
`98037ceba81683ad1a2c214bada30a10f2f3f69e`
(`fix(evidence): validate report-index consistency`), then explicitly authorized
acceptance recording and integration. Both the 2A1 tool and current-recording
manual evidence are accepted within the disclosed scope; eight unknown intervals
remain unknown. Later sections preserve verification history and do not supersede
this acceptance or expand its scope.

- Accepted evidence aggregates: four reports, 533 requests, 402 unique successful
  frames, four deployments and 12 boxes; validate/review 0/3, candidate_gate true,
  experiment_gate false, status insufficient. These are the previously verified
  local evidence results, not new manual review or a model accuracy result.
- Accepted non-blocking limitations: eight unknown intervals are not negatives;
  one match cannot establish cross-match generalization; report/index consistency
  is not source authenticity or first-source-frame certification; nested advisory
  preparation_report.coverage_gaps validation is deferred and cannot override
  computed gates/gaps; Windows symlink creation is permission-skipped while real
  junction tests have run; ChatGPT reviewed remote code/test design but did not
  independently rerun 223 tests or access private recordings/labels/hashes.
- This integration changes only README.md, CURRENT_STATE.md, DEVELOPMENT_PLAN.md
  and this verification record. No tool, test, dependency, config, schema or private
  evidence changes; no re-extraction or repeat manual playback/annotations.
- Authorization: fresh full regression and dependency checks, one documentation
  acceptance commit, normal feature-branch push, git merge --ff-only into main,
  normal main push, preserve the original feature branch, then stop. No PR,
  release, force push, rebase, branch deletion or subsequent module.
- Before integration, both local/remote implementation refs were the accepted
  SHA; local/remote main was `35653db3f50b756a53aa6a27c7d9de632c808b89` and
  the worktree was clean. Exact documentation commit/integration outcome is
  recorded by Git and the final handoff; authorization alone is not push evidence.

Fresh acceptance checks on the documentation tree before commit/integration:

- `.venv/Scripts/python.exe -m pytest -q --tb=short`: **223 passed, 1 skipped**
  in 59.48 seconds; skip remains Windows symlink-creation permission.
- `.venv/Scripts/python.exe -m pip check`: no broken requirements.
- `git diff --check`: passed. Exact four-document diff, all 29 tracked filenames,
  added-line private-path/secret patterns and local Markdown links checked;
  no unintended tracked data or broken links, no tool/test/dependency changes.
- A separate read-only documentation reviewer confirmed consistent current versus
  historical status, all six accepted limitations, four-file scope and closed
  later-module gates. Reviewer did not rerun tests or access private evidence.

Private-evidence revalidation, source decoding, continuous playback, model training
and Android builds are intentionally not rerun in this documentation-only task.

## Report / Index Repair — 2026-10-04 Current Verification

The initial repair authorization covered only the two tasks in the plan, against
baseline `13330de9967b2c15af64d8b829be7431b6b10181`, with no commit or push.
The acceptance review found that report existence alone did not establish
per-request agreement, and impossible requested times could pass validation.

- Production change is limited to evidence_prepare.py: strictly parse the v1
  export report and check metadata, ordered one-to-one request pairing, safe
  actual PNG paths, rational bases, PTS serialization, result states and timing
  before any duplicate-frame merge. Module 1 pipeline/CLI are unchanged.
- Success uses the existing inclusive 100ms constant. A timeout miss retains its
  candidate PTS/time, an EOF miss has no candidate, and coherent partial/all-miss
  runs remain legal. Error/contradictory runs fail with path-free EvidenceError.
- Float compatibility uses adjacent-float midpoint rounding cells and one common
  possible request satisfying A-Q and the recorded error. No extra millisecond,
  relative isclose tolerance or adjustable report-provided business limit.
- Tests mutate only real encoded synthetic exports in temporary locations.
  Core baseline RED: both index-only and double-file impossible request tests
  failed with DID NOT RAISE. Clean CLI RED: six assertions saw 0/3 instead of 2.
  Refined positive-request 100ms+1us and same-basename/different-file cases also
  failed on baseline, then passed after repair. A zero-denominator report base
  reproduced uncaught ZeroDivisionError and now returns EvidenceError.
- Initial test collection/encoding/time-base fixture mistakes were corrected;
  those failures are not counted as defect evidence. One combined baseline run
  overlapped restoration for CLI subprocesses; only the clean separate CLI run
  is cited as its RED evidence. Existing compatibility tests were already green.
- Before final review, targeted repaired suite: **99 passed, 1 skipped**, full
  regression **220 passed, 1 skipped**. After final fixes, full regression:
  **223 passed, 1 skipped**. pip check: no broken requirements; diff check passed.
  Final targeted suite after the review fix: **102 passed, 1 skipped**.
  Real Windows junction tests run; symlink creation remains permission-skipped.
- Existing local input recheck: **4 reports, 533 original request records,
  402 unique successful frames after merge**. Actual subprocess validate/review
  exits **0 / 3**. Four verified deployments, 12 key boxes, candidate_gate true,
  experiment_gate false, status insufficient and eight unknown gaps unchanged.
- Pre/post hashes of **591 explicitly referenced existing files** match,
  including source MP4, original PNGs/contact pages, indexes/export reports,
  manual evidence/notes and prior review reports. A new ignored review report was
  created without overwriting old outputs. No prepare/re-extraction/manual
  playback or annotation edit occurred. File identities and hashes remain local.

Repair verification is separate from user acceptance of Module 2A1. The unknown
coverage and one-match insufficiency do not change. This consistency check is not
source-video authenticity certification: without re-decoding it cannot establish
that both files were never coherently forged, or that a chosen frame was the
first source frame at/after the request. No anti-tampering system was added.

One independent fresh-context read-only repair reviewer checked the working diff
against the fixed baseline and independently ran the targeted suite. No Critical
or new Minor findings; one Important cross-request inconsistency was reproduced:
increasing requests could return decreasing candidate PTS. Executor ruled this
within temporal-consistency scope, not source authenticity. One fix pass added
three RED/GREEN regressions for backwards success, backwards timeout misses and
skipping an already-known eligible candidate. Full post-fix suite: 223 passed,
one permission skip. No second reviewer claimed. Real evidence recheck and all
591 original-file hashes repeated after the fix; results unchanged. Reviewer did
not access private footage/labels/hashes, independently redo whole-video review,
or rerun full tests/dependencies/historical RED; those remain executor evidence.

Execution rulings: use the specified feature checkout without a new worktree;
retain ignored ledger/uncommitted review rather than commit-based cleanup; one
narrow 30Hz fixture supports an exact 1/30s source clock absent in the millisecond
fixture. Costs are less checkout isolation, retained local scratch and a small
extra test fixture. Source authenticity stays unproven and stored advisory gap
nested validation remains explicitly deferred. Module acceptance/integration is
still the user's decision; no review verdict supplies that authorization.

Final hygiene: all 595 checked project-local original/generated artifacts ignored
by Git (the 591-file hash set also contains the external source MP4). Targeted
private identifier/secret diff scan: zero matches. Exactly five tracked files
modified: loader, its two test files and the two state/verification documents;
none added/deleted. Development plan has no conflicting state to change.
Not run: continuous video playback/re-annotation, source re-decoding, Android
build, model training/accuracy and subsequent modules (intentionally out of scope).

At the repair handoff, changes were uncommitted and unpushed on the existing
feature branch. Subsequent publication authorization and fresh checks follow;
no main merge, PR, next module, dependency/database/migration or Android change.

## Final Publication Verification — 2026-10-04

The user subsequently authorized checking the existing repair, final validation,
committing exactly its five tracked files and a normal push of the existing
feature branch. Baseline HEAD and branch were verified as `13330de9967b2c15af64d8b829be7431b6b10181`
and `feat/module-2a1-current-recording-evidence`. No production/test change was
needed during publication; only these two documents synchronize authorization
and fresh verification. Exact commit SHA and push outcome belong to Git and the
final handoff; permission alone does not establish either outcome.

- Fresh full suite: **223 passed, 1 skipped** (25.16 seconds). The skip is Windows
  symlink-creation permission; real Windows junction tests passed. Fresh pip check
  reported no broken requirements; git diff --check passed.
- Read-only loading of all **4 reports / 533 original requests** produced **402
  unique successful frames**. Actual validate/review subprocesses exited **0 / 3**.
  candidate_gate **true**, experiment_gate **false**, status **insufficient**.
- **Four deployments, 12 key boxes and eight unknown intervals** unchanged;
  computed counts, gates, status and the full gap list matched the previous repair
  report. No manual playback, annotation changes, extraction or source decoding.
- All **591 existing-file hashes** matched before and after, including the original
  MP4. All **596 checked project-local artifacts** are Git-ignored: 590 protected
  project files, five existing repair artifacts and one new exclusive review
  report. The external MP4 is the remaining protected file, outside the checkout.
  The new report did not overwrite any old report; private paths/hashes stay local.
- Exactly five tracked files were modified: the loader, its two test files and
  these two documents. No tracked private recordings, PNGs, actual index/report/
  annotation JSON, hash manifests, models or unrelated generated files.
- No dependency/storage/schema/configuration change, PR, release, main merge,
  Module 2A2, Module 2B, Module 3, Android implementation or training. Formal
  Module 2A1 acceptance remains pending independent user review; one-match
  insufficiency, unknown intervals and source-authenticity limits remain intact.

## Task 4 Continuation — Fresh Evidence

The user completed whole-recording playback and supplied opening/result
completeness, no edits/skips/speed changes, own-bottom perspective and four new
opponent normal Inferno Dragon deployment leads. Executor did not watch continuous
playback: original static exports were inspected for absence/birth/motion,
visibility endpoints, ownership markers, variant appearance and boundaries.
Rough player times were refined using actual exported PTS, not game countdown.

- Three new local fine-extraction runs: success, all 477 targets exported.
- Four distinct verified opponent deployments; three distinct original key-frame
  boxes each, 12 total. No repeated PNG counted as a second deployment.
- Source hash rechecked against original preparation: unchanged.
- Real validate exit **0**; real review exit **3**, status **insufficient**,
  candidate_gate **true**, experiment_gate **false**. One reviewed complete segment.
- Eight timeline gaps explicitly reported. Broad battlefield absences were not
  inferred from sparse samples or from the rough deployment form. Reviewed
  selection/result/transition/system negatives include the exact terminal frame.
- Birth flashes, poison/countdown text and overlapping units were recorded as
  limitations. Onset brackets are supported visible-onset estimates, not hidden
  card-tap times. Disappearance endpoints are first confidently absent inspected
  samples; residual uncertainty remains, especially one heavily obscured end.
- Fine original-frame inspection corrected a rough loading-screen boundary.
  Capture completeness is supported by user playback plus original opening/result
  samples; it is not an independent codec-integrity guarantee.
- Fresh pre-work contract/review regressions: **74 passed**. Fresh full regression:
  **145 passed, 1 skipped**; pip check: no broken requirements. Symlink permission
  skip unchanged. No code/test/config/dependency changes in this continuation.

All precise times, boxes, source identifiers, user notes, original PNGs, indexes
and evidence/report JSON remain in ignored local outputs. This finishes the
lightweight current-recording stage with disclosed gaps, not complete temporal
ground truth for model scoring. Further interval review, independent match data
and separately approved 2A2 remain prerequisites for 2B. No second recording,
training, live feature or implementation merge was performed.

The sections below preserve the earlier partial verification and review history.

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
- Task 4: earlier partial verification/documentation, completed by the continuation
  above; no additional tool implementation.

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

## Earlier Blocking Acceptance Item — Resolved by User Playback

At the earlier stopping point, available tools provided static images, not full
continuous local video playback to the executor. Contact pages do not substitute
for watching the complete match. Playback/deployment review and key boxes had not
been performed, so Task 4 could not then be marked complete. The user's subsequent
whole-playback review resolved that blocker; current scope and remaining coverage
limitations are stated in the continuation above. No second recording was required.

This distinction remains separate from the correct one-recording **insufficient
for 2B** result. 2A2 / 2B / Module 3 / Android / live assistance were not entered.

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

Earlier Not Run: full continuous playback/manual card annotations (then a blocker),
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

At the earlier implementation handoff, authorization covered feature push only,
not integration. The missing user playback evidence was subsequently supplied;
original-frame annotations and actual CLI checks are reported above. The later
formal acceptance and separate ff-only integration authorization at the top now
supersede that former authorization state; no next module is approved.
