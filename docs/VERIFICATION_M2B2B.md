# Module 2B-2B Verification

Current authorization is Phase C fixed-budget two-class smoke training; see
[the protocol](PHASE_C_SMOKE_PROTOCOL.md). The following Phase A/B/GT/data-lock
sections are historical results, not a veto of that separate current authority.
The initial Phase C checkpoint validates the unchanged training lock with exit 0,
reruns the 65 original/private GT-lock tests (all pass, 16.98s) and offline
`pip check` (exit 0). No training or download occurred in these checks.

Preserved separately authorized Phase B result (2026-10-06):
**MODEL_ENVIRONMENT_QUALIFIED**, synthetic only; `training_qualified=false`.
See the final Phase B section for new execution evidence. Earlier Phase A and
GT-only limits/results below retain their historical stage scope.

Dates: 2026-10-05–06. Status: **Tasks 1–5 verified/reviewed/locally committed;
final combined regression passes; Task 6 valid-but-insufficient and stopped at
the consolidated gap boundary — no real multiclass Dataset Lock claimed**.

## Historical Phase A authorization and baseline

The user reports ChatGPT plan verdict PHASE_A_AUTHORIZED_WITH_SIMPLIFICATION.
For that Phase A stage only Tasks 1–6 were authorized. Owner gate amendment is recorded in the existing
spec/plan and DECISIONS; no new planning document. Branch:
`codex/module-2b2b-multiclass-infrastructure`; baseline:
`d8a34a127e1507998fa0528d7d18bf244bb9001d`.

Phase A uses the existing fixed environment with no dependency additions. Phase B,
model installation, weights, training, Model Lock, blind-test work, Module 3,
Android/live work, push and merge were not authorized during that stage.

## Fresh pre-implementation checks

- `.\.venv\Scripts\python.exe -m pytest tools/offline_video/tests -q --tb=short -rs`:
  exit 0; **680 passed, 2 skipped in 436.32s**. The skips are the existing Windows
  symlink-privilege cases in evidence_prepare and training_dataset, not GUI skips.
- `.\.venv\Scripts\python.exe -m pip check`: exit 0, No broken requirements found.
- `git diff --check`: exit 0; no whitespace errors. Git reports normal LF/CRLF
  checkout warnings for amended Markdown, not test failures.
- A read-only SHA-256 baseline inventory covers **22,939 existing private files**
  under outputs/local_data. All were ignored and no private/media/weights tracked.
  The initial helper's newline-output check misread Git-quoted paths; an independent
  NUL-delimited check reported zero unignored files. The helper was corrected to
  NUL delimiters and the complete hash capture then succeeded. No private file changed.

Full stdout and private hash inventory are retained only in a fresh ignored
Phase A run directory. Private paths/content are not reproduced in this document.
The checks above describe the old baseline, not completion of new tasks.

## Task progress

Task 1: closed contract and both scoped repairs have passed independent
specification/quality review and final maintained regression.
Missing-interface RED: 77 failed. Malformed ancestor RED/GREEN: 1 failed/90
passed then 91 passed. Actual final-PTS rounding RED/GREEN: 1 failed/92 passed
then 93 passed. The independent task review identified a separate legitimate
terminal-frame/group containment rejection; covering RED: 2 failed/96 passed,
focused GREEN after narrow new-layer repair: 98 passed. Ordinary half-open
appearance ends remain exclusive; only the actual terminal frame can be included
when the group ends at the recording's actual last-frame boundary.

The latest complete run before that group repair: 773 passed / 2 known Windows
symlink-permission skips in 436.09s, exit 0, no GUI errors or skips. This is not
presented as full verification of the subsequent group repair. Final repaired
run: **778 passed / 2 known Windows symlink-permission skips in 445.52s**, exit 0;
no GUI errors or skips. Fresh pip check: exit 0, No broken requirements found.
Working/staged diff checks: exit 0. Final protection: **22,939 originals unchanged,
24,459 current private files ignored**, no forbidden tracked files, legacy
source/tests/config unchanged. Sensitive-pattern/text-only checks passed. Tasks
3–6 remain pending. No data freeze or model behavior is claimed.

Task 2: five scoped files frozen for independent review, not committed. Actual
focused run: 138 passed (39 readiness plus 99 closed contract). Combined
new/legacy contract regression: 255 passed. Old prepare/review/development
compatibility: 202 passed / one existing symlink-permission skip. Controller
read the JUnit receipts: respectively 138/255/203 total, zero failures/errors,
and 0/0/1 skips. Tool wait time is not asserted as the pytest-summary duration.
Initial RED: 17 failed; the invalid-null output refinement and later
causal/excluded, partial-own, terminal-unknown regressions each have named real
RED/GREEN evidence. Exact JUnit receipts are retained in the ignored run.
Pip/syntax/staged diff checks passed. Protection: 22,939 originals unchanged,
24,988 current private files ignored, legacy source/tests/config unchanged.
Full maintained suite is Not Run for this snapshot; it follows review
consolidation on final approved code. No scale snapshot or Dataset Lock created.
Independent Task 2 review identified two Important cases not covered by those
passing tests: owner branches of the same cause incorrectly gained extra scale
weight, and UTF-8 canonical serialization failure escaped the controlled invalid
readiness report. Both have been fixed and independently re-reviewed: Approved,
no new issues. Repair RED: 3 failed; GREEN: **142 passed in 68.61s**, with actual
stdout and JUnit evidence. The extra fourth regression verifies unrelated
programming errors are not swallowed. The final full run on 2026-10-06 returned
exit 1: **1 failed, 821 passed, 2 skipped in 1207.46s**. The failing legacy
`test_isolated_tk_child_faults_fail_parent_and_retain_full_output[skip]` expected
the child pytest's exit code 0 but got None. This is not yet diagnosed as a Tk
initialization error or implementation defect. Its complete stdout/XML remain
retained; no skip or old-test adjustment. Commit and Task 3 are held while its
existing child receipt and one unchanged focused diagnostic are checked. Those
focused readiness results do not replace the failed full run. Support cells
remain owner-specific; scale weighting is unique per match/cause/class. No real
draft, labels or locks are changed to address these synthetic regression cases.

The implementer read the original temporary child receipt before the diagnostic:
`exit_code=null`, `timed_out=true`, empty stdout/stderr and no JUnit document.
The diagnostic's ordinary pytest temporary-directory cleanup removed that old
child directory before its byte-copy attempt; the attempted destination is empty.
These child details are retained as a contemporaneous observation transcript,
not claimed as retained raw child bytes. Original full-run stdout/XML are intact.
That particular synthetic skip-test child
does not create Tk. One identical single-case diagnostic then passed, exit 0,
**1 passed in 20.19s**. No legacy source/test/config/timeout changed. Neither
result proves the timeout's cause or a native-GUI repair. One unchanged full
confirmation run is now authorized, preserving the failed run separately;
another failure stops without retrying or lowering validation rules.

### Confirmation run interrupted — Task 2 held, Tasks 3–6 not started

The single confirmation run uses the identical environment/command and separate
`task-2-confirmation-maintained.stdout.txt`. On 2026-10-06 its remaining log
reaches 87% with multiple error/failure markers, but has no final pytest summary.
At 09:00 local time no Python test process was visible and the requested JUnit
file did not exist. Main-controller inspection of the original session 11342
returns `Unknown process id 11342`; its exit status cannot be recovered from
the remaining tool state. The original worker was interrupted in `pending_init`
state to prevent an obsolete queued continuation from initiating more work;
this is NOT a passed full run and no count is inferred from progress markers.

