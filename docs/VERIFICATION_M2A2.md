# Module 2A2 verification

Date: 2026-10-04. Module implementation was explicitly authorized. This staged
record now includes a real DEV_LOCKED result below; it is not formal Module 2A2
acceptance. Earlier checkpoint results retain their historical scope.

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

At the intake stopping point, development evidence review was pending, not
DEV_LOCKED or Module 2A2 completion. Its next step was full candidate review and
recording rough opponent card/form/deployment times; do not use contacts as full-playback
evidence, inspect the remaining matches to tune selection, or lower thresholds.
Private source paths, frame labels and hash inventories are not public artifacts.
No push, main merge, PR, release, model work or next module during this intake.

## 2026-10-04 — Human rough review and recording-end conflict

- User confirms full viewing of the available first file, own-bottom perspective,
  and no repeated counting of a persistent unit. Preserved five card/form inventory
  entries with 12 approximate new-deployment times; one form remains unknown.
  User explicitly discloses dense-combat ambiguity/missed plays and does not claim
  an exhaustive deck inventory. These are human observations and location hints,
  not precise verified onset/visibility intervals or key-frame annotations.
- Before precision extraction/selection, inspected original first, sample and
  actual last exported frames. The final frame is still gameplay, not a verified
  ending/result. This contradicts the earlier opening-to-result declaration;
  full viewing of an available file does not certify its recording completeness.
- Fresh read-only existing _scan plus strict load_indexes exited 0: the source's
  measured actual end equals its indexed end and last successful exported frame;
  one report/index pair, 37 requests/successful unique frames. Source SHA-256
  matches the intake value. No new frames extracted or old files changed.
- Added one ignored human-review sidecar preserving the original rough inventory,
  unknown form/dense-combat notes, prior source declarations and the contradictory
  terminal-frame findings. This is not a production development draft/lock. No
  negative intervals, precise occurrences, boxes, target choice or lock fabricated.
- Do not mark a reviewed complete match segment verified or freeze development
  despite this conflict. Retain the rough review; resolving the missing ending
  does not require the user to repeat the same complete-file review/table.
  A complete source for this match, or an explicit documented switch to another
  provisional development match, is the next required input/choice.
- Other three sources remain unseen/unassigned. No third-party vision service,
  detector/model execution, code/dependency change, training, 2B, Model/Test GT
  Lock, Android, realtime, push or main merge. Full pytest/pip/build not rerun for
  this evidence/document-only checkpoint; old results are not fresh proof.
- Final checks: strict sidecar JSON loads with five entries/12 rough deployments,
  one unknown form and no verified negatives or development lock. All four source
  hashes unchanged; all 50 explicitly listed private source/output files ignored;
  no tracked private/generated files or added private-path/hash/secret-pattern
  matches. Only the four intended public Markdown status files changed; diff
  check exited 0. No production/test/dependency file changed.

At that checkpoint: blocked by recording-completeness conflict, not DEV_LOCKED or
MODULE_2A2_READY_FOR_ACCEPTANCE. Private timestamps, source mapping and terminal
image stay local/ignored. This check identifies a visible contradiction; it does
not authenticate provenance or guarantee no unseen edits in the recording.

## 2026-10-04 — Authorized sequential second-recording boundary check

- User explicitly authorized the second item in the unchanged original intake
  array; no re-sorting, card/difficulty/candidate-quality selection or automatic
  continuation to third/fourth. Read-only order/reason audit confirmed the position
  and completeness-based rejection of the first recording, not a quality filter.
- First source, 37-frame preparation, original report/index/contacts, intake and
  five-card/12-time rough review all retained unchanged. A new private disposition
  record marks it "incomplete; does not meet Development Data Freeze conditions",
  never a negative sample. Earlier declarations/review are preserved as history.
- Second only: existing full _scan establishes technical origin/actual last frame;
  existing Module 1 extraction exports six boundary frames successfully. Opening
  shows battle history, replay loading and matchup introduction. The last export
  equals the exact measured file end and still shows ongoing gameplay, no result.
  Thus the second also fails recording completeness; this is not a card-quality or
  recognition judgement. No runtime/model used to choose targets or count plays.
