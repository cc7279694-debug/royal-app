# Module 3B — Oracle implementation and fixed replay verification

## 2026-10-08 — Grouped Event Dedupe Repair

Baseline `60494187aff7e3afc578c477212d963265460a46`, existing3B feature branch.
Latest user explicitly authorizes the minimal repair. No new architecture plan,
detector, App change, training, extraction/GT edits, main merge or push.

Root cause: fixed displacement from the previous bbox fragmented moving Minions
between sparse samples. New grouped-only geometry motion policy is
max(existing bbox budget,90px/s*actual gap), retaining7.5s gap ceiling. No card
cooldown. Explicit GroupedCardEpisode owns member IDs, emitted ID and deterministic
active/occluded/closed tracking state. Existing members cannot emit another play;
coexisting genuinely new unassigned tracks can form a separate episode even
immediately. Trusted human identity can attach newly visible same-group members.

TDD: first synthetic run7failed/3passed, catching repeated long-movement events
and old episodes swallowing genuine new groups. One lifecycle test wrongly
assumed hash-ID output order; corrected to assert first_seen/state mapping.
Additional human-group membership growth regression failed as expected, then
fixed. Final event engine suite84 tests, combined annotation/event contracts
262passed/1 Windows symlink permission skip. Long movement, sampling gaps, new
coexisting groups, expiry/reappearance, both cards, ownership/spawn/observe-only,
human identity, deterministic replay and existing scoring guards are covered.

Frozen original94-observation stream reused byte-for-byte; no adapter rerun or
new frames. Repair replay-v1 followed the first synthetic fix; replay-v2 followed
the additional synthetic human identity repair. Both configs/registries/sources
are identical and both pass; outputs are preserved independently, not replaced.
Code hash/config/source SHA recorded before each run. No result-driven tuning.
Event GT remains `abd434cb5a8aba399295a87e0ad49a2997cf2304c2afff4792e16d991d8e03cb`.

Final replay/evaluation exits0/0:5/5 positives exactly once,0 positive duplicates,
dedupe04/09/12 counts0/0/0. Five matched event IDs, timestamps, confirmation times
and rule semantics are unchanged. Only Minions source_observation_ids expands to
include its continuation. A supplementary checker initially required unchanged
entire event objects; it was corrected to permit this intended evidence growth
while enforcing unchanged identity/timing/semantics and retaining all old source
IDs. No replay/GT was edited to satisfy it.

Nine events total,3 grouped episodes;4 unresolved outputs remain unscored. No
Negative/FP is invented. Witch confirmation delay remains3s: retrospective
timestamp hit is not validated<=2.5s online confirmation. No cross-match or
detector performance/full-match FP claim. Fixed90px/s is not a proven physics
calibration and can remain ambiguous in crowds.

Fresh offline regression908passed/3skipped (927.13s), combined contracts262passed/
1skip, smoke contracts200passed: total1370 Python passes/4 Windows permission
skips. App51passed + Node review UI8passed =59 JavaScript passes;
App TypeScript/build and pip check exit0. Bounded protection checks1884 original
files, all hashes unchanged; private files ignored, no tracked private artifact,
main unchanged. Diff/credential checks pass;103 relative links checked,0 broken.
Full logs and receipts are in the repair completion report. All old artifacts,
including the original FAIL, remain
unchanged. Private receipts/replay/evaluation: `outputs/module3b-repair/`.
Current status: `MODULE_3B_ORACLE_ENGINE_REPAIR_PASS` for the fixed Oracle gate;
stop for independent acceptance, not detector mode or Module4.

## Preserved original implementation verification — 2026-10-07

Date:2026-10-07. Baseline `d4c5b94625dda49dfb1af2c1b5c8d4851751650a`;
branch `codex/module3b-oracle-event-engine`, same local checkout. The latest user
attachment explicitly authorizes3B only. No main merge/push or detector mode.

## Outcome: valid Oracle run, gate FAIL

`MODULE_3B_ORACLE_ENGINE_FAIL`. Five confirmed GT events each match once, but
candidate09 Minions continuity incorrectly produces a new event at127s. Dedupe
04/09/12 has new-event counts0/1/0, so the required three-window gate is not met.
This is not a usable automatic card tracker or an accepted Module3B PASS.

