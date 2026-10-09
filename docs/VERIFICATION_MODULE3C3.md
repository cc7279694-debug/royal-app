# Module 3C-3 — Deployment Evidence & Spawn Group Prototype

Verified:2026-10-09. Authorized baseline
`bbcd0917493e8d04aa8a61bc74d3da4d2941b376`; branch
`codex/module3c3-deployment-spawn-shadow`. Main remains
`602dd0f0d92f9bcd09b866b7ab081c5352ba5a93`.
The user formally ended3C-2 diagnosis; automatic3C recognition remains unaccepted.

## Outcome first

**Prototype implemented; sole scored same-input experiment is insufficient.**
Do not replace the accepted3B engine or describe duplicate reduction as a repair.

| Measure | Original detector baseline | Independent Shadow |
| --- | ---: | ---: |
| Frozen confirmed windows hit |2/5|0/5|
| Royal Hogs duplicate |1|0|
| Original emitted events / provisional subset |14|2|
| Actual experimental Spawn Groups |Not applicable|0|

Of14 original events,12 are UNRESOLVED due to overlapping identity/owner conflicts.
This includes both Royal Hogs events and the previously matched Minions event.
The other two remain PROVISIONAL Flying Machine outputs at77.75 and162.5s.
All2339 baseline candidates are preserved;2337 become UNRESOLVED. No physical
deployment is confirmed by the Shadow layer. Unresolved is not Negative.

No real Royal group was created: both events abstain before association. Thus
duplicate0 reflects withholding both, not proving they were successfully merged.
Synthetic group success cannot substitute for this missing real-data validation.
The algorithm's conservative conflict rule is demonstrably too abstention-heavy
for this noisy detector stream. No post-score weakening or other tuning was done.

## Scope and implementation

New subsystem only: `tools/deployment_shadow/prototype.py`, `cli.py`,
`__main__.py`, `README.md` and two test modules. Status/decision/verification/
checkpoint documents are updated. No pre-existing production source/test/config
changes, new dependencies, SQLite/schema/migration, App or Android edits.

The prototype consumes frozen model observations and explicit sampled-frame
coverage, reuses the unchanged production replay, and retains that complete
baseline separately. It rejects human/GT identity and unsupported answer fields.
There is no GT argument, GT I/O or scorer in generation. Event IDs, source IDs,
first-seen, confirmation and baseline episodes are retained without shifting.

Time fields distinguish `first_seen_timestamp`, `confirmation_timestamp` and
`estimated_deployment_timestamp`. Algorithmic estimates are null; source-video
analyst notes remain separate and are never injected into generation. The score
still uses original first-seen, not confirmation or a visually inferred onset.

### Frozen observational group policy

Inherited parameters stay2.5s birth window,120px grouping distance,90px/s motion
budget and7.5s track gap. No extended card cooldown or capacity-fill rule.
First baseline-qualified groups/direct events are PROVISIONAL, not card-play truth.
A later nearby group can be a possible late member, but remains UNRESOLVED;
other overlap stays ambiguous even after the birth window. Every abstained event
survives with original IDs/source observations and an inspectable reason.

A second provisional group requires existing distinct-unit qualification plus
observational separation from every earlier group: all birth centers beyond all
recent old-member motion budgets, or two explicit recent sampled frames with no
same-class sightings after old-member last-seen. Both require the frozen gap
limits. Track expiry alone cannot prove a new deployment. Sampled non-detection
is expressly not physical absence, a Negative label or exact onset evidence.

Overlapping conflicting own/unknown/form/origin sightings within the inherited
birth window make a candidate UNRESOLVED. This runs retrospectively over all its
source observations: later owner conflict can withhold an earlier event. It is
not an online-causal implementation, calibrated owner classifier or proven
physical-unit identity. Distant own sightings alone do not conflict.

Only actually created provisional cohorts constrain subsequent associations;
guarded/abstained sightings are not a certified earlier deployment. This remains
an experimental limitation, not a reason to silently promote uncertain events.

## Four actual source-video evidence windows

Root and the evidence subtask inspected actual pixels, including four context
sheets and four corrected adjacent-PTS sheets; no generated images or model rerun.
The subtask also inspected interval-boundary originals. These are assistant visual
analyses, **not new user-attested Human GT or independent ChatGPT acceptance**.

