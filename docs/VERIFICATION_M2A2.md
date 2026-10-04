# Module 2A2 verification

Date: 2026-10-04. Module implementation was explicitly authorized. This is a
staged verification record, not final Module 2A2 acceptance or DEV_LOCKED.

## Baseline

- Clean local and fetched remote main matched
  `3ad657f2c9190f4e389ccd035682becd12d0c51c`.
- Branch: `feat/module-2a2-experiment-lock`; user chose the existing checkout.
- Fresh `./.venv/Scripts/python.exe -m pytest -q --tb=short`: 223 passed,
  1 skipped (Windows symlink creation permission); exit 0.
- Fresh `./.venv/Scripts/python.exe -m pip check`: no broken requirements;
  exit 0. No dependency installation or upgrade.
- Existing real evidence: 4 report/index pairs, 533 raw requests, 402 unique
  successful frames; CLI validate 0 / review 3. Four verified deployments,
  12 key-frame boxes, eight gaps; candidate true, experiment false, insufficient.
- All 591 explicitly referenced existing files matched their previous hashes,
  including the source MP4. The detailed hash inventory remains private/ignored.
- Only a new ignored baseline review report was generated. No new extraction,
  media playback, manual labels or changes to old evidence.

## Authorized implementation boundary

Separate experiment schemas, development readiness, immutable versioned locks,
Model Lock and later Test GT contracts, blind-test protocol and synthetic tests.
Existing Module 1 and 2A1 production code/CLI remain unchanged. No model training,
inference, automatic selection, automatic evolution/cycle/elixir, database,
Android, HUD, live game access, runtime network request or external asset import.

## Implementation and final verification

### Task 1 — development contract/readiness

- Synthetic draft tests failed before production existed, then passed with the
  strict schema and reused v1 validation. Added boundary/coexisting-unit cases.
- Fresh task review identified two blocking inconsistencies: evolved with
  not_equipped, and malformed bool/numeric snapshot fields accepted by equality.
  Behavioral tests reproduced one form case and 13 snapshot-type cases before
  the narrow fix. Scoped re-review closed both findings with no new blocker.
- Latest focused run: 54 passed. Early full run before later additions:
  258 passed, one known skip; this is not the final module count.
- Local commits: `eeda95f`, `4e22465`; no existing v1 production/tests changed.

### Task 2 — versioned lock chain

- Synthetic lock tests failed before implementation, then passed. Traversal and
  a real Windows junction reproduced unsafe early path normalization (two RED
  cases), then passed with pre-normalization safe_path checks.
- Two tests reproduced nonzero sampling skipping the recording prefix before
  the protocol-v1 zero-origin fix; latest focused run: 61 passed.
- Root full run before those last two tests: 336 passed, one known skip.
  Final full regression will include all additions, not reuse that count.
- Fresh task review passed: no Critical/Important issues. Deferred Minor:
  repeated frame/bbox annotations within one GT play under different IDs are
  accepted. Future metrics must reject/deduplicate them; no current GT box-count
  threshold or score depends on this count.
- Local commit: `4de9d55`; pure future Model/GT contracts, not model execution.

### Task 3 and final checks

- Added separate experiment_cli.py and 38 subprocess integration cases using
  real encoded anonymous MP4/report/index/PNG inputs. Tests were written first:
  RED 38 failures (missing CLI, fixtures succeeded), then GREEN 38 passed.
- Four commands: readiness, freeze-development, validate-lock, freeze-test-gt.
  Strict disk binding precedes freeze; GT's declared snapshot is compared to
  actual loaded files, never silently rewritten. Public output is status only.
- Local code commit: `52f74d8`. Fresh Task 3 review passed with no issues;
  final whole-branch review is pending.
- Controller fresh full `./.venv/Scripts/python.exe -m pytest -q --tb=short`:
  **376 passed, 1 skipped in 78.47s**; exit 0. The skip remains the Windows
  symlink creation permission test; real junction tests passed. No test removed.
- Fresh pip check: no broken requirements, exit 0. compileall: exit 0.
- Local wheel build with --no-index --no-deps --no-build-isolation: exit 0;
  generated package stays ignored. No download/installation or dependency change.
