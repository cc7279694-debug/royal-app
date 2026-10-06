# Module 2B-2 Data Preparation — Verification Checkpoint

Historical checkpoint date: 2026-10-05. Status at that checkpoint:
**Waiting for human evidence resolution, not accepted or dataset-locked**.
Scope: the former user-approved specialist data-only slice, now paused and
superseded as a product route; its evidence and original validator behavior remain.
Accepted main baseline: `8a03e288fb814d81b0a8e255b8004dbc4d0efb02`.
Branch: `codex/module-2b2-data-preparation`; local only, no push/main integration.

Completed 2026-10-06 data authorization is the separate private local **2-Class
Training Dataset Lock v1** preparation/verification on the two-class smoke route in
[Module 2B-2B verification](VERIFICATION_M2B2B.md). This document retains the
old specialist checkpoint and target-recheck results as **superseded / historical**.
The old four-match/eight-play shortfall is not a current task or a smoke-lock
precondition; no old result, source, pending revision or lock is overwritten.
The current separate Phase C authority is described in
[the fixed smoke protocol](PHASE_C_SMOKE_PROTOCOL.md); this document does not
restore the obsolete specialist route or provide a training gate.

## Verified task gates

- Baseline maintained suite: 474 passed / 1 Windows symlink skip; pip check passed.
- Task 1 contract: 68 focused tests; 542 full passed / 1 skip after the independent
  review's Important absence-conflict repair. Fresh fix review approved.
  Commits `2a49414208d9778647c6b2828bf91bb5705416e8` and
  `1c69f1c87b5bad6f7c02d9059521a179785c9bf7`.
- Task 2 bindings/lock: 583 full passed / 2 Windows symlink-privilege skips;
  pip/syntax/diff checks passed. Separate review approved with no findings.
  Commit `047dc1bba380af3a6f75da4f73c12c012b72ed43`.
- Actual Windows junction checks run. A skipped symlink test is not junction proof.

The explicit maintained-suite command is:

```powershell
.\.venv\Scripts\python.exe -m pytest tools/offline_video/tests -q --tb=short -rs
.\.venv\Scripts\python.exe -m pip check
git diff --check
```

Bare root collection includes ignored old Review Packet test copies; it is not
the verification command and was not made green by deleting or changing tests.
All baseline production/test/config files remain unchanged.

## Task 3 window verification — passed, with runtime limitations

Geometry and additive paired saves are covered with synthetic evidence only.
The first focused 43/1 and full 626/3 runs used an overbroad discarded TclError
skip; the added GUI skip is **not** accepted as environment-unavailability proof.
After narrowing the skip classifier, focused 47 passed, but the full run produced
**629 passed / 2 skipped / 1 error**, exit 1. The real Tk constructor failed
loading the installed scrollbar runtime before the annotator was constructed.
The files exist/read correctly; bare roots and a retained-object probe pass.
The native-loader cause is unknown; no install, runtime repair or wider skip.
An exact predecessor-pair diagnostic output was not captured and is not evidence.

The test harness now uses one fresh process per actual application lifecycle,
the same Python/environment/cwd and original real Tk/Pillow assertions. Captured
initialization/callback errors, timeout/nonzero exit and any GUI skip fail; no
retry or dummy GUI. Focused result: **52 passed, no skips**. This is test isolation,
not proof that the native runtime was fixed or shared-interpreter launches work.
Final maintained regression: **635 passed / 2 known Windows symlink skips in
428.71s**, exit 0; no GUI skip/error/failure. Dependencies/syntax/diff passed.
Task 3 commit: `c5aa3b0efde50d4b9adb150f0a640478ffbda49b`, exactly the two new
annotation Python files and contract section. Protection is complete: all 16,745
original files unchanged; 20,790 private files ignored, none tracked; baseline
source/test/config unchanged. Independent Task 3 review requires a local fix:
invalid false-complete state could advance in the forward-only UI and strand
later saves. A callback-error test also needs a valid passing report to prove
trace-specific rejection. Local fix `6f34af3018f1caa6aeea17ee21589d0322ef8c57`
adds validation before advancement, keeping valid pending navigation. Covering
tests: 7 passed after 3 named RED failures; focused: 55 passed, zero skips; full:
**638 passed / 2 known Windows skips in 318.69s**, exit 0. A valid passing JUnit
report plus callback trace now proves the trace guard (deliberate guard removal
caused RED, then was restored). Dependencies/syntax/diff/privacy passed. Scoped
fix-review: both findings addressed, no new breakage. Post-fix protection:
16,745 original files unchanged; all 21,463 current private files ignored,
none tracked; legacy sources/tests/config unchanged. Original failed-run evidence
remains a disclosed limitation.
Human visible-window manual acceptance: **Not Run**; native UI controls are not
available to this task. Programmatic real-window smoke is not human review.