A read-only Windows System event check confirms a sleep/resume during this
confirmation: event SleepTime `2026-10-05T16:31:46.1331059Z` / WakeTime
`2026-10-06T00:44:48.9951385Z`, i.e. approximately **00:31–08:44 Asia/Shanghai**.
Only event timestamps/provider/IDs and those two fields were inspected; no
power-setting change. This establishes environmental interruption, not the
specific cause of each residual error. It does not explain the earlier failed
run, which completed before this sleep interval.

No third run, old-test/timeout/config patch, Task 2 commit or Task 3 release.
The approved focused implementation is retained staged; its full verification
gate remains unsatisfied. The original failure and diagnostic evidence stay
distinct from this incomplete confirmation.

### Fresh blocked-handoff checks — main controller, 2026-10-06

- Existing `protect.py check`, tool session 87987: exit 0; **22,939 originals
  unchanged**, **26,349 current private files ignored**, privacy passed, legacy
  source/tests/config unchanged. Source recordings, old 2A2 Development Lock and
  accepted 2B-1 failed results are covered by the original inventory. No recapture.
- `.venv/Scripts/python.exe -m pip check`: exit 0, No broken requirements found.
- Working and staged `git diff --check`: both exit 0.
- Six changed Markdown documents: 24 local links checked, zero broken.
- Staged added-line private-key/token pattern scan: zero matches. This is a
  scoped hygiene scan, not a complete security or provenance certification.
- Independent documentation review found an obsolete current-design-only
  statement; it is now explicitly historical. Scoped re-review confirms that
  Phase A is authorized, Task 2 remains uncommitted, Tasks 3–6 not started.
- HEAD stays `0109070af1dc5d2f1080e9449d2f606c4d2346c5`; Task 2's exact five files
  stay staged. Controller CURRENT_STATE and this verification document remain
  unstaged/new. No commit on the failed gate, push, merge or next-phase work.

These passed protection/hygiene checks do NOT change the failed/incomplete full
regression verdict. No new real multiclass GT, scale snapshot or Dataset Lock
exists. Next continuation must resolve the regression gate in an uninterrupted
environment before Task 3; no legacy timeout/code alteration is authorized here.

### User-authorized stable continuation — Task 2 verified

The user explicitly superseded the previous blocked-turn no-third-run stop and
authorized an unchanged stable complete regression, local Task 2 commit on pass,
and continuous Tasks 3–6. No redesign, code rollback, new Review Packet or model
route change. The exact five staged implementation/test/contract-document files
were preserved, not rebuilt.

- Fresh command: `.\.venv\Scripts\python.exe -m pytest tools/offline_video/tests
  -q --tb=short -rs`, with a separate JUnit receipt. **822 passed / 2 skipped in
  506.33s**, exit 0; JUnit 824 total, zero failures/errors. The skips are the
  same two Windows symlink-permission tests. No GUI skip/error, no changed
  assertion or child timeout. The previously timing-out skip-child case passes.
- The local verification launcher requested ES_CONTINUOUS|ES_SYSTEM_REQUIRED
  only while running. No ES_DISPLAY_REQUIRED; no permanent power setting changed.
  Its finally receipt confirms the thread's request was released. This prevents
  automatic sleep, not explicit user sleep or arbitrary process termination.
- Fresh `pip check`: exit 0, No broken requirements found. Working/staged diff
  checks: exit 0. Staged added-line secret-pattern matches: zero.
- Reused original protection inventory, no recapture: **22,939 originals unchanged,
  27,028 current private files ignored**, legacy source/tests/config unchanged.
- Local Task 2 commit `f72420e1b6578a161fef622d764b2ee71c6b2a6d` contains exactly
  the five expected files, 1,131 insertions / 3 deletions. No push or merge.

Fresh stable-pass stdout/XML/launcher receipts remain in the existing ignored
phase run alongside the failed, isolated-diagnostic and interrupted-run evidence.
The fresh pass establishes the current verification gate; it does not prove why
the first child timed out or make the interrupted confirmation a completed run.
Task 3 is released; Phase B and model operations remain prohibited.

### Task 3 — checked binding and immutable data locks verified

Local commit `48452bf2c8fa91a4a2c5dafce25cd78dcb844ccb` changes exactly four
implementation/test/contract files. It adds checked media/sidecar binding and
separate pre-selection scale snapshots and selected dataset freezes. Existing
extractor/evidence/training sources and tests are not modified.

- Initial missing-interface tests failed as expected; expanded checked binding
  tests passed. Independent review then found two blocking safety issues:
  selected drafts were allowed to freeze the pre-selection scale snapshot, and
  an `os.close` fault could skip new partial-file cleanup. Actual regression RED:
  **3 failed / 1 passed**, exit 1; narrow fixes GREEN: **4 passed**, exit 0.
  The scale entry rejects selected drafts; nested cleanup runs despite close
  failure and only removes this operation's own incomplete file.
- Final five-file compatibility command includes `test_multiclass_dataset.py`,
  `test_multiclass_contract.py`, `test_multiclass_readiness.py`,
  `test_training_dataset.py` and `test_evidence_prepare.py`, with
  `-q --tb=short -rs` and separate JUnit receipt. **315 passed / 3 skipped in
  865.99s**, exit 0; XML 318 total, zero failures/errors. Three skips are Windows
  symlink privilege cases (one new, two inherited), not GUI skips. The Windows
  junction containment test executed. This is task compatibility, not the
  final combined Phase A full regression.
- Fresh pip and syntax checks exit 0; staged/worktree diff checks exit 0;
  two local documentation links valid; scoped secret/private-path hits zero.
- Original protection baseline reused: **22,939 unchanged originals,
  27,070 current private files ignored**, privacy passed, legacy unchanged.
  The process-bound automatic-sleep guard was released, without power-policy
  changes. Final frozen-diff independent re-review approved both repaired issues.

Checked loaders verify declared artifacts, PTS and paired producer metadata;
they do not re-decode source videos or certify original-video authenticity.
The bound operation hashes every referenced export dependency. Persisted locks
commit declared frame/media/sidecar hashes, not historical hashes of unrelated
unlisted locator images. Such images cannot supply GT/readiness/export support.
Historical private bytes remain separately covered by the protection baseline.
Task 4 is released; no real multiclass Dataset Lock or model operation is claimed.

### Task 4 — additive manual annotation, final tests verified

Initial missing-API RED: 18 failed, exit 1. One earlier wrong subprocess node
path is retained as a harness error, not intentional feature RED. Initial GREEN
reported 16 passed / 2 failed: canonical hash ordering exposed wrong annotation
display order. Narrow state regressions then produced actual RED 3 failed /
1 existing-source compatibility pass; a separate unknown test explicitly failed
on complete versus pending. Fixes passed all 23 then-collected cases.

Independent review additionally identified cross-box unapplied-control loss.
The first withdrawn-window event receipt did not prove the intended bug and is
retained as a harness failure. Corrected mapped real-Tk events verify callbacks
before the assertion: RED **2 failed / 1 compatibility pass**, exit 1; narrow
active-ID/Apply-first/new-box-mode GREEN **3 passed**, exit 0. The editor now
preserves unapplied A controls on selection of B and cannot bypass the guard
through save, navigation, drawing or new-box mode. No edit-buffer architecture.

Final frozen command runs `test_multiclass_annotation.py` and unchanged
`test_unit_annotation.py` with `-q --tb=short -rs` and a separate JUnit receipt:
**83 passed in 224.27s**, exit 0 (28 new + 55 inherited). XML 83 total, zero
failures/errors/skips; real native GUI tests do not hide initialization,
callback or subprocess failures. Source/test/contract SHA-256 match before and
after. The temporary automatic-sleep request was released.