- Because completeness fails, no default full-survey prepare/index/contact pages,
  human full-file card inventory request, precise annotations, negatives, target
  selection or Development Data Lock. Six boundary images are diagnostic outputs,
  not a completed survey or full human review. Third/fourth remain unseen/unassigned.
- Fresh protection check: all 50 explicit pre-switch source/evidence files match
  their before hashes, zero missing/changed, including all four original MP4s.
  Original preparation/intake/rough review files were not rewritten. New boundary,
  hash/check and disposition artifacts are private/ignored, exclusively new.
- No production/test/dependency/storage-format changes, model training/inference,
  2B, Android, live/HUD, source deletion, push or main merge. Full pytest/pip/build
  not rerun for this data/document-only check; earlier tests remain historical.
- Final boundary checks: all six original PNG sizes and PTS-derived timestamps
  match their report entries; strict disposition JSON retains original positions
  and rejects Freeze/negative use for both incomplete recordings. All 61 explicitly
  listed private files are Git-ignored; zero tracked private/generated files or
  added private-path/hash/secret-pattern matches. Exactly four intended Markdown
  files changed; diff check exited 0. Read-only document scope audit found no
  blocking wording issue. No code or full-regression success claim for this check.

At that stopping point: second recording incomplete, not DEV_LOCKED or ready for
Module 2A2 acceptance. Obtain its complete version or an explicit next-item direction;
do not ask the user to annotate this incomplete file or inspect remaining matches
for target selection. All former unknown evidence stays unknown, not negative.

## 2026-10-04 — Authorized ordered third/fourth boundary checks

- New user authority: check original intake position three, then four only if
  three fails completeness; stop at the first confirmed complete recording.
  Read-only order audit confirmed this scope. The original intake array, prior
  dispositions and first rough review remain historical snapshots, not overwritten.
  No re-sorting, inferred natural chronology or card/difficulty/quality filtering.
- Third first: fresh existing full technical scan, six opening/end exports and
  13 supplementary tail exports. The extra tail images check whether crown and
  transition scenes show a final match result; they are not a card survey. Tower
  destruction/own crown scoring and a terminal red/blue transition are observed,
  but no unambiguous final whole-match outcome. Result boundary unconfirmed;
  not Freeze-eligible, not a negative. Searching-for-opponent opening also differs
  from the prior replay declaration; this is an unresolved provenance discrepancy,
  not proof of a replay or permission to rewrite the user's historical statement.
- Fourth was decoded/viewed only after the third's failed result-boundary check.
  Fresh full technical scan and six opening/end exports succeed. Opening has a
  battlefield start; the actual terminal PNG has enemy crown-scoring animation,
  not an unambiguous final whole-match outcome. Result boundary unconfirmed;
  not Freeze-eligible, not a negative. Neither boundary outcome proves that no
  combat was recorded; it fails to establish the required final result boundary.
- No final reward-page requirement added. The protocol's opening-through-result
  rule permits an unambiguous final win/loss/result animation, but not an inferred
  final outcome from one tower destruction, crown increment or screen transition.
  Read-only protocol audit confirmed this distinction; it did not inspect media.
- Fresh mechanical checks: three strictly loaded diagnostic export reports,
  25 successful full-size PNG exports, 24 unique recording/PTS identities because
  the exact third end frame was exported twice. All original PNG dimensions and
  PTS-derived timestamps match their report entries. Terminal export times equal
  each corresponding fresh full scan's actual end. These are diagnostic reports,
  not new prepare/index bundles or full human-review/verified-play evidence.
- All 61 explicit pre-check existing files match their before hashes, zero missing
  or changed, including the four sources, original intake, first survey/rough review
  and second boundary check. New diagnostics, disposition and protection records
  are exclusively created in a fresh ignored run, with no old evidence rewrite.
- NUL-delimited Git path checks confirm all 96 explicit private files ignored and
  zero tracked private/generated media, labels, reports or model weights. This
  avoids Windows text-mode newline ambiguity; private paths/hashes/images remain
  local and out of public documents.