78 original frozen4FPS sample frames and40 adjacent source display frames were
extracted only in four bounded windows.432×960 source, time_base1/90000, origin0;
adjacent spacing3750PTS,24FPS. Model boxes/IDs come unchanged from frozen rows.
All eight extraction inputs are byte-identical before/after. No full-video rescan.

| Case | Frozen first-seen / confirmation | Estimated visible deployment-cue interval | Pixel evidence |
| --- | --- | --- | --- |
| Witch |30.5/30.75| (29.083333,29.125] | Clock/red level then gold arrival behind upper king tower, subsequently recognizable purple-hood/staff Witch;30.5 box contains target. |
| Flying Machine |77.75/78| (76.958333,77] | Separate clock/red level near right bridge then rotor/barrel arrival;77.75 box and78s support target. |
| Golden Knight |102.25/102.75| (101.958333,102] | Clock/shadow and gold sword-bearing descending figure;102.25 box supported by subsequent recognizable landing. |
| Royal Hogs |75.75/76; second76.75/77.25| (75.416667,75.458333] | One staggered arrival with four red-level silhouettes by75.75, then four Hogs at bridge; no separate Hog arrival with second episode. |

Intervals bound the last frame without a local cue and the first with it. They
are not exact player-release/server-spawn times; those scalar times stay unknown.
They do not revise approximate GT31.5/78/102.5/75.5 or the one-sided `[0,2.5]`
scoring window. All three early events still miss. These findings explain why a
score miss is not proof the visual target was absent or misclassified.

Royal pixels support late discovery of already visible members; exact individual
identity through overlap is still uncertain. Some own-labeled model boxes enclose
red-level opponent arrival, supporting local model owner errors, not adapter
channel inversion. The separate arrival at77s is Flying Machine. These cues are
missing from the current observation contract; notes do not automatically fix it.

Use `visual-evidence/compact/<case>-context/contact-sheet.png` and corrected
`compact/<case>/contact-sheet-raw.png` under the ignored3C-3 outputs. Adjacent
sheets intentionally omit model boxes; their initial misleading absence caption
is superseded with a preserved caption-correction receipt. No absence inference.

## Royal Hogs episode association comparison

| Original event/episode | Track births | Shadow disposition |
| --- | --- | --- |
|`event-4c8512a30989a44bdf85cb98` / `appearance-4d5ef3b3562196f58ab393f0`|75.75,76|UNRESOLVED,10 conflict observations, group=null|
|`event-470cbb33af8aaba57965eddc` / `appearance-e6e07d6f3d0d1acbf452c113`|76.75,77.25|UNRESOLVED,2 conflict observations, group=null|

Original track sets are respectively
`track-4d5ef3b3562196f58ab393f0`/`track-9159888df5530711555faa61` and
`track-e6e07d6f3d0d1acbf452c113`/`track-31b2f9413fbd6a1e5a58d201`.
Local `royal-cohort-comparison.json` retains full tracks, observations, IDs and
reasons. Its relation arrays are empty; actual association was not exercised.
Source pixels suggesting one arrival are not read by the algorithm or used to
force these episodes to merge. All14 baseline events remain in the local timeline.

## One scored run; unscored IO abort preserved

The first frozen invocation returned2 before algorithm/scoring: its49,052,296-byte
detector stream exceeded the reused16MB Oracle JSON loader. No Shadow/evaluation
artifact existed. The abort log and first policy/code/input freeze are retained.

A regression test reproduces rejection with a valid sealed stream above16MB.
The new CLI only gains a bounded64MB detector-stream parser using the existing
strict JSON parser; malformed and oversized data remain rejected. Production
Oracle/parser/extractor are unchanged. Policy and prototype hashes are identical
across freezes. A second pre-run freeze binds the IO-compatible source/tests.

The sole subsequent scored run exits0 for sealed replay and3 for valid FAIL
evaluation. All sealed original inputs and GT SHA remain unchanged; baseline
replay is identical to3C-1. GT bytes were hashed before running for protection;
GT answer rows are parsed only by the separate evaluator after output sealing.
This is one scored experiment, not two scored attempts or score-driven retry.
Earlier TDD/debug/synthetic calls are retained and are not performance experiments.