New paired revisions are exclusive, sidecar first and checked draft last. Old
artifacts stay byte-checked; only owned new files are cleaned after failure.
First-box placeholders are never accepted as persisted checked GT. Original
intake/actual-time display order differs deliberately from canonical hash order.
Unknown/ignore content remains pending, not a negative. Scoped final independent
re-review approves all three repaired Important issues. Fresh pip/syntax checks
pass; main controller stages exactly three Task 4 files and cached diff check
passes. Fresh original-baseline protection exits 0: **22,939 unchanged originals,
27,112 current private files ignored**, privacy passed and legacy unchanged.
The process-awake request was released. Local Task 4 commit
`d70c0afe1b364484b4eb877ab6c2f7de48a07c5c` changes exactly three approved
files (1,114 insertions), without subsequent source/test/contract edits.
Task 5 is released; no push, merge or next-phase/model work.

### Task 5 — metadata-only exports and independent commands verified

Local commit `377831aedde90db23879911535f7391f2f505b42` adds exactly four
source/test files plus the contracts section (738 insertions). The independent
seven-command CLI is additive; old CLI/extractor/evidence/training sources and
tests remain unchanged. Metadata-only YOLOX/TorchVision exports require a checked
qualified lock, retain identity geometry and full-image blocking reasons, and
publish a manifest only after labels and an unchanged checked-lock reload.

- Missing-API RED: 11 failed, exit 1. First GREEN: 5 failed / 7 passed. Four
  failures exposed a new exporter overcheck of the broad outputs parent; only
  the destination leaf check was corrected, without weakening legacy path policy.
  The fifth was an occupied synthetic fixture directory, not an exporter failure.
  Corrected expanded GREEN: 17 passed in 210.33s, exit 0.
- Actual short-write regression RED: 1 failed, DID NOT RAISE, exit 1. A real prefix
  write had incorrectly allowed success publication. The narrow writer fix
  checks the returned byte count. Short-write, manifest-fsync owned-file cleanup
  and fresh-process native CLI annotation GREEN: 3 passed / 17 deselected in
  48.34s, exit 0; zero errors/skips. This is synthetic native GUI verification,
  not human review of the user's footage.
- Final focused command runs `test_multiclass_export.py`, `test_multiclass_cli.py`
  and unchanged `test_cli.py`, `test_evidence_cli.py`, `test_experiment_cli.py`,
  `test_training_dataset_cli.py`, with `-q --tb=short -rs` and separate JUnit:
  **115 passed in 549.64s**, exit 0 (20 new + 95 inherited); XML 115 total,
  zero failures/errors/skips. Fresh pip/syntax exits 0, two links valid,
  scoped credential/private-path scan zero matches. Frozen hashes matched.
- Main-controller staging of the exact five files exposed one extra EOF blank
  line in the previously untracked new export test. Earlier worktree diff checks
  did not cover it. Only that blank line was removed; definitive cached check
  then exits 0. The final combined maintained suite passes on this committed
  whitespace-clean snapshot, not merely inferred from the earlier focused pass.
- Original protection inventory reused: **22,939 original files unchanged,
  27,765 current private files ignored**, privacy passed and legacy unchanged,
  exit 0. The temporary automatic-sleep request was released. Final scoped and
  combined code reviews report no residual Important/Critical finding; these are
  local reviews, not ChatGPT independent acceptance.

Actual root/help and freeze help exit 0. Existing plan examples were synchronized
to positional input and `--scale-snapshot`, without new features or altered gates.
No real Dataset Lock, model installation/weights/Model Lock, push or merge.

## Inherited data limitations

Read-only metadata inventory retains four recordings in original order, with
four declared distinct natural matches and historical successful decode receipts.
The inherited pre-Phase-A draft had 72 pending representative/locator frames,
zero individual-unit labels and zero completed multiclass frame reviews.
Two ordinary-Minions deployments
and six combination boxes are historical evidence, not new individual GT.
Second-recording completeness has a concrete active-combat-end conflict; later
sources remain pending in order. Missing result UI alone is not incomplete.
In this phase the user explicitly replies that no subsequent footage exists and
instructs keeping recording 2 pending; no complete/negative claim is added.
That historical input had no multiclass candidate pool, splits, clean size
statistics or Dataset Lock. A new ignored preliminary handoff now reuses four
sources in original order, with whole-match TRAIN/DEV_VAL declared alternately
before class selection. It retains 75 existing frames, two historical confirmed
groups and eight image-assisted individual boxes **all pending**; no old group
box was automatically divided or converted into GT. Sources 3/4 remain pending
full human multiclass review. Source 2 remains pending under the user's latest
no-following-clip answer. Checked binding succeeds for 302 referenced files;
prospective readiness reports zero qualified classes, ready=false and
PROVENANCE_INSUFFICIENT, alongside data/owner/scale blockers. No scale snapshot,
Dataset Lock or new full-image absence certification was created. This is
unreviewed data, not proof that target units are absent from the recordings.
Training-use provenance is not established by technical decode or natural-match
attestation. Task 6 must report actual gaps without inventing evidence.

### Consolidated current-data gaps — not a new design or collection quota

Four user-supplied natural-match identities are retained, not four qualified
multiclass training matches. Only the first has inherited full-match rough human
review; it still lacks new exhaustive individual-unit GT. Recording 2 is pending
under the user's no-following-clip answer. Recordings 3/4 have technical/boundary
receipts, not completed human multiclass review. The new whole-match assignments
are TRAIN / DEV_VAL / TRAIN / DEV_VAL in original order, before class selection.
No recording in this already-exposed collection can become a Blind Test.

The five provisional visual hypotheses are `unit.minion`, `unit.cannon_cart`,
`unit.golden_knight`, `unit.flying_machine` and `unit.witch`. They come from the
first recording's inherited rough review, not a fixed product taxonomy or selected
PoC classes. Each currently has **zero qualified opponent support cells in both
TRAIN and DEV_VAL**. The eight provisional individual boxes remain pending;
the two historically confirmed Minions deployments are preserved, but combination
boxes do not supply new individual GT or an exhaustive training image.

The unmet gates are reported together:

- At least two qualified, isolated Development matches including DEV_VAL.
- Three to five qualified selected classes, with opponent support in both splits.
- At least one class with additional own support in both splits.
- At least two moving classes, including relative-small and medium/large under
  the fixed preselection policy. No clean qualified scale pool/cutpoints exist
  yet; pending boxes cannot establish those bins.
- Explicit training-qualified source/provenance evidence. Current sources have
  only manual-evidence scope; ownership of a recording alone does not certify
  rights in every depicted asset.
- Exhaustive whole-image class coverage and verified individual-unit/group rows.
  All 75 reused frames remain pending, not negative images or FP/min denominators.

Zero qualified support means **not yet reviewed/qualified**, not that these units
are absent. First finish the existing original-order reviews/individual labels;
then recompute the full candidate pool and add natural Development material only
if those actual support/owner/scale gaps remain. Do not demand Minions 4/8, change
splits after selection, lower gates, or invent absence/independence/provenance.

### Task 6 — actual read-only command checks and insufficient-data boundary

The root controller ran the final committed seven-command implementation against
the new pending draft with the explicit project data container:

```powershell
.\.venv\Scripts\python.exe -m clash_tracker_video.multiclass_cli validate-dataset <explicit-pending-draft> --data-root <explicit-project-root>
.\.venv\Scripts\python.exe -m clash_tracker_video.multiclass_cli scale-report <explicit-pending-draft> --data-root <explicit-project-root>
```

Both **native CLI subprocess exit codes are 3**, valid-but-insufficient. Actual
stdout and command/exit/awake-release receipts are retained separately as
`task6-final-validate.*` and `task6-final-scale.*` in the ignored phase run. The
first outer PowerShell tool wrapper normalized a nonzero native status to 1;
its launch receipt records child exit 3. The scale wrapper explicitly propagated
`$LASTEXITCODE` and reports 3. Neither is a malformed-evidence exit 2 or a ready 0.