- Working/staged diff checks: exit 0; no staged media/private JSON/weights or
  secret-pattern matches. All nine Python additions are new files; existing
  Module 1/2A1 production, tests and dependency blobs are unchanged from main.
- Read-only real regression: 4 report/index pairs, 533 requests, 402 unique
  successful frames; validate exit 0, review exit 3; four deployments, 12 boxes,
  eight gaps; candidate_gate=true, experiment_gate=false, status=insufficient.
  Only new ignored machine review reports are written. No extraction, playback,
  new manual review, re-labeling or evidence rewrite.

- After the full run, all 591 existing protected files matched their earlier
  hashes (zero changes), including the original external MP4. All 590 protected
  files inside the checkout were confirmed Git-ignored; one original MP4 stays
  outside the repository. No tracked media, private JSON, weights or secrets.
- README/state/protocol/contract/plan cross-links checked: no missing relative
  targets. The detailed protected hash inventory remains ignored and private.

### Final branch review and gate correction

The fresh whole-branch review at `3ad657f..9cabd10` found one Important issue:
the new adapter accepted any complete segment and counted clear verified plays
across disjoint or incomplete segments. An in-memory two-segment fixture reached
DEV_VALIDATED and a development lock. This is a detectable structural conflict,
not a request to authenticate source footage or human declarations.

A narrow two-file new-adapter/test fix now requires one complete reviewed shared
segment per candidate bundle, consistent identity/bounds/metadata across
candidates and qualifying deployments bound to it. The original v1 validator,
extractor and old CLI are untouched. Local code commit: `beda5b8`.

- Nine new regression cases: two cross-segment/incomplete variants, five
  cross-candidate metadata conflicts, valid shared-match lock compatibility,
  and empty valid-but-NOT_READY compatibility.
- Every malformed fixture first passes unchanged v1 validation, then must be
  refused by development readiness, require_development and lock construction.
- TDD RED: 7 failed / 56 passed, then GREEN: 63 passed. Controller focused run:
  63 passed in 0.89s; exit 0.
- Latest controller full run: **385 passed, 1 skipped in 77.14s**, exit 0.
  This supersedes the earlier 376-pass full run as final regression evidence.
- Fresh pip check and rebuilt no-index wheel: exit 0. No dependency change.
- Fresh scoped re-review: finding ADDRESSED; no new breakage, Critical/Important
  issue or out-of-scope observation. No new full-branch review loop or feature
  expansion. All blocking findings from the whole-branch review are closed.
- Post-fix old CLI validate/review repeated: exit 0/3. All 591 protected hashes
  checked again after the 385-pass regression; zero changes, original MP4 intact.
  Compile/diff checks passed. No extraction, playback or annotation changes.

At the infrastructure checkpoint, real readiness/freezing could not run without
new development footage. This is
infrastructure verification, not Module 2A2 acceptance or recognition-performance
evidence. The 376-pass run above precedes this final gate correction.

## Changed file inventory and storage

Nine new Python files under tools/offline_video/:

- src/clash_tracker_video/experiment_contract.py
- src/clash_tracker_video/experiment_development.py
- src/clash_tracker_video/experiment_lock.py
- src/clash_tracker_video/experiment_cli.py
- tests/experiment_fixtures.py
- tests/lock_fixtures.py
- tests/test_experiment_development.py
- tests/test_experiment_lock.py
- tests/test_experiment_cli.py

Four new public documents: MODULE_2A2_BLIND_TEST_PROTOCOL.md,
MODULE_2A2_CONTRACTS.md, VERIFICATION_M2A2.md and
superpowers/plans/2026-10-04-module-2a2-experiment-lock.md, all under docs/.
Four updated documents: README.md, docs/CURRENT_STATE.md, docs/DECISIONS.md,
docs/DEVELOPMENT_PLAN.md. No files deleted or old Python/dependency files modified.

Storage: separate versioned local JSON contracts/locks in ignored outputs/ or
local_data/, exclusively created. No SQLite, migration, repository storage,
backup format, dependency or original annotation format change. Synthetic media,
locks, build files and detailed review artifacts remain ignored and are not real
experiment evidence. All public documents contain only aggregate private results.