## Private evidence and actual data status

The explicit initial protection snapshot covers **16,745 existing files**, with
the previous 10,376 closing-protection files also checked. An earlier diagnostic
recheck: all 16,745 byte-identical; 20,117 current private files ignored, none
tracked; accepted legacy source/test/config unchanged; diff check exit 0.
Detailed paths, media hashes, protection manifests and test output remain only
in ignored local receipts, not this public document.

Metadata inventory preserves four sources in original intake order. User already
attested independent natural complete unedited replays; absent result UI is legal
with the exact 0..actual-last-frame boundary. That does not certify target cards
or unit labels. Historical manual confirmation supplies one match/two ordinary
Minions plays and six old group-box images; those images are not per-unit labels.
The other three sources remain pending target review, not certified no-target.
No real new per-unit annotation or Training Dataset Lock has been generated.
No actual data-readiness success, detector accuracy or FP/min claim is made.

## Inherited boundaries and handoff

Unknown/other-form content never becomes negative; sparse absent frames never
replace reviewed absent duration. Actual source authenticity, match/event human
independence and exhaustive labelling are not proved by schema/digest checks.
Old Development Lock, group labels, private sources and accepted 2B-1 FAIL stay
unchanged. No 2B-1 tuning/rerun, torch/torchvision install, weights, training,
recognizer inference, Model Lock, blind-test data, Module 3, Android or HUD.

Task 3 verification/review gate passed. Task 4a CLI is committed at
`a62bb721f3e15dea0af58c997d520f1cb66ab8bd`: 34 focused passed in 123.13s, plus one
strengthened post-write case passed separately. Pip/syntax/diff/privacy/protection
passed; 16,745 originals unchanged, 21,473 private files ignored, none tracked.
Independent scoped CLI review approved, no Critical/Important findings.
Task 4b began afterward: four original-order full technical decodes passed;
eight existing first-source representative frames were visually sampled, not
human-certified individual-unit GT. Initial binding **failed before draft write**:
the new loader compared exact rational PTS with a rounded decimal last-frame
boundary and rejected a legal original export. This is a new-layer compatibility
defect, not evidence corruption; the failed receipt is retained. Local repair
`192d6eca1ef47a8d01f3a9eeb2866a8d08c6b426` changes only the two new validators,
their two tests and contract note. Covering RED 2 failed / 4 passed becomes
GREEN 6 passed; two adversarial PTS cases also pass. Targeted regression: 431
passed / two known Windows permission skips. No added time epsilon, no legacy
100ms/extractor/CLI change. Independent repair review approved, no new
Critical/Important breakage. Huge conflicting PTS guards reject before float
conversion. An initial reserved pytest parameter-name collection error is not
counted as defect RED. The original failed real binding receipt remains evidence.

## Task 4b actual pending data and gap

After the repair gate, all four sources again passed full technical decode;
unchanged first-source reports/indexes/images now pass checked new-layer binding.
Technical decoding is not human playback or absence/target certification.
Only the original-order second source received new two-second locator extraction:
64 frames and six contact sheets, all still pending. No harder/easier source
substitution, detector inference, GT generation, old-file overwrite or deletion.