Readiness: ready=false, **PROVENANCE_INSUFFICIENT**, zero qualified classes and
one inherited human-reviewed eligible match; all data/owner/scale reasons are
also present. Scale report: **SIZE_COVERAGE_INSUFFICIENT**, zero qualified scale
classes, Q25/Q75 null, with fixed `dev_moving_area_quantiles_v1` and unchanged
candidate/split digests. No pending pixel sizes were promoted into clean scale
statistics. The six files of the new current handoff have identical before/after
SHA-256 across both checks; neither command edits them. Both temporary automatic-
sleep requests were released. Earlier checked binding verified 302 referenced
files/four recordings/75 frames/eight all-pending boxes.

No scale freeze, selected-class freeze, real Dataset Lock or export was attempted
on this insufficient material. New metadata and provisional individual boxes
exist only in a new ignored revision; no original PNG/report/index/video/old lock
was changed, decoded again or needlessly regenerated. Task 6 stops at the approved
combined gap-report boundary, not at MULTICLASS_DATASET_LOCKED. Real human
multiclass review, source qualification and resulting clean dataset remain pending.

## Final combined maintained regression — main controller

Fresh final command on source commit `377831aedde90db23879911535f7391f2f505b42`:

```powershell
.\.venv\Scripts\python.exe -m pytest tools/offline_video/tests -q --tb=short -rs --junitxml=<new-ignored-final-receipt>
.\.venv\Scripts\python.exe -m pip check
```

**908 passed / 3 skipped in 1292.19s**, native exit 0. Controller-read JUnit:
911 total / zero failures / zero errors / three skips. All are OS symlink
privilege cases: evidence_prepare:105, multiclass_dataset:387 and
training_dataset:464. No GUI skip or error; the existing Windows junction case
and the previously timing-out legacy synthetic skip-child regression executed.
Maintained test path is explicit to avoid collecting copied historical Packet
code under ignored outputs. No test selection, assertion, timeout, plugin,
dependency or old source was altered to force this pass.

Actual stdout/XML/command receipts are `phase-a-final-maintained.*`, retained
beside earlier failed/interrupted runs, not replacements. The process-bound
automatic-sleep request was released; no permanent OS policy/display requirement.
Fresh final pip check exits 0, No broken requirements found; its independent
receipt confirms release. Post-run `git diff --exit-code HEAD -- tools/offline_video`
exits 0, confirming the source/test snapshot stayed unchanged through this run.
This verifies the infrastructure and legacy compatibility, not real training,
recognition reliability, video authenticity or dataset readiness.

Final root original-inventory protection (`phase-a-final-protection.*`) exits 0:
**22,939 existing private files byte-unchanged; 28,450 current private files
Git-ignored; privacy passed; legacy source/tests/config unchanged**. This covers
source MP4s, original PNGs/index/reports/labels, old 2A2 Lock and accepted 2B-1
FAIL. The original inventory was reused, never recaptured. The final protection
guard was released. No source re-extraction, old-evidence edit, real inference
rerun, Model Lock, push or merge. All code reviews and the scoped documentation
consistency review approved; this still requires ChatGPT/user formal acceptance.

Git boundary: source checkpoint `377831aedde90db23879911535f7391f2f505b42`,
followed only by a local documentation checkpoint whose SHA is supplied in the
handoff. Feature branch retained; local main remains
`8a03e288fb814d81b0a8e255b8004dbc4d0efb02`. No remote mutation, PR or Release.
The approved subtask/verification/checkpoint workflow retained original failed
receipts and every local task boundary, instead of replacing historical evidence.
Final staged/worktree diff checks exit 0. Eight relevant Markdown documents have
57 checked local links and zero broken targets. Full-baseline added-line
credential/private-personal-path matches: zero; forbidden tracked media/private/
model artifacts: zero. Exact public change set: 21 text-only Markdown/Python files
(15 added, six modified, none deleted), within the listed module scope.

## Not Run

Model installation, pretrained downloads, GPU qualification, real training,
threshold tuning, Model Lock, prospective test/GT/prediction, Module 3 and mobile
evaluation: Not Run — outside authorized Phase A.

## Public files and storage boundary

Relative to the Phase A baseline, the public change set adds:

- `docs/MODULE_2B2B_CONTRACTS.md` and this verification document.
- Six additive sources under `tools/offline_video/src/clash_tracker_video/`:
  `multiclass_contract.py`, `multiclass_readiness.py`, `multiclass_dataset.py`,
  `multiclass_annotation.py`, `multiclass_export.py`, `multiclass_cli.py`.
- Seven synthetic test/helper files under `tools/offline_video/tests/`:
  `multiclass_fixtures.py`, `test_multiclass_contract.py`,
  `test_multiclass_readiness.py`, `test_multiclass_dataset.py`,
  `test_multiclass_annotation.py`, `test_multiclass_export.py`,
  `test_multiclass_cli.py`.

It modifies six existing documents: README, CURRENT_STATE, DECISIONS,
DEVELOPMENT_PLAN, the existing multiclass design/spec and its implementation plan.
No public files are deleted. No legacy source/test/dependency change. Versioned
local JSON/sidecar/lock/export files are additive and ignored; actual user data
has only a new pending revision, not a qualified frozen training dataset.
No SQLite, migration, cloud, repository-layer app storage or Android change.
TypeScript/ESLint/web or Android builds are not applicable to this Python-only
offline data-tool stage, and are not represented as passed tests.

A fresh metadata-only package inventory exits 0: none of torch, torchvision,
YOLOX or Ultralytics is installed in the fixed environment; no model imported.
Its actual stdout/awake-release receipt is `phase-a-final-model-boundary.*` in
the ignored phase run. This is not GPU or future training qualification.

The inherited separate Minions lock, accepted template-baseline FAIL and all
old evidence remain protected. Formal ChatGPT Phase A acceptance and further
real-data human/source qualification are still pending; no automatic next phase.

## 2026-10-06 — Matches 03/04 human review preparation only

Scope: the user returned a contact-sheet/key-image review of matches 01/02 and
authorized preparing matches 03 then 04 with existing tools. No production
source/test/dependency, readiness rule or split changes. No new planning stage.
The returned findings are an additive private non-GT handoff, not automatic
annotation import. The original 75-frame/eight-pending-box draft is unchanged.
Six original Minion boxes are reported accepted by the returned reviewer; Witch
form stays unknown and separated sightings do not by themselves certify new
deployments. Reported spawned Skeletons retain the original wording and the
existing canonical `summoned` interpretation only if confirmed; no causal root
or card deployment is invented. Match 02's ongoing-battle EOF conflict remains.

Fresh command, fixed environment, from repository root:

```powershell
.\.venv\Scripts\python.exe outputs/module2b2b/phase-a-20261005/awake_run.py review-matches-03-04-20261006 outputs/module2b2b/human-review/assembly/prepare_matches_03_04.py
```

The assembler is an ignored one-off artifact script, not a new application
feature. It reuses unchanged `prepare_evidence` / Module 1 extraction and strict
`load_indexes`; existing boundary reports and PNGs are copied byte-for-byte into
fresh private outputs. Requests are fixed before inspecting pixels: match 03
uses 2, 4, ..., 282 seconds, reusing the already available 284-second boundary
frame; match 04 uses 2, 4, ..., 202 seconds. Both new exports return success.

Actual result: **242 new successful requests + 24 reused unique PTS frames =
266 unique review frames**. Match 03 / TRAIN has 159 frames and 18 contact sheets;
match 04 / DEV_VAL has 107 frames and 12 contact sheets. Source order and
whole-match assignment are retained. There are zero candidate boxes in these
two new review matches; all eight original boxes remain protected outside this
bundle. The old EOF occurs in two reused reports, so there are 25 physical
reused PNG copies but only 24 unique reused frames. Thirty main review contact
sheets are distinct from 21 auxiliary native extractor previews.