## Infrastructure checkpoint (before recording intake)

Infrastructure is implemented and verified, with final blocking review findings
closed; Module 2A2 itself was not accepted or complete. At this checkpoint,
new complete natural development footage was still awaited. No actual
development selection/freeze, Model Lock, Test GT or Evaluation Result exists.
The prepare handoff command and recording instructions are in README.md.

All changes are focused local feature commits. Main and its remote remain at
the baseline, the original 2A1 branch is preserved, and no 2A2 branch is pushed.
No PR, merge, release, history rewrite, next module or model work occurred.
Final commit SHA is reported from Git in the handoff, not self-referenced here.

## Infrastructure acceptance boundary

No new natural development recording had been supplied at that checkpoint. No actual
Development Data Lock, Model Lock, Test GT Lock or Evaluation Result was created.
Synthetic lock tests are not real experiment evidence. The checkpoint's
experiment status is WAITING_FOR_DEVELOPMENT_MATCH, not DEV_LOCKED.

Match identity, natural provenance, whole-playback completeness, first qualifying
test choice and lack of prediction exposure are human attestations. Digest/linkage
checks do not independently prove them or certify original-video authenticity.
Immutable means exclusive creation by these tools with versioned snapshots;
it is not OS protection against someone editing local files outside the tools.

Not run at that checkpoint: new real development review/selection/freeze, model
work, independent test inference, recognition metrics, TypeScript/ESLint and
Android builds. Missing real footage blocked DEV_LOCKED; other checks are outside
this Python module.

No push, merge, PR, release, history rewrite or next module is authorized by
this record. Exact local commits and final status belong to Git and the handoff.

## 2026-10-04 — Recording intake / first development survey

- Four local MP4s received. User confirms four distinct new natural matches,
  opening-to-result complete normal-speed unedited replays, excluding the old
  Inferno Dragon match. These are human attestations, not machine proof or a
  completed full human evidence review.
- All four were checked for metadata and SHA-256 only before selection. All are
  H.264, 432x960, approximately 24 FPS. Distinct byte hashes do not prove distinct
  underlying matches. Original filenames/mappings and hashes remain private.
- Filename order selected the first provisional development candidate before
  any pixel exposure; no card/difficulty/model-based filtering. Existing unchanged
  prepare exited 0. Its one report/index pair and PNGs were loaded and checked:
  37 raw requests, 37 unique successful frames, four contact pages, success.
- All four source hashes still match the intake values. No source rename, move,
  overwrite, old evidence edit or re-labeling. New intake/preparation/check files
  are in fresh ignored output directories; sources are ignored too.
- The other three were not decoded or viewed and remain unassigned. They are not
  a selected/qualified independent test set; no future first-qualifying-test or
  natural chronology claim is inferred from filenames.
- Full human playback review, opponent inventory/forms, independent deployments,
  target selection, precise annotations and real Development Lock remain pending.
  Source declarations and locator frames do not establish full_human_review=true.
  No Model Lock, Test GT Lock, Evaluation Result, model execution or 2B work.
- This intake changes only generated private outputs and four public status/
  verification documents. No production/test code, dependency or storage-format
  change. Full pytest/pip/build were not rerun for this recording/document-only
  update; the preceding 385-pass/one-skip result remains historical infrastructure
  verification, not a fresh intake test result.
- Final intake checks: all four source hashes unchanged; all 49 explicitly listed
  source/generated files ignored; zero tracked private/generated files or added
  private-path/hash/secret-pattern matches. Only the four expected Markdown files
  changed; diff check exited 0. Read-only public-document scope review found no
  blocking wording issue. No full regression result is claimed for this intake.

Current stopping point: development evidence review pending, not DEV_LOCKED or
Module 2A2 completion. Next, review only the prepared candidate in full and record
rough opponent card/form/deployment times; do not use contacts as full-playback
evidence, inspect the remaining matches to tune selection, or lower thresholds.
Private source paths, frame labels and hash inventories are not public artifacts.
No push, main merge, PR, release, model work or next module during this intake.
