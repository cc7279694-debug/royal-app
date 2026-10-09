# Module3C4 — Visual Evidence Improvement

Verified scope:2026-10-09; local baseline
`f3cd570ae759f6998a3045971c0c4d475ec9372e`, feature
`codex/module3c4-visual-evidence`. Main remains
`602dd0f0d92f9bcd09b866b7ab081c5352ba5a93`. No push or merge authorized.

## Outcome first

**Bounded experiment completed; visual identity/owner/deployment evidence still
insufficient for production replacement.** Do not claim Royal Hogs was repaired.

| Measure | Frozen3C1 / production3B |3C4 parallel trial |
| --- | ---: | ---: |
| Five confirmed windows hit |2/5|4/5|
| Royal Hogs matched |yes|no|
| Royal Hogs duplicates |1|0, because no Hog event|
| Emitted outputs |14|10|
| Unscored outputs |12|6|
| Five-class algorithm tracks |61|ByteTrack66; unchanged3B projected59|
| Five-class singleton tracks |13|ByteTrack35; projected3B10|
| Raw observation denominator |792|792|
| ByteTrack assignment coverage |not applicable|678/792 (85.61%)|

Royal Hogs abstention is **not** successful grouping or identification. All three
original continuity windows remain zero new events, but the fourth-match Witch
window still lacks corresponding detections; it cannot validate physical continuity.
The unchanged scorer exits3 (`passed=false`), not PASS. Six unscored outputs remain
inspectable, not negatives/false positives. No full-match FP/min is computable.

### Owner / timing interpretation

On the same owner-agnostic ByteTrack hypothesis links, raw known-owner flips52
become0. Known-known coverage falls from612/612 to424/612 (69.28%); unknown
observations rise from0 to335/792 (42.30%). This is a stability/abstention tradeoff,
not verified owner accuracy. The raw model supplies binary owner channels but no
owner probability/logit; detection confidence never becomes owner confidence.

Projected first-eligible events are Witch32.75s, Flying Machine78.25s, Golden
Knight103.25s and Minions117.5s. Raw timestamps/PTS/bboxes are unchanged; three-frame
owner eligibility and track fragmentation delay usable evidence. Newly scored
hits do not establish more accurate physical deployment onset. No artificial
timestamp translation, confirmation-for-first-seen substitution or scoring change.

At the Royal75–81.5s inspection window,34 predictions yield11 assigned algorithm
IDs,9 unassigned rows and32/34 unknown owners. A tentative two-track cohort is
recorded, but four stable physical member identities are not established. No
Royal output survives unchanged3B eligibility. Whole-match Royal raw59 sightings
produce18 ByteTrack tracks/11 singletons versus12/1 in the original engine;
assignment is39/59. The selected tracker defaults do not solve this low-cadence,
small-object, conflicting-owner evidence problem. No result-driven retuning.

Track starts/singletons are mechanical proxies with fixed denominator and explicit
unassigned coverage; no physical track GT exists, so true fragmentation/ID-switch
accuracy is unknown. Metric `initial_visible_track_count`/`final_visible_track_count`
refer to each class's observed detection-stream edges, **not** recording censoring
or real deployment birth/death.

## Single mature tracker / provenance