Fresh artifact verification checks all 266 PTS/geometry/source mappings, original
PNG SHA-256 values, preview gameplay-pixel crops and contact-sheet tiles. Human
object/group worksheets are blank, every frame is pending, and no deployment,
absent interval or Negative is inferred. A separate read-only inventory also
loads all five strict report/index pairs, obtaining the same 159/107 unique
frames, and verifies every local gallery link. A few rendered sheets/originals
were inspected for layout only, not substituted for full human label review.

Process exits **0**, elapsed 292.42 seconds; its temporary system-awake request
is released. No permanent power-policy or display-awake change. Actual stdout
and release receipt are retained under the ignored phase-run directory.
Fresh `pip check` exits 0, `No broken requirements found`; production
`git diff --exit-code HEAD -- tools/offline_video` and `git diff --check` exit 0.
Full pytest: **Not Run** in this artifact-only step; the 908/3 suite above remains
historical infrastructure evidence, not a new result.

Input protection reuses stored historical hashes rather than recapturing a new
baseline: **645 relevant existing files unchanged**, including the four MP4s,
original review frames/boxes/pending files, old review bundle/ZIP, boundary
exports, 2A2 Development Lock and original 2B-1 JSON results/protocol. The new
ZIP passes CRC and every archived member SHA-256 comparison, and source bundle
hashes remain unchanged by packing. All new private outputs are Git-ignored;
MP4s are not embedded in the ZIP. Provenance remains facts only:
`user_recorded_gameplay / local_research_training_poc / redistribution=false`,
not legal authorization or promotion of training eligibility.

No old evidence/lock write, match 01/02 re-extraction/re-review, model inference,
training, dataset/model freeze, gate reduction or Phase B. The new review
material is not imported into the existing draft, so readiness is not recomputed
or claimed improved. Stop for human review of matches 03/04 before support and
Scale Coverage Gate evaluation. No commit, push or main integration in this step;
HEAD remains `76400f5e532e8acd579806e0205584e57a4ff02a`. Only the two public
state/verification documents are updated after successful artifact checks.

## 2026-10-06 — Minimal two-class human drafts, no freeze

Authorized scope: standalone private Witch/Skeleton proposals for match 01 / TRAIN
and match 04 / DEV_VAL. The user explicitly separates eventual Smoke GT Freeze
from training qualification. This turn implements neither lock/production contract;
old 3–5-class code, schema and readiness remain unchanged. No new planning stage.

Fresh artifact command, fixed environment from repository root:

```powershell
.\.venv\Scripts\python.exe outputs/module2b2b/human-review/assembly/prepare_two_class_drafts.py
```

The ignored one-off assembler strictly loads two existing report/index pairs
using unchanged `load_indexes`, then byte-copies existing PNGs. There is no new
decode/extraction, model prelabel or automatic GT import. Proposals were manually
located in those existing images, not confirmed by ChatGPT. Selected relative
PTS times are 163/164s for match 01 and 68/72s for match 04, at 1/90000 time base,
432×960 original geometry. Frames, recording and underlying-match identities
are preserved independently, with unchanged TRAIN/DEV_VAL assignments.

Actual result: **four frames, twelve approximate bbox proposals (four Witch /
eight Skeleton candidates), four proposed observation-episode groups, one
contact sheet, twelve exact box crops and twelve 4× context crops**. Every
object/group and proposed Witch→Skeleton source edge is pending_human_review.
Reviewer/confirmation fields are null; confirmed independent deployments = 0.
Entity/deployment/source-card/causal-root identities are not invented. The shared
Skeleton episode is not a claim of one summon wave or continuous individual
identity; final review can split/correct it using evidence, not frame count.

Witch form stays unknown. Skeleton raw origin is `spawned`, explicitly a pending
source proposal rather than proof of Witch causality or Skeleton card placement.
Fourth-match units have stronger class/boundary uncertainty and may be rejected.
A larger gold-colored 72-second bridge unit is retained only as an uncertain
region, not forced into a Skeleton box. Marked boxes are non-exhaustive: remaining
units, obscured targets, effects and unboxed regions cannot become Negative.

The bundle contains originals, box overlays with a separate 130px metadata header,
pixel-coordinate crops, local index.html, contact sheet, draft JSON/groups/CSV,
blank human-return decisions, provenance facts and the two-lock boundary summary.
Provenance remains `user_recorded_gameplay / local_research_training_poc /
redistribution=false`, with `training_qualified=false` and no legal conclusion.
Neither a Smoke GT Lock nor a ready-for-training Dataset Lock is created.

Fresh assembler exits **0**. Mechanical checks pass for strict source PTS/identity,
PNG copy SHA, in-bounds integer xywh, exact crop pixel equality, pending/null
confirmation states, match-local relationships, local gallery links and Git ignore.
Historical stored hashes are reused: **1,256 protected existing files unchanged**,
including original recordings, old pending labels/boxes/review bundles, selected
source frames/reports, the 2A2 Development Lock and accepted 2B-1 JSON results.
This is the scoped protection set, not a fresh repeat of the 22,939-file inventory.

The ZIP contains 45 members, 5,197,074 bytes; CRC and every member SHA match the
assembled source. ZIP SHA-256 is retained in the private packaging receipt.
All new paths are ignored; no MP4 or model artifact is embedded. The private
packaging receipt records full source-member hashes and output paths. Rendered
overlays/crops are inspected for presentation, not treated as final human GT.

Fresh `pip check` exits 0 (`No broken requirements found`). Source diff against
HEAD is empty. Full pytest: **Not Run** because this step only generates private
review artifacts and updates memory documents; the earlier 908/3 result is not
reported as a fresh regression. No installation, weights, inference, training,
old evidence/lock overwrite, readiness promotion, Phase B or later module.
No commit, push or main integration; stop for final ChatGPT bbox/group review.

## 2026-10-06 — User-relayed final review and dedicated Smoke GT Lock v1

The user explicitly reports TWO_CLASS_SMOKE_HUMAN_REVIEW_CONFIRMED for the exact
small review ZIP and supplies every object/group/coverage decision. This is
the authority for ingestion, not a new ChatGPT reply retrieved by Codex in this
turn. The external review timestamp is unknown/null; local processing time is
recorded separately. The original ZIP and its pending draft stay unchanged.

Final results are preserved in a new ignored human-return/CSV revision:

- Objects 01–11 confirm: **11 positive boxes = four Witch + seven Skeleton**.
  Object 12 rejects with `too_ambiguous_to_confirm_as_skeleton`; it is Unknown,
  not background/Negative, and is excluded from positive GT.
- Every bbox is the original accepted integer xywh. Owner is opponent and form
  remains unknown for all confirmed objects; no normal-form coercion.
- Four accepted appearance groups: each match has one confirmed independent
  Witch deployment group; both Skeleton groups are spawned-from their same-match
  Witch group and **not Skeleton-card deployments**. Counts are group-only;
  source-card/entity/causal-root IDs and exact spawn times are not invented.
- Match 01 / TRAIN uses 163/164s; match 04 / DEV_VAL uses 68/72s. The 163/164/68s
  frames are reported exhaustive for the two selected classes. At 72s only
  Witch11 is positive, rejected Skeleton12 stays Unknown, and coverage remains
  non-exhaustive. This frame is not complete-supervision background. Four sampled
  frames do not establish full-timeline negatives or an FP/min denominator.
- Visibility/occlusion are user-authorized local moderate/low quality metadata;
  they are not falsely attributed as precise values separately supplied by ChatGPT
  and cannot change confirm/reject decisions.