Actual latest CLI command: `python -m clash_tracker_video.training_dataset_cli
validate-dataset PRIVATE_DRAFT --data-root EXPLICIT_ROOT --development OLD_LOCK`.
Captured subprocess exit is **3**, stderr empty. The PowerShell wrapper can report
1 for a nonzero native exit; the retained subprocess receipt establishes actual
CLI semantics. Anonymous output states `valid=true`, `training_data_ready=false`,
`evaluation_ready=false`, and the two fixed missing-training requirements.

| Distinct fact | Verified count |
| --- | ---: |
| Retained underlying matches / recordings | 4 / 4 |
| Historical human-confirmed target matches / ordinary deployments | 1 / 2 |
| New training-eligible target matches / deployments | 0 / 0 |
| Existing first-source representative frames reused | 8 |
| Second-source diagnostic locator frames | 64 |
| All draft frames / pending frames | 72 / 72 |
| New unit boxes / training images / training boxes | 0 / 0 / 0 |
| Unknown intervals / certified absent seconds | 6 / 0 |
| Real Training Dataset Locks / Model Locks generated | 0 / 0 |

No individual GT is manufactured: old group rectangles cannot supply unit support.
No certified absent interval or negative screenshot was inferred from sampling.
The minimum evidence gap from historical confirmation is three additional
target-positive match confirmations and six additional independent ordinary plays,
plus reviewed unit support for all qualifying plays. New-contract eligibility
currently lacks all four supported matches/eight supported plays. These are
different counts; do not report old plays as nonexistent or frames as new plays.
Other retained sources might supply some evidence; their target status is pending,
so this is not a claim that a fixed number of new recordings is already necessary.

The source-2 original terminal image visibly retains a substantial battle clock,
live king towers and ongoing combat. This creates a specific completeness
conflict, not merely absent result UI. Its earlier `user_confirmed` attestation
is retained unchanged. New additive draft marks completeness unestablished and
intake pending; it cannot silently become training eligible. One targeted user
question asks whether later footage is missing. No need to reconfirm distinct
natural matches or rewrite the old 2A2 lock. Source 3/4 target review is held in
original order until this fact is resolved, not excluded for recognition difficulty.

Private pending draft revisions, diagnostic observations, source references,
per-image hashes, exact timing and the next local command are in ignored outputs.
The public repository contains only schema/synthetic tests and these aggregates.
The data phase stops here for human resolution; no freeze attempt, training,
threshold selection or next slice is opened.

## Final stage verification and changed files

Fresh maintained regression completed: **680 passed / 2 skipped in 391.67s**,
exit 0, stderr empty. Skips are exactly the pre-existing evidence-loader symlink
creation permission case and the new checked-dataset symlink privilege case.
No GUI skip/error/failure. Fresh `pip check`: exit 0, no broken requirements.
Runtime package metadata confirms neither torch nor torchvision is installed.
Full raw command/stdout/stderr/exit receipts remain in ignored local outputs.
Stage-end protection passed: **16,745 original files byte-identical, zero missing
or changed** (including the old Development Lock, old boxes/source media and the
accepted 2B-1 results). All **22,239** current private files were Git-ignore checked;
zero not ignored, zero prohibited private/generated files tracked. All baseline
offline-video source/test/config files remain unchanged. Full branch secret/private
reference scan and `git diff --check` passed. Counts are the actual checked snapshot,
not a claim that subsequently added local receipts already existed at that point.

The branch adds only the approved plan/design, dataset contract, four new source
modules (`training_dataset_contract`, `training_dataset`, `unit_annotation`,
`training_dataset_cli`), their four test modules and a synthetic fixture helper.
The checkpoint additionally changes README, CURRENT_STATE, DEVELOPMENT_PLAN and
adds this verification document. No deleted file, SQLite/schema migration,
dependency/configuration, old-module implementation/test change or binary payload.
Real pending drafts, new locator images, binding/review/protection receipts and
the private handoff are additive ignored local files; no old lock/data overwrite.

Physical human-window acceptance and real exhaustive per-unit review: **Not Run**.
Training, detector inference/metrics, model packaging and Android build: **Not
Run**, prohibited or outside this slice. Native Tk shared-interpreter initialization
remains an explicitly unresolved runtime limitation as recorded above. Fresh
single-application process tests do not certify repeated launches in one process.
Schema and hashes cannot establish unobserved card absence, source authenticity,
human match independence or complete human labelling. Independent task reviews
supplement, not replace, later user/ChatGPT acceptance. No publication is authorized;
all commits remain on the local feature branch and main stays at the baseline.