- Final public checks: git diff --check exited 0; exactly the four expected
  Markdown files changed, zero production/test/dependency edits. Added-line
  private-path/source-filename/hash/secret-pattern scan found zero matches.
  Protection and ignore checks were repeated after the documentation update:
  all 61 existing hashes unchanged and all 96 explicit private files ignored.
  Read-only public-document scope review found no blocking wording issue.
- Only four public status/verification Markdown files updated. No production,
  test, extractor, dependency or storage-format change. Full pytest/pip/build
  not rerun for this boundary/document-only task; the infrastructure 385-pass/
  one-skip result is historical, not a fresh result. No model execution, human
  full-file inventory, target, precise labels, Development Lock, 2B, Android,
  live/HUD, source deletion, push, main merge, PR or release.

At that stopping point: all original four checked in the authorized sequence;
no confirmed complete development recording found. Stop; obtain a complete
natural replay through an unambiguous final match result before full review.
All sources, historical review and uncertainty remain preserved, not negatives.
No DEV_LOCKED or Module 2A2 acceptance/completion claim.

## 2026-10-04 — Authorized completion-definition amendment

- The user now explicitly confirms all four recordings cover complete natural
  matches. This supersedes the earlier result-screen-based exclusions, not the
  immutable historical observations or files. A visible victory/defeat/result
  screen is no longer required; the actual final decoded PTS frame is the valid
  evaluable end. Missing result UI alone must not block Development Data Freeze.
- Identity may record the strict paired fields
  `completion_attestation=user_confirmed` and
  `terminal_result_screen_present=false`. Legacy identities remain compatible;
  both new fields are required together and are included in the existing freeze
  digest. False complete/unedited/full-review attestations, incomplete segments,
  corrupt or undecodable files and missing key battle coverage remain blockers.
- Tests first: three new acceptance/lock cases failed on the old closed identity
  shape; 139 focused cases passed. The minimal loader shape extension then passed
  all 142 focused cases. Fresh complete regression: 403 passed, one existing
  Windows permission skip, in 51.33 seconds; exit 0. Fresh pip check exited 0,
  reporting no broken requirements. No extractor, v1 evidence semantics, CLI,
  lock algorithm, dependency or schema-version change.
- Before continuation, all 687 explicitly protected existing files matched their
  hashes: 96 four-recording intake/evidence files plus 591 historical Module 2A1
  files. The first existing report/index strictly reloads with 37 successful unique
  frames. Prior source files, rough review, result-screen findings and exclusion
  records remain unchanged. No new real precise annotations or lock are claimed
  by this rule-only verification.
- Continue from original position one using its existing rough review and survey;
  do not select among recordings by card difficulty. Unknown intervals/forms stay
  unknown, not negatives. Only adequate precise independent deployment evidence
  may produce DEV_LOCKED. No push, main merge, model work or Module 2B authorized.

## 2026-10-04 — First-source real Development Data Lock

- Continued original position one only, without choosing a source by card quality.
  All four user-confirmed sources and prior exclusions remain unchanged. The
  existing 37-frame survey and five-entry/12-time rough inventory were reused;
  no second whole-playback request or model-assisted candidate selection.
- Precise original-PNG inspection exposed rough identity/time mismatches. A
  targeted local-image question received explicit user confirmation: both clear
  opponent deployments are ordinary Minions (three), not Minion Horde (six).
  The original rough review was not rewritten. Frozen selection rationale retains
  the discarded Horde/Cart/Golden Knight hypotheses and why they do not count.
- Four actual candidate bundles: Minions/normal is qualified with two independent
  clear verified deployments and three original key boxes each; Cannon, Flying
  Machine and Witch retain unknown form/ambiguity, no known-form verified plays.
  No fixed card-name priority. Only the corrected target has adequate clear,
  known-form evidence; distinctive group/visibility/occlusion/owner/form rationale
  is explicit. Card groups, not persistent per-frame instances, count as plays.