Official [ByteTrack](https://github.com/FoundationVision/ByteTrack) was audited and
pinned to `d1bf0191adff59bc8fcfeaa0b33d3d1642552a99`; root MIT copyright2021 Yifu
Zhang is preserved with source hashes. BoT-SORT was not run because image GMC/ReID
adds complexity without an approved new appearance model; DeepSORT was not run
because its default person descriptor is mismatched and GPL3. Existing KataCR
Ultralytics tracker files are AGPL3 and may auto-install LAP; they are not copied
or imported as this tracker.

ByteTrack's four-file core is privately staged, not redistributed in Git. The
root MIT notice does not independently resolve shared Kalman source history,
game assets or model rights; no commercial clearance is asserted. Adaptations:
relative imports/unused framework removal, NumPy dtype compatibility, independent
pixel-inclusive IoU, precise observation-ID provenance and a synthetic-proven
terminal-removal fix. Original LAP cost-limit matching is used, not a homemade
Hungarian/post-filter substitution. Adaptation/source/license SHA records are local.

New isolated tracking environment: Python3.12.4, NumPy1.26.4, SciPy1.13.1,
[LAP0.5.13](https://pypi.org/project/lap/0.5.13/) (BSD2), pytest8.3.5. Official
Sources and licenses were audited before installation; actual PyPI binary wheel
URLs/hashes and installed license metadata were recorded after installation.
No Torch/YOLOX/Ultralytics/new model package is installed in
that environment; existing detector and offline environments remain unchanged.

Frozen settings:4FPS contiguous explicit frames, high>.5, low(.1,.5), new birth
>=.6, match=.8, buffer2s, upstream score fusion. Owner-agnostic per-match/class
association; missing/ambiguous identity remains uncertainty. Kalman predictions
never synthesize observations, human identities, absence evidence or GT.

## Separation and bounded repair

Public additions are `tools/visual_evidence` runtime/CLI/metrics/policy/tests/docs
and affected repository-memory documents only. All old non-document sources,
formal3B engine/adapter/rules/scorer, App, GT locks and old results remain unchanged.
No SQLite/migration/schema/model training/Android build or live-game integration.

MOT IDs and candidate cohorts stay sidecar-only. Formal3B accepts trusted human
appearance identity; this experiment never fakes that source. Thus formal3B sees
only owner/source projection and still computes its own tracks/episodes. A future
identity-consuming contract would need separate authority and evidence; none is
silently enabled. Region/trajectory/reacquisition are context flags, never current
half-of-map ownership guesses. Unknown/form/origin are not manufactured.

Diagnostic groups tentatively associate late members, leave ambiguity unresolved,
and permit observationally separate new cohorts. They do not emit card events.
No long cooldown, GT duplicate label, expected-count-as-birth or capacity-as-confirmation.
Synthetic tests cover staged discovery, movement, short gaps, simultaneous distinct
units, class/match isolation, independent second groups and ambiguous overlaps.

An internal read-only code review (not ChatGPT acceptance) found a deterministic
diagnostic-only group earliest-member/span bug using generic synthetic inputs.
After RED2/25, repair keeps immutable anchor identity/time/bbox, records member
births and enforces total span<=2.5s. v1 freeze and sole actual replay/score remain
intact. Cached-sidecar v2 reconciliation proves **all owner evidence and all
projected rows identical**; no detector/tracker/engine/scorer rerun or parameter
change. Both histories survive.

Freeze SHA256:

- v1:`633ce204311f22761c201fcb7bcd051f3a1e3ea5d41ff40c1fe759a1141c6678`
- v2:`b27a471eb93abd6ad13d095db0191140bf75e02de9f52c0b3532a5a22fd2fa19`

Generation reads only raw frozen predictions/frame metadata/source hashes and
imports no GT/scorer. Separate evaluation consumes the original GT only after
exclusive output manifests are sealed. Hash-bound source byte execution and input
rechecks avoid executing an unaudited tracker or silently changing retained data.

## Retained diagnostic clip / speed

Before new inference, freeze the **earliest20s** of third recording (80 samples).
Selection is chronology-based, not card/score-based. This match had prior general
review/preannotation exposure, but not3C event-window tuning; it is not blind.
Actual inspected15s image is matchmaking UI. The prefix has301 proposals, zero
five-rule-class observations and zero baseline/experimental events. It is
**insufficient to assess target tracking or overfitting**. Do not move the window
after seeing that result; missing classes/non-detection do not become Negative.
This exposes the need for an explicit battlefield-scene validity boundary.

Tracking on the1523 frozen samples takes174.61s (114.65ms/sample), CPU NumPy/SciPy/
LAP only; owner policy9.41s; unchanged engine172.55s. These are offline measured
component timings, not full online latency or real-time readiness. Existing model
benchmark mean369.37ms/frame is historical; it was not rerun over the main input.
The extra80-frame clip used actual GTX1050Ti CUDA, peak allocation580731392 bytes,
mean677.91ms/median360.85ms including warm-up; inference wall63.80s, process314.69s
including import/startup. Weights are unchanged, no training/dataset/GT imported.
Three process-local network attempts were denied. Not an OS sandbox guarantee.

## Fresh verification / protection

- New tracker/policy/metrics/CLI suite:75 passed, no skipped runtime tests in the
  isolated tracking environment; initial RED evidence is retained.
- Historical related/smoke contracts:570 passed/1 existing Windows symlink skip.
- Complete offline-video regression:908 passed/3 existing Windows symlink
  permission skips in1569.97s; fresh exit0. The interrupted/historical runs do
  not substitute for this result.
- Combined executed suites:1553 passed/4 existing Windows permission skips;
  no unresolved assertion failure. Tracker runtime tests are not counted as skips.
- Offline, original detector and new tracker `pip check`:exit0 each.
- All2580 protected existing material files and156 existing non-document source
  files are hash-unchanged.7546 local private files checked:all Git ignored,
  none tracked. `git diff --check`:exit0. Public scope is16 files:four existing
  memory documents and twelve new research source/test/document files.
- JS/App/Gradle/AVD tests:Not Run; no App or Android modifications in this module.

Actual commands and output receipts are retained locally under
`outputs/module3c4/verification/`:

```text
# Isolated tracker environment, repository root
python -B -m pytest tools/visual_evidence/tests -q --import-mode=importlib --tb=short -rs
# Existing offline environment, repository root
python -B -m pytest tools/detector_events/tests tools/event_engine/tests tools/deployment_review/tests tools/preannotation/tests tools/recorded_replay/tests tools/deployment_shadow/tests tools/smoke_training/tests tools/smoke_training_attempt02/tests -q --import-mode=importlib --tb=short -rs
# Existing offline environment, tools/offline_video working directory
python -B -m pytest -q --tb=short -rs
# Each of the three respective environments
python -B -m pip check
git diff --check
```

Log SHA256, command, environment/cwd, actual exit code and elapsed time are
recorded with each receipt; junit XML retains individual test/skip results.

Ignored local artifacts: `outputs/module3c4/` contains sealed replay/evaluation,
raw tracking/owner/cohort sidecars, v1/v2 reconciliation, timeline, component
timings, source/licenses/environment receipts and reused-source visual sheets.
The latest compact visual ZIP is local/private; no media/weights/labels enter Git.

## Recommendation — do not add another same-GT rules loop

Do not promote this strategy or keep tuning it on the same five windows. First
resolve visual input support: battlefield-validity detection, detector confidence
and class/owner reliability, and contiguous small-object identity evidence.

Minimal next **diagnostic**, not training requirement:10–20 consecutive Royal
arrival/movement/occlusion frames with per-member identity and owner review, plus
one separate complete natural match's short battlefield clip fixed before model
output. This would distinguish missed boxes, bad owner/class and association error
without calling one existing group a generalization test. Require a genuinely
separate second deployment in synthetic and separately reviewed video evidence.

If retraining is then needed, begin a small primary-entity detector dataset from
at least two development matches with representative Royal Hogs, Minions and
selected direct entities, per-object owner facts and exhaustive selected-class
coverage; reserve another whole match.20–40 representative development frames is
only a feasibility starting budget, not a proven sufficiency/training gate or
automatic permission. Use the already qualified YOLOX-Nano local route rather
than stacking unverified event heuristics; model replacement/training/source
clearance requires a new scoped authorization. No additional model is tried here.