Runtime for the private replay plus separate scoring is63.844s. This is not model
inference timing or realtime latency. No inference was rerun; historical3.2FPS
remains the old benchmark, not a fresh performance claim.

## Fresh tests and dependencies

Actual exit0 logs/JUnit/commands remain in `outputs/module3c3/verification/`.
No historical1370/1439 result is substituted for these fresh checks.

| Check | Actual result |
| --- | --- |
| Detector/event/review/preannotation/recorded/Shadow contracts |370 passed,1 existing Windows permission skip|
| Offline-video complete suite |908 passed,3 existing Windows permission skips|
| Both historical smoke-training contract suites, no training |200 passed|
| Total |1478 passed,4 skipped|
| Existing offline environment pip check |Exit0, no broken requirements|
| Isolated KataCR environment pip check |Exit0, no broken requirements|

New tests:33 core cases and6 CLI cases,39 total. Core tests cover staged2→4
members yielding one provisional event with preserved uncertain later candidate;
movement/sparse sampling; old members alive with far new group yielding two;
fresh sampled groups after disappearance; expiry alone/close ambiguous groups;
Royal Hogs, owner flicker, unknown/spawned/evolved/observe-only guards;
determinism, no identity/answer injection, same-timestamp cohorts and distinct
time fields. Historical Minions contracts also pass in the unchanged event-engine
suite; new Shadow group fixtures use Royal Hogs. These are synthetic, not
cross-match accuracy evidence.

CLI tests cover no-GT sealed output, changed-input rejection, exclusive output,
safe path-free errors, a valid stream above16MB and rejection above64MB. Missing
entrypoint/assertion and synthetic cohort edge failures were observed before
implementation fixes; final tests pass. The large-stream regression's RED was
observed in the tool output, not stored as a separate raw RED log.

Commands (the receipts include actual absolute execution paths):

```powershell
.\.venv\Scripts\python.exe -B -m pytest tools/detector_events/tests tools/event_engine/tests tools/deployment_review/tests tools/preannotation/tests tools/recorded_replay/tests tools/deployment_shadow/tests -q --import-mode=importlib --tb=short -rs
# From tools/offline_video:
..\..\.venv\Scripts\python.exe -B -m pytest -q --tb=short -rs
# From the repository root:
.\.venv\Scripts\python.exe -B -m pytest tools/smoke_training/tests tools/smoke_training_attempt02/tests -q --import-mode=importlib --tb=short -rs
.\.venv\Scripts\python.exe -B -m pip check
```

Skips are the existing symlink-creation privilege checks in evidence_prepare,
multiclass_dataset, training_dataset and deployment_review/event_gt. No new skip.
JS/App tests, Android build/emulator/phone: **Not Run**, unchanged and outside scope.
New detector inference, training and environment installation: **Not Run**, prohibited.

## Privacy, protection and local handoff

Original GT SHA remains
`abd434cb5a8aba399295a87e0ad49a2997cf2304c2afff4792e16d991d8e03cb`.
Original detector stream SHA remains
`dee7e9101acdbd4664c18d4e1a56c47714757b288437019c7a640011ebba748b`.
Old locks, historical FAIL/provenance/weights/APK and private inputs are preserved.
New pixels/JSON/timelines/logs/helpers stay local/ignored; no weights or footage
are added to Git. No cloud, data/schema change or new Model/GT lock.

Fresh protection passes:2381 existing private material files and151 existing
non-document tracked sources are byte-identical. At that checkpoint2574 private
files were checked, all ignored, none tracked; worktree diff check exits0.
The final public-diff receipt also verifies manifest/code/input hashes and links;
no generated private receipt is committed. Private
handoff entry is `outputs/module3c3/REVIEW_INDEX.md`, containing the four context
and four onset sheets, timelines, Royal association comparison, sole evaluation,
abort/freeze/run logs and fresh test evidence. The failed Shadow outcome is kept.

Recommendation: **do not formally replace3B with this prototype**. Improve
reliable class/owner/physical-identity and deployment-arrival evidence before a
separately authorized experiment. No silent forced grouping or same-GT tuning.
This is not full-match FP/min, cross-match validation, independent ChatGPT
acceptance or a live-game/App capability. Local commit only; no push/main merge,
training, Module4/cycle/elixir/Android or next-stage work.