- Source timeline/boundaries come from measured PTS and strictly loaded indexes,
  not average FPS or game clock. Shared complete capture segment starts at actual
  first PTS and ends at actual last PTS; opening UI stays unknown within capture,
  not a skipped battle prefix. User completion attestation is recorded independently
  of result-screen absence. Onsets are sampled absence/first-appearance brackets,
  not exact input times. Positive visibility windows are conservative reviewed
  subsets; surviving/partially visible units outside them are unknown, not absent.
- Seven real report/index pairs: 191 raw requests, 188 unique successful frames.
  Reused survey contributes 37; new exclusive supplements contribute 154 requests.
  Three overlaps during visibility diagnostics are retained and checked before
  merging. No existing source, PNG, index, export report or human label overwritten.
  Six selected original-key boxes are group rectangles; split-lane boxes include
  intervening space. This is disclosed experimental data, not a detector result.
- Fresh actual candidate CLI: four validates exit 0; four reviews exit 3,
  candidate_gate=false / experiment_gate=false / status=insufficient. Historical
  v1's four-play rule is unchanged and does not veto 2A2's two-play readiness.
  Separate readiness exits 0 / DEV_VALIDATED, freeze-development exits 0 /
  DEV_LOCKED, validate-lock exits 0. Canonical re-creation from the same verified
  disk indexes equals the stored lock; repeated reload yields the same SHA-256.
  Exclusive canonical experiment/type/version-one lock stays local/ignored.
- Three explicit unknown intervals, six recomputed per-candidate coverage gaps,
  zero verified negatives; Witch unknown and dense combat remain uncertainty.
  No automatic evolution/cycle/elixir inference. Equipment, charge, rule version
  and progress remain unknown/null. Evolution capability uses a manually inspected
  current public catalog; missing variants are an inference, not an independently
  authenticated exhaustive rules registry or future guarantee. This limitation is
  in the frozen rationale and private source notes; correction requires new version.
- Fresh historical Module 2A1 read-only regression: four reports, 533 requests,
  402 unique frames; validate/review 0/3, four plays, 12 boxes, eight gaps,
  candidate true, experiment false, insufficient. Only a new ignored review output;
  no historical extraction/playback/label rewrite.
- Fresh final full regression: **403 passed, one existing Windows permission skip
  in 76.06 seconds**, exit 0. Pip check: no broken requirements, exit 0.
  No dependencies or v1 producer/CLI/format changed. Current change consists of
  one compatible identity validator, three test/fixture files and affected public
  documentation; real evidence is private. Build/compile/wheel not rerun in this
  continuation; model accuracy, Android/device, Model/Test GT and live safety
  checks are not run and not claimed.
- Protection recheck: all 687 existing file hashes unchanged, zero missing/changed,
  including four new source recordings and original historical video. Before-hash
  inventory and local attestation/provisional/final bundles are retained. Earlier
  provisional serialization excluded an opening prefix; pre-freeze inspection
  corrected it by creating a separate complete-file bundle, retaining the unfrozen
  provisional file rather than overwriting it. Only the complete-file bundle froze.

- Final fresh-context code/document review approved this narrow continuation,
  with no Critical, Important or Minor finding. The reviewer independently ran
  17 pure regression cases and legacy/new-identity lock compatibility checks;
  did not independently rerun the full suite or certify private media, manual
  labels, hashes, candidate truth, catalog completeness or future model suitability.
  This scoped review does not replace independent ChatGPT module acceptance.
- Final protection scan again matched all 687 protected hashes. The explicit
  existing/new private set contained 899 files, all Git-ignored, zero tracked;
  no tracked media/model/archive/credential binary was found. The new aggregate
  protection report is also checked as ignored separately. Old Module 1/2A1
  producer, loader, CLI, tests and dependency configuration remain unchanged.
- Independent read-only public hygiene audit checked eight affected documents:
  all 23 relative Markdown links exist; added text exposes no private source
  filename, absolute path, SHA-256, account identifier or credential. The two
  apparent private paths in changed tests are synthetic rejection inputs only.
  Final diff check exits 0; local feature commits only, no push or main merge.