| Card | approximate Event GT(s) | first supported appearance(s) | confirmed_at(s) |
| --- | ---: | ---: | ---: |
| Witch |31.5|32|34.5|
| Royal Hogs |75.5|77|77|
| Flying Machine |78|79.5|79.5|
| Golden Knight |102.5|104.5|104.5|
| Minions |116|117|117|

All first appearances are in the fixed [GT,GT+2.5s] window. Witch confirmation
actually occurs3s after its GT; this is retrospective Oracle evidence, **not**
validated <=2.5s real-time confirmation. Only the first supported appearance is
the event timestamp; it is not a fabricated exact deployment onset.

There are11 total emitted events: five positive matches, one explicit dedupe
failure, five unscored outputs. Four unscored outputs overlap the four unresolved
review windows; the extra19.5s Minions output is unreviewed, not automatically FP
or Negative. No full-match false-positive rate or cross-match/detector accuracy.

## Implemented boundary

`tools/event_engine/engine.py`: pure deterministic observation validation,
one-to-one geometry/human-continuity tracking, fixed versioned five-card registry,
strong/medium/weak candidates and STRONG events. Identity dedupe overrides gap;
grouped strong evidence requires coexisting distinct tracks, not accumulated
single-unit fragments. Own/unknown/spawned/secondary and unmapped observations
cannot emit. Geometry remains deliberately simple, no ReID.

`oracle.py`: source-SHA-bound read-only accepted Human visual metadata/PTS,
human final owner/form/origin, never raw teacher confidence. Unresolved identity
tokens omitted, not forged into unit identities. `evaluation.py` alone grades
against Event GT after replay. `cli.py` separates both commands and emits hashed,
exclusive artifacts. No video extraction, detector, training, new annotation,
database/migration or dependency. No Module1/2A1/2A2 tool semantics changed.

`app/src/demo/recorded-event-source.ts` plus a narrow tracker boundary extension
accepts offline Oracle JSON with confidence=null. The real11-event output was
read back by that adapter. No UI wiring, mock control changes, APK rebuild, phone
test, 8-card rules, cycle/evolution/elixir, capture, cross-App HUD or game access.

## Immutable source and run bindings

Event GT byteSHA (fresh load_lock validation exit0):
`abd434cb5a8aba399295a87e0ad49a2997cf2304c2afff4792e16d991d8e03cb`.
All five confirmed events are natural_match_01; match04 has only an unresolved
onset/continuity check. The underlying match/recording distinction is preserved.

Multiclass batch1 lockSHA:
`7d4a9a7fafd627f1fbf82f73db3d66232163e5aac14dbdc8f5996c2c0b3a9dae`;
batch2 lockSHA:
`4a2bf638855d18b6d00ddc35738c3b4f2cdc5a460837364989e552d169d986f8`.
Input is all83 accepted boxes/all48 sampled frames. Empty reviewed frames are
Unknown, never absence/Negative. Source selection is not based on event windows.

Separately declared legacy visual-regression lockSHA:
`f48b401136e3285700d5000d73fed4c6381131cfabcbf956c2f3ee96804d97f1`.
All11 existing confirmed Witch/Skeleton objects/all4 frames are included, not
only a GT-selected match04 window. Only visual continuity is imported; historical
independent-deployment/counting assertions are not input. This legacy lock's old
reviewer wording is preserved, not used to rename ChatGPT a human reviewer in any
new artifact. Total94 observations/52 source frames, same existing recordings.

Fixed config and source/codeSHA were written before replay under ignored
`outputs/module3b/run-contract.v1.json`. The first replay is preserved in
`oracle-replay-v1/`. Its first grading call exited2 because the old lock loader
requires an absolute path; no evaluation output was created. The new CLI now
normalizes the path; a regression was observed failing then passing. No old
loader or evidence was relaxed. Original error log remains.

An independent read-only code reviewer found three synthetic Important defects:
shared human identity could emit twice; a split singleton could appear as two
units; overlapping GT windows could double-count a legally matched event. All
were reproduced RED and fixed GREEN. Scoped review confirmed all addressed.
The fixed version is `oracle-replay-v2/` and `oracle-evaluation-v2/`.
Registry/config/sourceSHA are identical v1→v2; only synthetic logic repairs were
applied. Both versions retain5/5 hits and candidate09's real FAIL. No association
threshold, gap, group distance/window or GT was tuned after seeing results.

