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

Real readiness/freezing cannot run without new development footage. Final branch
review will be recorded before the staged handoff. This is infrastructure
verification, not Module 2A2 acceptance or recognition-performance evidence.

## Acceptance boundary

No new natural development recording has been supplied in this task. No actual
Development Data Lock, Model Lock, Test GT Lock or Evaluation Result was created.
Synthetic lock tests are not real experiment evidence. The honest current
experiment status is WAITING_FOR_DEVELOPMENT_MATCH, not DEV_LOCKED.

Match identity, natural provenance, whole-playback completeness, first qualifying
test choice and lack of prediction exposure are human attestations. Digest/linkage
checks do not independently prove them or certify original-video authenticity.
Immutable means exclusive creation by these tools with versioned snapshots;
it is not OS protection against someone editing local files outside the tools.

Not run: new real development review/selection/freeze, model work, independent
test inference, recognition metrics, TypeScript/ESLint and Android builds. Missing
real footage blocks DEV_LOCKED; other checks are outside this Python module.

No push, merge, PR, release, history rewrite or next module is authorized by
this record. Exact local commits and final status belong to Git and the handoff.