The ignored one-off assembler reuses strict `load_evidence`, `canonical_bytes`,
`load_indexes` and checked private-path/ignore helpers. It does not call the
old training-dataset freeze or Model-linked Test GT freeze, and does not modify
any production source/schema/test/configuration. Its dedicated closed envelope
and exact expected-payload binder support **this supplied Development review**,
not a general-purpose new production schema or media authenticity certificate.

Actual freeze command (exit 0), process-bound awake guard released:

```powershell
.\.venv\Scripts\python.exe outputs/module2b2b/phase-a-20261005/awake_run.py smoke-gt-freeze-20261006-2fbe34 outputs/module2b2b/human-review/assembly/freeze_two_class_gt.py
```

Exclusive immutable snapshot:
`two_class_witch_skeleton_development_gt.two_class_smoke_gt_lock.v1.json`
(private ignored artifact).
Kind = `two_class_smoke_gt_lock`, freeze version = 1. Strict readback and rebinding
pass. Canonical full-envelope and GT semantic digests are recorded privately.
Lock file SHA-256:
`f48b401136e3285700d5000d73fed4c6381131cfabcbf956c2f3ee96804d97f1`.
The digest binds class/bbox/owner/form/origin, group/source relations, rejection,
Unknown/coverage, underlying-match/recording/split semantics, source image/PTS/
report/index metadata and the supplied review/ZIP references. No original lock
or evidence is overwritten. Version reuse, including renamed existing files,
is refused; write/sync failure only cleans that invocation's new partial file.

Fresh original-data protection: **1,303 existing files unchanged**, using stored
hashes before/after, including original recordings, original review packet and
draft, selected source frames/reports, old 2A2 lock and accepted 2B-1 results.
This is scoped protection, not a fresh claim about all 22,939 historical files.
PNG/index identity and every selected bbox/source relationship are rechecked
without decoding source video, re-extracting frames or rewriting labels.

An internal read-only review verified actual GT/lock/human-return/CSV decisions.
It noticed inherited candidate fields in the first presentation's rejected CSV
row and historical doubts/flags in its trace. A new **presentation-only revision**
fixes final rejected class/bbox/group/source to empty and owner/origin to Unknown;
historical fields are explicitly `draft_*` or nested `draft_annotation`. Confirmed
GT is a separate `final_annotation`, null for object 12. The original nine
revision/lock files and frozen GT hash remain unchanged. This is not a second
freeze or a silent modification of locked evidence.

Final presentation:
`outputs/module2b2b/two-class-smoke/review-final-aa765cec58a94f958d715efc8c3521ad/`.
It contains filled human-return, corrected review CSV, reviewed objects/groups,
frame index, identical reviewed GT, metadata-source clarification and manifest.
All outputs are confirmed Git-ignored and untracked. The read-only re-review
passes presentation consistency; it is not a substitute for the user's supplied
external pixel review. No media is uploaded or redistributed in this step.

Fresh private GT tests: **25 passed**, exit 0, actual stdout/receipt:
`smoke-gt-targeted-final-20261006-fd2117.*` in the ignored phase-run directory.
Tests include rejection exclusion, Unknown form/source preservation, partial frame
protection, original bbox/split identity, deterministic serialization, tampering
with recalculated digest, qualification promotion rejection, duplicate/renamed/
corrupt-version refusal and owned failed-write cleanup. Negative mutations use
in-memory/test-owned fixtures, never real recordings/labels. Initial missing
behavior and failure-cleanup/presentation/version edge tests were observed red
before their scoped private implementation fixes.

An initial repository-root `pytest -q --tb=short` exited 2 during collection,
because ignored archived Review Packet test copies were included alongside source
tests. The three import mismatches were test_baseline, test_baseline_io and
test_experiment_cli. Nothing was deleted, renamed or changed in the old packets
or production tests. The corrected full maintained suite uses its existing
package configuration and official test directory:

```powershell
.\.venv\Scripts\python.exe outputs/module2b2b/phase-a-20261005/awake_run.py smoke-gt-maintained-regression-20261006-02dc99 -m pytest -c tools/offline_video/pyproject.toml -q --tb=short tools/offline_video/tests
```

The corrected full run exits **0: 908 passed / 3 existing Windows permission
skips, 1289.98 seconds**. No failures or GUI errors. Actual command/stdout/receipt
are `smoke-gt-maintained-regression-20261006-02dc99.*` in the ignored phase run;
the process-bound sleep guard is released. The initial collection-error log is
retained separately, not retrospectively called passing. Fresh `pip check`
exits 0, `No broken requirements found`. Final diff/link/privacy checks pass;
all source/test/dependency files remain unchanged against HEAD.

That GT-only stage's scope result was **Smoke GT frozen only**: `training_qualified=false`,
`ready_for_training=false`, no real Training Dataset Lock, no Model/Test GT Lock,
no model installation, weights, inference, training, Phase B or later module.
Training provenance/readiness remains a separate unmet gate, not a legal grant
from gameplay recording or this GT snapshot. No SQLite/migration/cloud change,
no commit, push or main integration. Only status/decision documents and private
append-only artifacts change; preserve the old schemas, locks and FAIL results.

## 2026-10-06 — Phase B isolated Model Environment Qualification

### Authorization, baseline and isolation

That Phase B user request separately authorized installation and synthetic
CUDA forward/loss/backward/optimizer/checkpoint/inference, Nano first and Tiny
second. It supersedes the old Task 7 no-optimizer/checkpoint/Nano-only wording
for this probe only. No real GT training, weights download, training lock,
formal training or later module is authorized. `training_qualified=false` remains.

Current branch: `codex/module-2b2b-multiclass-infrastructure`. HEAD stays
`76400f5e532e8acd579806e0205584e57a4ff02a`; main stays
`8a03e288fb814d81b0a8e255b8004dbc4d0efb02`. Five pre-existing dirty documentation
files are preserved and updated in place; no source/tests/offline requirements
changes, staging, commit, push or merge. All new runtime/audit/checkpoint/probe
files are under the separate ignored run directory:

`outputs/module2b2b/environments/phase-b-yolox-20261006-8431/`.

Its `venv/Scripts/python.exe` is the new model interpreter; the existing `.venv`
remains the offline tool environment. Windows 11 Home Chinese, 10.0.26200 x64;
Python 3.12.4; NVIDIA GeForce GTX 1050 Ti, 4096 MiB, driver 582.28, WDDM,
compute capability 6.1. Driver headline CUDA 13.0 is its maximum, not this runtime.
No driver/system CUDA toolkit or permanent power-policy change is made. Log
wrappers use process-bound temporary system-awake requests and release them.

### Exact dependencies, source and license audit