Final replay manifestSHA:
`2b88548b0d35bb3149da20a83243462226f6ea7149bffa944973a0d9eb087524`.
Final prediction/evaluation JSON, timeline and source manifests remain private,
local and ignored. New files cannot replace the old locks or output versions.

## Fresh checks

Full owned suites are run with their existing per-project import modes; root
collection of ignored upstream model archives is not a meaningful regression.

| Actual check | Result |
| --- | --- |
| `.venv python -B -m pytest`, cwd tools/offline_video, JUnit log |908passed/3skipped, exit0,1301.51s|
| Python deployment_review + preannotation + event_engine, importlib mode |248passed/1skipped, exit0; includes70 new Oracle tests|
| Python smoke_training + smoke_training_attempt02, importlib mode |200passed, exit0|
| Node preannotation reviewer/review-ui tests |8passed, exit0|
| App Vitest |51passed, exit0, final rerun|
| App `npm.cmd run build` (includes TypeScript) |exit0|
| `.venv python -B -m pip check` |exit0, no broken requirements|
| actual recorded-App JSON readback |11events accepted; confidence=null; no UI wiring|
| real Oracle CLI replay/evaluate |0/3, FAIL correctly reported|
| diff / links / credential-pattern check |exit0;100 relative links,0 broken;0 credential-pattern matches|
| bounded privacy / source protection |1814 existing file hashes unchanged;1879 private paths ignored;0 tracked private files; main unchanged|

Fresh maintained Python total:1356passed/4skipped. Fresh JavaScript total:59passed
(51 App +8 annotation-tool tests). Existing Windows permission skips are reported,
not counted as passes. No Android build/phone test, detector inference, training,
or full ignored upstream SDK/model-environment test collection was run.

Actual commands and full outputs/JUnit receipts are retained under ignored
`outputs/module3b/checks/`. Combined contract command:
`.venv\\Scripts\\python.exe -B -m pytest tools/deployment_review/tests tools/preannotation/tests tools/event_engine/tests -q --import-mode=importlib --tb=short`.
The full offline suite used the same interpreter from `tools/offline_video`;
smoke contract suites used importlib mode. App checks were `npm.cmd test -- --run`
and `npm.cmd run build`; annotation UI checks used Node's built-in test runner.

Protection captures all1814 pre-existing material files, including the original
recordings, locks, reviewed visual evidence, Attempt01/02, benchmark and Module3A
artifacts. Their hashes and Module3A directory membership are unchanged. Privacy
enumeration is explicitly bounded to those files, current Module3B outputs and
local_data; it does not claim a scan of every SDK/model-environment dependency.
An initial unnecessarily broad output-tree scan was stopped, then this bounded
material audit completed. No old files or environments were changed or deleted.
Receipt `protection-after-1.json` checked1879 private paths; later receipts may
include additional new verification files. All scoped private paths remain
ignored. Source config/registry bindings are unchanged across the two replay
versions. Local Git checkpoint only; no push/main merge. The exact checkpoint
SHA and post-commit status are recorded in the private completion report.

New Oracle tests observed33 missing-behavior fixture errors, adapter/scorer22
failures, CLI7 failures and corrected App adapter8 failures before implementations.
Initial App type-check exposed nullable-confidence narrowing/unsafe test index;
those were fixed without any/type suppressions, then typecheck/build passed.
Review/CLI fix wave RED6fail→GREEN70pass. Tests cover the requested identity,
occlusion, grouped-unit, owner/spawn/observe-only, deterministic-ID/replay,
five-positive/three-dedupe synthetic grading and unknown-unscored contracts.

The initial offline regression launch failed before execution because its output
directory had not yet been created; the successful full command above was then
run. First review-package rendering hit Windows GBK decoding; only its private
logging helper changed to UTF-8. Both issues are retained in actual tool logs,
not called code/assertion failures or grounds to modify old data.

## Known limitations and stopping point

Sparse2.5s visual observations with unresolved individual identities can break
geometry continuity; the127s real dedupe failure remains unresolved. No parameter
search, new visual annotations, regenerated videos or forced event merging using
Event GT answers. Wait for ChatGPT/user review of this valid FAIL before further
repair or detector mode. The engine is implemented/testable, but the full Oracle
acceptance gate has **not** passed. No Module4 or real-game capability is enabled.