Current verified stopping point: **DEV_LOCKED, ready for independent Module 2A2
acceptance**, not formal acceptance. No push, main merge, PR/release, model or test
experiment, Module 2B/3, Android/live/HUD, deletion or old evidence mutation.

## 2026-10-04 — Independent-review completion-boundary repair

- Independent ChatGPT review of `6fa1706d74d4bc68c960ee4e03bac2fc13d6563a`
  found one Important blocker missed by the earlier scoped local review: a
  user-confirmed draft could mark a shortened shared segment complete, leave the
  excluded tail unknown, and still validate/freeze. The prior local review does
  not establish independent acceptance; this fix awaits ChatGPT re-review.
- Minimal adapter-only repair: when completion_attestation=user_confirmed, every
  candidate's sole verified complete shared segment must start at relative zero
  and end exactly at recording.last_frame_seconds. Comparisons use existing
  rational seconds conversion, without tolerance or a result-screen requirement.
  Missing terminal result UI remains legal. Legacy completion identities and
  Module 1/2A1 prepare/validate/review code, tests, formats and gates are untouched.
- TDD reproduction: added synthetic shortened-end (0..19 of a 20-second file)
  and delayed-start (0.25..20) cases retain terminal 19..20 unknown. Both remain
  valid under v1 but must be refused by development readiness, require_development
  and make_development_lock. Before production repair: **2 failed, 1 passed**;
  both failures show the incorrectly accepted valid=True. Added positive test
  freezes 0..last_frame with terminal_result_screen_present=false successfully.
- Fresh focused development/lock/CLI suite: **183 passed in 58.19 seconds**.
  Fresh complete regression: **406 passed, 1 skipped in 76.32 seconds**, exit 0.
  The skip remains the known Windows symlink permission case. Commands actually
  executed with the fixed local environment:

  ```powershell
  .\.venv\Scripts\python.exe -m pytest -q --tb=short
  .\.venv\Scripts\python.exe -m pip check
  git diff --check
  ```

  Pip check reports no broken requirements, exit 0; diff check exits 0.
- Read-only real revalidation strictly reloads all seven existing report/index
  pairs: 191 requests, 188 unique successful frames. The existing shared segment
  already starts at zero and ends exactly at its recording's last actual frame.
  Result screen remains false. Readiness exits 0 / DEV_VALIDATED; validate-lock
  exits 0. Pure canonical lock reconstruction equals the stored version-one lock;
  no freeze command, lock overwrite or new version was necessary.
- Target minions/normal, two independent clear verified deployments, six boxes,
  three explicit unknown intervals and six recomputed coverage gaps are unchanged.
  No unknown interval becomes negative. Stored lock digest and bytes are unchanged;
  no extraction, playback, repeated human review or evidence edit was performed.
- Protection: all **901** existing files match pre-repair SHA-256 hashes, zero
  missing/changed, including the original 687 protected set, all four current
  source recordings, historical source and current private evidence/lock. The
  final explicit privacy scan covers **911** local files including fresh receipts:
  all Git-ignored, none tracked. All **18** baseline Module 1/2A1 offline-tool
  files are unchanged from main. New machine receipts are in a fresh ignored run;
  no private paths, images, labels, hash inventories or generated files are committed.
- Fresh-context read-only scoped repair review found no Critical, Important or
  Minor issue. Reviewer ran 13 targeted cases plus four pure in-memory assertions
  covering legacy compatibility and loaded-lock refusal of both shortened ranges;
  that probe mocked disk reading and did not certify private evidence. The root
  performed the separate real disk lock/index check described above. This local
  review supplements, but does not replace, ChatGPT independent re-review.
- Build/compile, source-video authenticity, model accuracy, Android/live behavior,
  Model/Test GT experiment and independent module acceptance are not rerun or
  claimed. No dependency, database, extractor, lock algorithm or module expansion.
  Repair remains on the original feature branch: local commit only, no push or
  main merge. Stop for independent re-review; Module 2B remains closed.