- PyTorch **2.7.1+cu118**, TorchVision **0.22.1+cu118**, actual runtime CUDA
  **11.8**, cuDNN **90100**. The Windows CPython 3.12 wheels come from the
  official PyTorch index; matched versions are listed in
  [official prior-version instructions](https://pytorch.org/get-started/previous-versions/).
- YOLOX **0.3.0**, pinned official commit
  `6ddff4824372906469a7fae2dc3206c7aa4bbaee`,
  [official source](https://github.com/Megvii-BaseDetection/YOLOX/commit/6ddff4824372906469a7fae2dc3206c7aa4bbaee).
  This version string is not treated as the older 0.3.0 tag. The source is
  integrated via the isolated environment's source-path file, not a fabricated
  pip distribution or modified requirement metadata. Runtime/source file hashes
  match the official ZIP; nine non-runtime documentation/demo Markdown symlinks
  are omitted due to Windows link permissions, and the original ZIP is retained.
- Minimal direct closure: NumPy **1.26.4**, OpenCV-headless **4.11.0.86**,
  loguru **0.7.3**, psutil **7.0.0**, packaging **25.0**, tabulate **0.9.0**,
  Windows binary pycocotools **2.0.10**, plus normally resolved transitive packages.
  **21 pinned new distributions + pip 24.0 = 22 installed distributions**.
  No full legacy ONNX-simplifier/Trainer stack is installed merely to import
  model operations. This is not full official Trainer qualification.
- Every resolved distribution has version, official wheel URL/SHA and declared
  license metadata recorded **before installation**. Installed metadata and
  actual bundled license/notice text/SHA are recorded **after installation**.
  PyTorch/TorchVision BSD-3-Clause, YOLOX Apache-2.0 and dependency/bundled
  notices are retained. New PEP-639 fields absent from pip 24 reports are obtained
  from version-specific official PyPI metadata, not guessed from repository names.
  Source license does not certify dataset/weights or gameplay rights.
- Torch wheel SHA-256:
  `80855ec840b7b06372ff43535d01393a8ec101842618d1f9ed629572b52aed71`;
  Vision wheel:
  `3e927a3b0b08c7582cfa09e5f16b35435de390a612cfe76eed1418ab7b68d6b6`.
  Installation uses the complete version/hash-pinned requirements, only binary
  wheels and official indexes. Both environments' pre-install pip checks pass.
  The successful isolated installation exits 0; post-install pip check passes.
- Future identifiers only: official release **0.1.1rc0 / yolox_nano.pth** and
  **0.1.1rc0 / yolox_tiny.pth**,
  [official release](https://github.com/Megvii-BaseDetection/YOLOX/releases/tag/0.1.1rc0).
  `downloaded=false`, provenance qualification pending. No COCO/YOLOX pretrained
  weight, Clash Royale weight or training image dataset is downloaded. The
  official source ZIP includes six upstream illustration/demo image assets;
  these remain unused by the probes and are not added to any training dataset.

The initial Torch metadata resolution/download timed out after a partial large
wheel; the retry completes from the official endpoint and matches the expected
hash before installation. The initial install-labelled pip command exits with
the requirements-file-missing error because the preceding license audit has not
yet emitted its lock; it installs no packages. Both failed receipts remain
separate, not erased or called passing.
Pre/post evidence: `preflight.json`, `complete-pre-install-audit.json`,
`requirements-resolved.txt`, `install-report.json`, `install-isolated-retry.*`,
and `post-install-audit.json` inside the ignored run directory.

### Actual GPU synthetic results

The closed request allows only 416 / FP32, random initialized models, two
anonymous toy classes, randomly generated in-memory tensors and two toy boxes.
It cannot name or open a real dataset. Nano batch 1 must qualify before Tiny or
optional batch 2 can run. CUDA availability is verified with real matrix kernels;
model/labels/loss/gradients are on `cuda:0`. Assignment is observed in GPU mode
and CPU fallback is a failure. Official optimizer uses nonzero lr; parameter
changes are measured rather than inferred from merely calling `step()`.

| Probe | Synthetic steps | Max parameter change | Peak allocated MiB | Peak reserved MiB | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| Nano / 416 / b1 | 3 | 5.066394806e-7 | 122.31 | 134 | exit 0 / passed |
| Tiny / 416 / b1 | 1 | 9.685754776e-8 | 147.93 | 182 | exit 0 / passed |
| Nano / 416 / b2 (optional) | 1 | 1.192092896e-7 | 219.25 | 234 | exit 0 / passed |

These are `torch.cuda.max_memory_allocated/reserved` from a fresh child process,
including checkpoint restoration, not the entire GPU/card peak. They exclude
context/driver/WDDM/display/other applications; starting free memory is about
3.28 GiB. Actual future data augmentation, object counts and long training need
their own measurement. No OOM or CPU assignment fallback occurs in these probes.
The first Nano cold-start is slow (245.44s total, first step 43.16s); warm step
times are not promoted into a real-video throughput/latency claim.

Each probe verifies finite positive real YOLOX loss, finite nonzero CUDA gradients,
optimizer update, strict model and optimizer state equality after save/load,
restored inference, and actual TorchVision plus YOLOX CUDA NMS. Checkpoints are
new synthetic artifacts, not downloaded weights or Model Locks. Restored output
max absolute difference is **0.0** in all three; shapes are `(1,3549,7)` or
`(2,3549,7)`. In-memory pycocotools mask encode/decode/area/bbox and toy COCO index
also pass. No real images, GT, negatives or appearance groups are loaded by a model.

Python audit counters are **network_attempts=0, forbidden_repo_opens=0**.
The closed probe uses only trusted audited local source/imports; this audit guard
is not a native-code/subprocess/network OS sandbox or formal isolation proof.
The old official source emits an AMP deprecation warning under Torch 2.7; no
functional failure follows, and upstream source is not patched to silence it.

Actual commands (exact command arrays are retained in receipts):

```powershell
$probePython = (Resolve-Path 'outputs/module2b2b/environments/phase-b-yolox-20261006-8431/venv/Scripts/python.exe').Path
.\.venv\Scripts\python.exe outputs/module2b2b/environments/phase-b-yolox-20261006-8431/run_logged.py nano-b1 $probePython model_probe.py yolox-nano 1 attempt01
.\.venv\Scripts\python.exe outputs/module2b2b/environments/phase-b-yolox-20261006-8431/run_logged.py tiny-b1 $probePython model_probe.py yolox-tiny 1 attempt01
.\.venv\Scripts\python.exe outputs/module2b2b/environments/phase-b-yolox-20261006-8431/run_logged.py nano-b2 $probePython model_probe.py yolox-nano 2 attempt01
```

The child interpreter argument is **absolute** because the child runs with cwd
set to its run directory. Stdout/receipt pairs
are `nano-b1.*`, `tiny-b1.*`, `nano-b2.*`; per-model `result.json` and synthetic
checkpoints remain in fresh `*-attempt01` directories. No real experiment is rerun.

### Fresh tests and protection

Private synthetic request/result guard tests follow observed RED then GREEN;
final **16 passed**, exit 0 (`contract-final-gate-green.*`). Checks cover forbidden
data/weights, invalid/nonfinite config, missing GPU/nonzero-update/checkpoint/NMS
proof and final memory/audit gate. Read-only probe review catches optional batch2
ordering and pre-final-counters status gaps, fixed and tested before model runs.
An earlier test failure was a controlled fixture path incorrectly nested under
the permitted run directory, not a relaxed production guard; failed receipt kept.

Fresh full maintained offline regression:

```powershell
.\.venv\Scripts\python.exe outputs/module2b2b/phase-a-20261005/awake_run.py phase-b-offline-regression-20261006-8431 -m pytest -c tools/offline_video/pyproject.toml -q --tb=short tools/offline_video/tests
```

**908 passed / 3 existing Windows permission skips in 1179.22s**, exit 0. Wrapper
elapsed 1184.39s, awake request released. Actual `phase-b-offline-regression-20261006-8431.*`
stdout/receipt is separate from the prior GT-stage 908/3 run. No production
test, timeout, configuration or dependency is changed to get this result.

Final checks use the exact preflight scoped inventory: **1,398 existing files
unchanged**, including original recordings, GT/media/review artifacts, 2A2 lock,
2B-1 FAIL, all offline source/tests/config and `.venv/pyvenv.cfg`. This is not a
claim of rehashing the entire historical 22,939-file inventory. `.venv` freeze
remains exactly identical; both final pip checks pass. Installed version set
and pinned YOLOX runtime source hashes are unchanged. Final Git diff/link/sensitive
pattern/privacy checks pass: only the same five documents are dirty, no staged
files, no private/model media tracked, all scoped private/probe/environment paths
ignored. Full checks, commands and script hashes are in private `final-checks.json`.

The first final-check helper stops at its line-delimited `check-ignore` set
comparison, after protection/dependency checks pass. A read-only diagnostic
reproduces Windows text-mode CRLF conversion: Git treats the appended carriage
return as part of every name and quotes it. This is a checker serialization bug,
not a changed ignore rule or leaked private file. NUL-delimited input/output
verifies the exact real path set; the final helper uses `-z --stdin`. Initial
failure and passing diagnosis receipts are preserved; no private data, product
logic, ignore rule or model result is changed to repair this check.

### Scope result and remaining gates

**MODEL_ENVIRONMENT_QUALIFIED** means the specified minimal synthetic GPU chain
works on this machine. It does not qualify full official Trainer/real COCO loaders,
FP16/AMP, actual dataset memory, long training stability, model accuracy, owner
discrimination, ONNX/ncnn/mobile export or live assistance. No real Training
Dataset Lock, Model Lock or blind Test GT is created; `training_qualified=false`.
No SQLite/migration/cloud change. Old GT/2A2 locks and 2B-1 results stay unchanged.

Recommended later starting configuration: **YOLOX-Nano / 416 / batch 1 / FP32**,
after data/weight provenance/readiness and training authorization. Optional b2 is
only a synthetic feasibility observation, not automatic training permission.
No Faster R-CNN restoration or extra architecture comparison. All model code and
artifacts stay ignored; current Git HEAD/branch/main unchanged. No commit, push,
merge or formal training. Stop for user/ChatGPT acceptance.

## 2026-10-06 — Scoped private-local two-class Training Dataset Lock

### Superseding authorization and preserved history

The user confirms the recovery report and explicitly authorizes only the existing
Smoke GT Lock v1's eleven accepted Witch/Skeleton boxes for
`private_local_research_poc`: match 01 / TRAIN and match 04 / DEV_VAL.
The preceding ordinary-Minions target-recheck is superseded/historical, not an
active four-match/eight-deployment product gate. Its report, sources and results
remain unchanged; the old validator and original 3–5-class contracts are preserved.

The new authorization records exactly:

```text
source_type = user_recorded_gameplay
intended_use = private_local_research_poc
user_training_authorized = true
external_upload = false
redistribution = false
rights_clearance = unverified
```

`training_qualified=true` means only the Clash Tracker internal private local
research PoC data gate. It is not copyright/trademark/legal clearance, Supercell
permission, rights to redistribute, commercial qualification or permission to
upload footage/crops/annotations. No third-party Clash Royale dataset or weights
are allowed. The present execution stops at data lock creation and validation;
formal training, pretrained-weight download, Phase C and Module 3 remain closed.

### Dedicated readiness and immutable readback

A small ignored local adapter reuses the strict JSON/canonical serializer,
private-path checks and original reviewed GT/media binder, without changing
production source, schemas, tests, dependencies or the legacy CLI. It verifies
the authorized parent GT file SHA, reconstructs the original human conclusions,
checks report/index/PTS/PNG correspondence and hashes actual source recordings.
Only the exact two classes, match splits and objects 01–11 are accepted. Each
class has opponent appearance support in both splits; no historical Minions or
general 3–5-class gate is invoked or weakened.

Actual dedicated readiness and new lock readback exit **0 / 0**. Status:
**TWO_CLASS_TRAINING_DATASET_LOCKED**. A separate exclusive version-one
`two_class_training_dataset_lock` freezes the unchanged parent reference, full GT
snapshot, user authorization, factual provenance, class map, underlying-match
assignment, scoped qualification, readiness and supervision policy. SHA-256
covers all these semantics; repeated or renamed version-one files cannot be
overwritten. The original GT-only lock remains byte-identical with its historical
`training_qualified=false`; the new scoped qualification is not written into it.
Private receipts retain the actual lock path and file/envelope/semantic hashes.

| Split | Underlying match | Frames | Witch boxes | Skeleton boxes |
| --- | --- | ---: | ---: | ---: |
| TRAIN | match 01 | 2 | 2 | 4 |
| DEV_VAL | match 04 | 2 | 2 | 3 |

All **11 accepted boxes / four frames / four appearance groups** are retained.
There are two confirmed Witch deployment groups and zero Skeleton card
deployments. Owner is metadata, not a detector class; forms remain unknown.
Skeletons retain confirmed spawned-from-Witch relationships. Object 12 remains
rejected Unknown, never Negative.

Three frames / ten boxes have complete selected-class supervision. The fourth
frame's Witch positive is retained as
`positive_only_requires_unknown_safe_consumer`: ordinary full-frame loss and
full-frame metrics are forbidden there. A standard consumer must exclude that
frame unless a separately verified Unknown-safe positive/ignore implementation
is provided. Freezing eleven positives does not certify eleven positives for
ordinary full-frame supervision, full-video absence or an FP/min denominator.

### Current verification evidence

Test-first check: one expected failing readiness test before the adapter existed
(39 deselected), followed by **40 passed** dedicated tests after implementation.
Tests cover exact authorization and boolean types, scope expansion, changed GT
even after re-digesting, class/split/bbox/Unknown changes, partial-frame loss,
determinism, duplicate/renamed/corrupt locks and interrupted writes. Bad-input
tests only change test-owned copies; no real evidence is edited.

Actual freeze/readback protection checks confirm **1,462 existing files
unchanged**, including original data/GT/reviews, historical target-recheck,
2A2/2B-1 results, offline source/tests/configuration and explicit Phase B reports
and probe artifacts. This is a scoped inventory, not a claim of hashing every
installed environment file. Fresh offline `pip check` and `git diff --check`
pass. Only six pre-existing tracked documentation files are dirty; source/tests/
configuration remain unchanged. No staging, commit, push or merge.

Fresh combined private adapter and unchanged GT-freeze tests:

```text
# Repository root, existing offline interpreter
python -m pytest -q --tb=short outputs/module2b2b/human-review/assembly/test_two_class_training_lock.py outputs/module2b2b/human-review/assembly/test_two_class_gt_freeze.py
65 passed in 14.66s
```

Fresh full maintained regression (cwd `tools/offline_video`, existing absolute
offline interpreter; JUnit written to a new ignored qualification directory):

```text
python -m pytest -q --tb=short --junitxml=<new-private-qualification-directory>/regression.xml
908 passed, 3 skipped in 1052.47s (0:17:32)
```

Exit 0; all three skips are inherited Windows permission cases, not GUI errors.
An initial command used a nonexistent interpreter relative to the chosen cwd;
it failed before executing tests and was corrected to the existing absolute
interpreter. No environment/test changes or historical-result substitution.
Exact commands and JUnit evidence are retained privately. Final documentation,
privacy, dependency and protection checks use a separate current receipt.

Final receipt exits 0: combined private tests again **65 passed** (10.25s),
`pip check` reports no broken requirements, all 1,462 protected hashes match,
and the new lock file SHA remains unchanged. All **1,422 checked private paths**
are Git-ignored; zero private artifacts are tracked. All **58 local documentation
links** resolve; the additions scan finds zero sensitive-pattern hits. No staged
files or legacy source/test/schema/dependency changes exist.

The first final-check attempt stopped on raw `pip freeze` text comparison:
the older text-mode receipt used LF and the current bytes-mode capture retained
Windows CRLF. Fresh diagnosis showed the same thirteen package lines, versions
and order, with no added/removed package. Only the new ignored checker now
normalizes line endings for this comparison; it still compares every package
line exactly. The initial failure and successful final test output remain in
separate private receipts; no environment, GT or training-lock change was made.

No training, extraction, relabeling, model-environment modification, pretrained
download or new model evaluation occurs in this step. Both actual detection
quality and the real training pipeline remain untested. Stop at the verified
Training Dataset Lock; the next separately authorized task may address Phase C,
not the obsolete Minions expansion or another Phase B installation.