## 2026-10-06 — superseded historical retained-source target recount

This was the bounded user-authorized ordinary-Minions evidence recount,
not a reversal of the subsequent multiclass direction or permission to train.
The user confirms source 02 has no later footage. Its retained actual EOF shows
**0:52 remaining with active combat**. New private draft revision v4 marks that
intake **excluded: mid-match truncation, not suitable for Training Dataset use**.
Its file, source hash, old indexes/images, annotations and prior attestations are
retained; no negative interval is created. Missing result UI alone remains legal.
Historical global completeness notes are explicitly labelled historical in v4,
with the source-02 claim superseded, not silently reapplied to all four matches.
Original v1-v3 drafts and old locked evidence are not edited.

Existing source 03 material is reviewed first, then source 04. Read-only visual
subtasks inspect all 18/12 contact sheets containing 159/107 unique sampled
frames and nine/seven unannotated original images respectively. Root spot-checks
also inspect the source-02 EOF, source-03 ground-unit confusion at 54s, and
source-04 small flying-group confusions at 14/128s. No detector or top-hand UI is
used to label targets. No new ordinary-Minions deployment is confirmed in either
sampled set; repeated survivors cannot supply a new independent deployment.
These are Codex visual-review observations, not fabricated ChatGPT confirmation,
new definitive GT or complete continuous-video playback. Two-second samples and
boundary frames cannot prove full-timeline absence. Unobserved, occluded and
ambiguous regions remain Unknown and never become Negative.

| Distinct fact at the historical recount | Count |
| --- | ---: |
| Retained sources / underlying matches | 4 / 4 |
| Confirmed mid-match-truncated source excluded | 1 |
| Source 03/04 sampled frames visually reviewed | 159 / 107 |
| Source 03/04 contact sheets visually reviewed | 18 / 12 |
| New confirmed ordinary target deployments from 03/04 | 0 / 0 |
| Historical confirmed target matches / independent plays | 1 / 2 |
| Historical gap against that request's four-match/eight-play confirmation | 3 / 6 |
| Historical single-unit boxes accepted in user-relayed ChatGPT review | 6 |
| Imported exhaustive unit boxes in the old native training draft | 0 |
| Native training-eligible target matches / deployments | 0 / 0 |
| Existing draft frames / Unknown intervals / certified absent seconds | 72 / 6 / 0 |
| Training Dataset Locks / Model Locks created by that recount | 0 / 0 |

Historical plays are ordinary opponent Minions at accepted onset 12/116s;
17/118s box observations are not new onset times or additional events. The six
accepted per-unit provisional boxes remain an explicitly attributed human-return
handoff, not automatic exhaustive-frame GT import. The 266 sampled review frames
are separate from the preserved 72-frame legacy draft; neither sampling volume
nor a box count substitutes for independent deployment count. At that checkpoint
material had at most three nonexcluded distinct matches. A continuation of that
old four-match contract would have required another complete target-positive
natural match; the current user instruction supersedes that route. This document
does not request new recordings or apply the old quota to the two-class smoke lock.

Fresh `validate-dataset` using actual private v4, the explicit local data root
and unchanged old Development Lock exits **3**, stderr empty. Actual checked
binding gives `valid=true`, `training_data_ready=false`, `evaluation_ready=false`,
native eligible counts 0/0. An in-memory-only contradictory copy that includes
the truncated source is rejected by the existing validator. No producer,
readiness gate, extractor, historical annotation, dependency or lock implementation
is changed to obtain these results.

Fresh related maintained tests (original offline environment; cwd
`tools/offline_video`):

```text
python -m pytest -q --tb=short -rs tests/test_training_dataset_contract.py tests/test_training_dataset.py tests/test_training_dataset_cli.py
151 passed, 1 skipped in 231.33s
```

Exit 0; the skip is the existing Windows symlink privilege case at
`test_training_dataset.py:464`. Fresh `pip check` exits 0, no broken requirements;
the original offline environment's package freeze equals its pre-existing
snapshot. **Full maintained regression: Not Run in this recount**, because no
production source/test/config/dependency is changed; preceding 908/3 runs are not
reported as current results. Full continuous video playback, new real extraction,
GT/absence certification, model installation/execution, training and model locking
are Not Run or prohibited in this round.

Fresh scoped hash protection confirms **1,448 existing files unchanged**, zero
changed/missing, including the four source MP4s, existing contact-sheet bundles,
drafts, source/index/report bindings, 2A2/2B-1 results, Smoke GT and offline code.
New receipts/drafts are additive ignored artifacts. No old file deletion or
overwrite. A separate read-only reviewer additionally checks 193 related old
JSON artifacts and the source-02 media hash. Initial one-off privacy checking
misclassifies the three prior-approved exact quoted repository model-interpreter
references and URI-scheme substrings in three official HTTPS links. Failed receipts
remain. The internal ignored checker is corrected narrowly: only the exact
quoted approved interpreter is distinguished; a drive token must not occur
inside an alphanumeric URI scheme. Private absolute paths, near-matching
interpreter paths, account IDs and secret patterns remain checked. No production
privacy policy or source evidence is weakened. Final privacy/link/diff receipts
and actual checked inventory counts are retained locally.

This round changes only CURRENT_STATE, DEVELOPMENT_PLAN and this verification
document, plus private additive v4/review/report/check receipts. Five prior dirty
documentation changes from Smoke GT/Phase B are preserved, not discarded or
committed. No SQLite/storage migration, production feature, new weights, threshold
choice or Model Lock. Branch remains `codex/module-2b2b-multiclass-infrastructure`,
HEAD `76400f5e532e8acd579806e0205584e57a4ff02a`, main
`8a03e288fb814d81b0a8e255b8004dbc4d0efb02`; no staging, commit, push or merge.
The earlier separately qualified model environment is preserved, not installed
or exercised again there. Training-use qualification stayed false within that
recount. Its gap report and four/eight validator remain historical evidence,
not the current continuation instruction or a smoke qualification precondition.

## 2026-10-06 — superseding private local Smoke data-lock authorization

The current user authorizes a separate **2-Class Training Dataset Lock v1**
(`two_class_training_dataset_lock`) for the unchanged parent
`two_class_smoke_gt_lock` v1: 11 confirmed boxes, Witch/Skeleton, match 01 / TRAIN and
match 04 / DEV_VAL. Provenance is `source_type=user_recorded_gameplay`,
`intended_use=private_local_research_poc`, `user_training_authorized=true`,
`external_upload=false`, `redistribution=false`, and
`rights_clearance=unverified`. The new scope's `training_qualified` is an
internal private local PoC gate, not legal clearance or official permission.
Old schemas/locks/readiness and every target-recheck artifact remain preserved;
the original 3–5-class gate is not weakened or retrospectively passed.

The separate smoke snapshot preserves 11 boxes/four frames. Default complete
selected-class supervision uses only three frames/10 boxes; the 72s Witch
positive is `positive_only_requires_unknown_safe_consumer`, with standard
full-frame loss/metrics prohibited by default and Unknown regions never background.

Status: **TWO_CLASS_TRAINING_DATASET_LOCKED; data-stage verification completed**.
The separately checked freeze receipt confirms exclusive v1 creation, dedicated
readiness/readback exit 0, scoped internal `training_qualified=true`, original
GT v1 unchanged and **1,462 protected existing files unchanged**. It does not
qualify a production training pipeline. Fresh joint private tests pass **65**
(40 new training-adapter + 25 original GT), no skips; full maintained regression
passes **908 / 3 existing Windows permission skips**, exit 0, 1052.47s, with
zero failures/errors. Pip and scoped documentation diff checks pass. Private
hashes remain in local receipts. Stop at the completed data-lock boundary.
The main evidence owner is
[VERIFICATION_M2B2B.md](VERIFICATION_M2B2B.md). No real training, weights download,
Phase C, Model Lock, blind testing, Android/live use or Git publication this round.
